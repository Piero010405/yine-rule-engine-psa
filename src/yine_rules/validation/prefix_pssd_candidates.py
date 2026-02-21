"""
Prefix candidates for PSSD validation rules.
"""
from __future__ import annotations
import re
from collections import Counter
import pandas as pd

PSSD_SUFFIXES = ["te", "ne", "re", "le"]

def tokenize(text):
    """Simple tokenizer that extracts words from text."""
    return re.findall(r"\b\w+\b", text.lower())

def extract_prefix_candidates(parquet_path: str, col_target: str):
    """
    Extract candidate prefixes for PSSD validation rules from the specified column of a Parquet file
    """
    df = pd.read_parquet(parquet_path)
    prefix_counter = Counter()

    for text in df[col_target].astype(str):
        for tok in tokenize(text):
            for suf in PSSD_SUFFIXES:
                if tok.endswith(suf) and len(tok) > len(suf) + 2:
                    stem = tok[:-len(suf)]
                    # Tomamos primeros 2–3 caracteres como candidato
                    prefix_counter[stem[:2]] += 1
                    prefix_counter[stem[:3]] += 1

    return prefix_counter.most_common(30)


if __name__ == "__main__":
    result = extract_prefix_candidates(
        "data/processed/positive/positive_corpus.v1.parquet",
        "yine"
    )
    print(result)
