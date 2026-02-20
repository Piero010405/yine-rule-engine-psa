"""
Split dataset into train/dev/test
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import random
import pandas as pd

from yine_rules.io.writers import write_json

@dataclass
class SplitConfig:
    """
    Configuration for splitting the dataset.
    """
    positive_parquet: str
    output_split_json: str
    seed: int = 42
    train: float = 0.8
    dev: float = 0.1
    test: float = 0.1

def make_splits(cfg: SplitConfig) -> dict:
    """
    Make splits for the dataset, ensuring that the same pair_id always goes to the same split.
    """
    p = Path(cfg.positive_parquet)
    if not p.exists():
        raise FileNotFoundError(f"Missing positive parquet: {p}")

    df = pd.read_parquet(p, columns=["pair_id"])
    ids = df["pair_id"].tolist()

    rng = random.Random(cfg.seed)
    rng.shuffle(ids)

    n = len(ids)
    n_train = int(n * cfg.train)
    n_dev = int(n * cfg.dev)
    # resto va a test para que sume exacto
    train_ids = ids[:n_train]
    dev_ids = ids[n_train:n_train + n_dev]
    test_ids = ids[n_train + n_dev:]

    split = {
        "seed": cfg.seed,
        "ratios": {"train": cfg.train, "dev": cfg.dev, "test": cfg.test},
        "counts": {"train": len(train_ids), "dev": len(dev_ids), "test": len(test_ids)},
        "train_ids": train_ids,
        "dev_ids": dev_ids,
        "test_ids": test_ids,
    }

    write_json(cfg.output_split_json, split)
    return split
