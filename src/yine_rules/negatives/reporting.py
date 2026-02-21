"""
Reporting utilities for negative sample generation.
"""
from collections import Counter
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from yine_rules.io.writers import write_json


def export_negatives(samples, out_dir: str | Path) -> dict:
    """
    Export negative samples to Parquet files, organized by rule and split.
    """
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)

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

    # -------------------------
    # Save merged
    # -------------------------
    df.to_parquet(outp / "negatives.parquet", index=False)

    # -------------------------
    # Save per-rule
    # -------------------------
    by_rule = Counter(df["rule_id"]) if len(df) else Counter()
    by_split = Counter(df["split"]) if len(df) else Counter()

    for rule_id in by_rule.keys():
        rule_dir = outp / rule_id
        rule_dir.mkdir(parents=True, exist_ok=True)

        df_rule = df[df["rule_id"] == rule_id]
        df_rule.to_parquet(rule_dir / "negatives.parquet", index=False)

        rule_stats = {
            "rows": int(len(df_rule)),
            "by_split": dict(Counter(df_rule["split"])),
        }

        write_json(rule_dir / "stats.json", rule_stats)

    # -------------------------
    # Global stats
    # -------------------------
    stats = {
        "rows": int(len(df)),
        "by_rule": dict(by_rule),
        "by_split": dict(by_split),
        "columns": list(df.columns),
    }

    write_json(outp / "stats.json", stats)

    return stats
