"""
Command-line interface for Yine corpus conditioning and rule engine utilities.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
import yaml

from yine_rules.settings import Settings
from yine_rules.utils.logging import setup_logging
from yine_rules.preprocessing.conditioning_pipeline import run_conditioning

# NEW imports for new commands
from yine_rules.datasets.freeze_positive import freeze_positive, FreezeConfig
from yine_rules.datasets.splits import make_splits, SplitConfig
from yine_rules.negatives.engine import generate_negatives, NegativesConfig
from yine_rules.negatives.load_generators import load_generators_from_rules_yaml

log = logging.getLogger("yine_rules")


def build_parser() -> argparse.ArgumentParser:
    """
    Construye el parser de argumentos para la CLI.
    """
    parser = argparse.ArgumentParser(
        prog="yine-rules",
        description="Yine corpus conditioning + rule engine utilities"
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # ---------------------------
    # condition subcommand (KEEP)
    # ---------------------------
    condition_parser = subparsers.add_parser("condition", help="Run corpus conditioning pipeline")
    condition_parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to main config yaml"
    )
    condition_parser.add_argument(
        "--logging-config",
        type=str,
        default="configs/logging.yaml",
        help="Path to logging yaml"
    )

    # ---------------------------
    # freeze-positive
    # ---------------------------
    freeze_parser = subparsers.add_parser(
        "freeze-positive",
        help="Freeze positive dataset v1 with stable ids + manifest"
    )
    freeze_parser.add_argument(
        "--exp-config",
        type=str,
        default="configs/experiments/dataset_v1.yaml",
        help="Path to experiment dataset v1 yaml"
    )
    freeze_parser.add_argument(
        "--logging-config",
        type=str,
        default="configs/logging.yaml",
        help="Path to logging yaml"
    )

    # ---------------------------
    # make-splits
    # ---------------------------
    split_parser = subparsers.add_parser(
        "make-splits",
        help="Create reproducible splits (80/10/10) over pair_id")
    split_parser.add_argument(
        "--positive",
        type=str,
        default="data/processed/positive/positive_corpus.v1.parquet",
        help="Path to positive parquet"
    )
    split_parser.add_argument(
        "--out",
        type=str,
        default="data/processed/splits/split_v1.json",
        help="Path to output split JSON"
    )
    split_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed"
    )
    split_parser.add_argument(
        "--logging-config",
        type=str,
        default="configs/logging.yaml",
        help="Path to logging yaml"
    )

    # ---------------------------
    # gen-negatives
    # ---------------------------
    neg_parser = subparsers.add_parser(
        "gen-negatives",
        help="Generate negative samples (rules plugged in registry)"
    )
    neg_parser.add_argument(
        "--exp-config",
        type=str,
        default="configs/experiments/negatives_v1.yaml",
        help="Path to negatives experiment yaml"
    )
    neg_parser.add_argument(
        "--logging-config",
        type=str,
        default="configs/logging.yaml",
        help="Path to logging yaml"
    )

    return parser


def main():
    """
    Main function for the Yine command-line interface.
    """
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(args.logging_config if Path(args.logging_config).exists() else None)

    if args.cmd == "condition":
        settings = Settings.load(args.config).config
        run_conditioning(settings)
        return

    if args.cmd == "freeze-positive":
        exp = yaml.safe_load(Path(args.exp_config).read_text(encoding="utf-8"))
        ds = exp["dataset_v1"]

        cfg = FreezeConfig(
            input_cleaned_parquet=ds["input_cleaned_parquet"],
            output_positive_parquet=ds["output_positive_parquet"],
            output_manifest_yaml=ds["output_manifest_yaml"],
            col_source=ds["columns"]["source_tag"],
            col_target=ds["columns"]["target_text"],
            col_source_text=ds["columns"]["source_text"],
            algo=ds["ids"]["algo"],
            id_fields=ds["ids"]["fields"],
        )
        manifest = freeze_positive(cfg)
        log.info("freeze-positive OK: %s rows", manifest["rows"])
        return

    if args.cmd == "make-splits":
        cfg = SplitConfig(
            positive_parquet=args.positive,
            output_split_json=args.out,
            seed=args.seed,
            train=0.8,
            dev=0.1,
            test=0.1,
        )
        split = make_splits(cfg)
        log.info("make-splits OK: %s", split["counts"])
        return

    if args.cmd == "gen-negatives":
        exp = yaml.safe_load(Path(args.exp_config).read_text(encoding="utf-8"))
        ng = exp["negatives_v1"]

        loaded = load_generators_from_rules_yaml(
            ng["rules_yaml"],
            seed=ng.get("seed", 42)
        )
        log.info("Loaded generators: %s", loaded)

        cfg = NegativesConfig(
                positive_parquet=ng["positive_parquet"],
                split_json=ng["split_json"],
                output_root=ng["output_root"],
                rules_enabled=ng["rules_enabled"],
                k_min=ng["k_min"],
                k_max=ng["k_max"],
                ratio_target=ng["ratio_target"],
                seed=ng["seed"],
                col_pair_id=ng["columns"]["pair_id"],
                col_source_text=ng["columns"]["source_text"],
                col_target_text=ng["columns"]["target_text"],
            )
        summary = generate_negatives(cfg)
        log.info("gen-negatives OK: total=%s", summary["total"])
        return

    raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
