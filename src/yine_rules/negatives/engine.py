"""
Global negative sampling engine (ratio-controlled).

Implements:
- Per-positive sampling
- Uniform rule selection
- k ~ Uniform(k_min, k_max)
- Global ratio_target enforcement
- Reproducibility via seed
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import random
import pandas as pd

from yine_rules.io.writers import write_json
from yine_rules.negatives.registry import get as get_generator
from yine_rules.negatives.reporting import export_negatives


@dataclass
class NegativesConfig:
    """Configuration for negative sample generation."""
    positive_parquet: str
    split_json: str
    output_root: str
    rules_enabled: list[str]
    k_min: int
    k_max: int
    ratio_target: float
    seed: int


def load_split(path: str) -> dict:
    """Load split from JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_split_index(split: dict) -> dict[str, str]:
    """Build index from pair_id to split label."""
    idx = {}
    for pid in split["train_ids"]:
        idx[pid] = "train"
    for pid in split["dev_ids"]:
        idx[pid] = "dev"
    for pid in split["test_ids"]:
        idx[pid] = "test"
    return idx


def generate_negatives(cfg: NegativesConfig) -> dict:
    """Generate negative samples based on the provided configuration"""
    rng = random.Random(cfg.seed)

    df = pd.read_parquet(cfg.positive_parquet)
    split = load_split(cfg.split_json)
    split_idx = build_split_index(split)

    out_root = Path(cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    all_samples = []

    n_positive = len(df)
    max_negatives_allowed = int(n_positive * cfg.ratio_target)

    for _, row in df.iterrows():
        if len(all_samples) >= max_negatives_allowed:
            break

        pair_id = row["pair_id"]
        source_text = str(row["source_text"])
        target_text = str(row["target_text"])
        split_label = split_idx.get(pair_id)

        if split_label is None:
            continue

        # sample k
        k = rng.randint(cfg.k_min, cfg.k_max)

        # choose rules uniformly
        for _ in range(k):
            if len(all_samples) >= max_negatives_allowed:
                break

            rule_id = rng.choice(cfg.rules_enabled)
            generator = get_generator(rule_id)

            samples = generator.generate(
                pair_id=pair_id,
                source_text=source_text,
                target_text=target_text,
                split=split_label,
            )

            # avoid duplicates per pair
            for s in samples:
                if len(all_samples) >= max_negatives_allowed:
                    break
                all_samples.append(s)

    stats = export_negatives(all_samples, out_root)

    summary = {
        "positive_rows": n_positive,
        "negative_rows": stats["rows"],
        "ratio_actual": round(stats["rows"] / n_positive, 4),
        "k_min": cfg.k_min,
        "k_max": cfg.k_max,
        "ratio_target": cfg.ratio_target,
        "rules": cfg.rules_enabled,
    }

    write_json(out_root / "manifest.json", summary)

    return summary
