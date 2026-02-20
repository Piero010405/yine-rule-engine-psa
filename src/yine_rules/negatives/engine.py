"""
Engine to generate negative samples based on rules.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd

from yine_rules.io.writers import write_json
from yine_rules.negatives.registry import get as get_generator
from yine_rules.negatives.reporting import export_negatives


@dataclass
class NegativesConfig:
    """Configuration for generating negative samples."""
    positive_parquet: str
    split_json: str
    output_root: str
    rules_enabled: list[str]


def load_split(path: str) -> dict:
    """Load the split JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_split_index(split: dict) -> dict[str, str]:
    """Build an index from pair_id to split (train/dev/test)."""
    idx: dict[str, str] = {}
    for pid in split.get("train_ids", []):
        idx[pid] = "train"
    for pid in split.get("dev_ids", []):
        idx[pid] = "dev"
    for pid in split.get("test_ids", []):
        idx[pid] = "test"
    return idx


def generate_negatives(cfg: NegativesConfig) -> dict:
    """Generate negative samples based on rules."""
    df = pd.read_parquet(cfg.positive_parquet)
    split = load_split(cfg.split_json)
    split_idx = build_split_index(split)

    out_root = Path(cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    summary = {"rules": {}, "total": 0, "notes": {}}

    # basic schema guard
    required_cols = {"pair_id", "spanish", "yine", "source"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"positive parquet missing columns: {missing}. Found: {list(df.columns)}")

    for rule_id in cfg.rules_enabled:
        rule_out = out_root / rule_id
        rule_out.mkdir(parents=True, exist_ok=True)

        try:
            gen = get_generator(rule_id)
        except KeyError:
            # Scaffold mode: generator not implemented yet
            stats = export_negatives([], rule_out)
            summary["rules"][rule_id] = stats
            summary["notes"][rule_id] = "generator_not_registered_yet"
            continue

        samples = []
        for _, r in df.iterrows():
            pid = r["pair_id"]
            sp = str(r["spanish"])
            yi = str(r["yine"])
            spl = split_idx.get(pid)
            if spl is None:
                # si no está en split -> lo registramos como nota, pero no rompemos
                continue

            samples.extend(gen.generate(pair_id=pid, source_text=sp, target_text=yi, split=spl))

        stats = export_negatives(samples, rule_out)
        summary["rules"][rule_id] = stats
        summary["total"] += stats["rows"]

    write_json(out_root / "manifest.json", summary)
    return summary
