"""
R4 Validation Module
Compute empirical statistics for Possessed Status Suffix (PSSD)
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
import pandas as pd

PSSD_SUFFIXES_EXPLICIT = ["te", "ne", "re", "le"]
MIN_TOKEN_LEN = 4

def tokenize(text: str):
    """Simple tokenizer that extracts words from text."""
    return re.findall(r"\b\w+\b", text.lower())


def compute_pssd_stats(parquet_path: str, col_target: str):
    """
    Compute statistics for Possessed Status Suffix (PSSD) in the specified column of a Parquet file.
    """
    df = pd.read_parquet(parquet_path)

    suffix_counter = Counter()
    examples = defaultdict(list)
    total_tokens = 0

    for text in df[col_target].astype(str):
        tokens = tokenize(text)
        total_tokens += len(tokens)

        for tok in tokens:
            if len(tok) < MIN_TOKEN_LEN:
                continue

            for suf in PSSD_SUFFIXES_EXPLICIT:
                if tok.endswith(suf):
                    suffix_counter[suf] += 1
                    if len(examples[suf]) < 20:
                        examples[suf].append(tok)

    stats = []
    for suf in PSSD_SUFFIXES_EXPLICIT:
        count = suffix_counter[suf]
        percent = round(count / total_tokens * 100, 4) if total_tokens else 0
        stats.append({
            "suffix": suf,
            "count": count,
            "percent_of_tokens": percent,
            "examples": examples[suf]
        })

    return {
        "total_tokens": total_tokens,
        "suffix_stats": stats
    }


if __name__ == "__main__":
    result = compute_pssd_stats(
        parquet_path="data/processed/positive/positive_corpus.v1.parquet",
        col_target="yine"
    )
    print(result)
