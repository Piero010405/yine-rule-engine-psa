"""
Scan corpus to see actual endings of seed adjectives (R7 support script).

Goal:
- corpus-driven evidence of endings (e.g., lu/lo/tu/to/ru/ro) on tokens that are
  known adjectives from a curated list.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import pandas as pd
import yaml

POSITIVE_PARQUET = "data/processed/positive/positive_corpus.v1.parquet"

ADJ_YAML = "resources/lexicons/r7_adjectives_yine.yaml"

COL_SOURCE = "spanish"
COL_TARGET = "yine"

TOKEN_RE = re.compile(r"\b[a-zñáéíóúü]+\b", re.IGNORECASE)


def load_adj_seed(path: str) -> set[str]:
    """Load the seed adjectives from the YAML file and return a set of lowercase words."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(w.lower() for w in data["r7_adjectives_seed"]["adjectives"])


def main():
    """Scan the corpus for occurrences of seed adjectives and analyze their endings."""
    adjs = load_adj_seed(ADJ_YAML)
    df = pd.read_parquet(POSITIVE_PARQUET)

    rows_with_adj = 0
    end2 = Counter()
    end3 = Counter()
    token_counter = Counter()
    examples = []

    for _, row in df.iterrows():
        tgt = str(row[COL_TARGET]).lower()
        src = str(row[COL_SOURCE]).lower()

        tokens = TOKEN_RE.findall(tgt)
        hits = [t for t in tokens if t in adjs]
        if not hits:
            continue

        rows_with_adj += 1
        for t in hits:
            token_counter[t] += 1
            if len(t) >= 2:
                end2[t[-2:]] += 1
            if len(t) >= 3:
                end3[t[-3:]] += 1

        if len(examples) < 25:
            examples.append(
                {
                    "spanish": src,
                    "yine": tgt,
                    "hit_tokens": hits[:5],
                }
            )

    print("\n================ R7 ENDINGS SCAN REPORT ================\n")
    print(f"Total rows: {len(df)}")
    print(f"Rows with at least 1 seed adjective: {rows_with_adj}")
    print(f"Coverage: {round(rows_with_adj / len(df), 4)}")

    print("\nTop adjective tokens (seed hits):")
    for tok, c in token_counter.most_common(20):
        print(f"  {tok}: {c}")

    print("\nTop endings (last 2 chars):")
    for suf, c in end2.most_common(20):
        print(f"  {suf}: {c}")

    print("\nTop endings (last 3 chars):")
    for suf, c in end3.most_common(20):
        print(f"  {suf}: {c}")

    print("\nSample examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
