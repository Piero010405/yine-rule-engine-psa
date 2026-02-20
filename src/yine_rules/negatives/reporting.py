"""
Reporting utilities for negative sample generation.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from pathlib import Path
import pandas as pd

from yine_rules.io.writers import write_json


def export_negatives(samples, out_dir: str | Path) -> dict:
    """
    Export negative samples to parquet + stats.json inside out_dir.
    samples: list[NegativeSample]
    """
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)

    # Convert to DataFrame (even if empty)
    if samples:
        df = pd.DataFrame([asdict(s) for s in samples])
    else:
        df = pd.DataFrame(
            columns=[
                "pair_id",
                "source_text",
                "target_text",
                "negative_text",
                "rule_id",
                "violation_type",
                "severity",
                "metadata",
                "split",
            ]
        )

    parquet_path = outp / "negatives.parquet"
    df.to_parquet(parquet_path, index=False)

    # Stats
    c_rule = Counter(df["rule_id"]) if len(df) else Counter()
    c_split = Counter(df["split"]) if len(df) else Counter()

    stats = {
        "rows": int(len(df)),
        "by_rule": dict(c_rule),
        "by_split": dict(c_split),
        "columns": list(df.columns),
    }

    write_json(outp / "stats.json", stats)
    return stats
