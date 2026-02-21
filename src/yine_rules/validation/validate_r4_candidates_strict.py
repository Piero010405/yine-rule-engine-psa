"""
Validation script for Rule R4: PSSD candidates in Yine when Spanish possessives are present.
"""
from __future__ import annotations

import re
from pathlib import Path
from collections import Counter
import pandas as pd
import yaml


# =========================
# CONFIG
# =========================
POSITIVE_PARQUET = "data/processed/positive/positive_corpus.v1.parquet"
POSESIVOS_YAML = "resources/lexicons/posesivos_es.yaml"
PSSD_YAML = "resources/lexicons/pssd_suffixes.yaml"
PREFIX_YAML = "resources/lexicons/possessive_prefixes_yine.yaml"

COL_PAIR_ID = "pair_id"
COL_SOURCE = "spanish"
COL_TARGET = "yine"

# =========================
# LOAD RESOURCES
# =========================
def load_posesivos(path: str) -> set[str]:
    """
    Load Spanish possessive forms from a YAML file and return them as a set of lowercase strings.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(w.lower() for w in data["posesivos_espanol"]["formas"])


def load_pssd(path: str) -> list[str]:
    """
    Load PSSD suffixes from a YAML file and return them as a list of strings.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data["pssd"]["suffixes"]


def load_prefixes(path: str) -> list[str]:
    """
    Load candidate prefixes for PSSD validation rules from a YAML file
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data["possessive_prefixes_yine"]["observable_prefixes"]


# =========================
# VALIDATION
# =========================
def main():
    """
    Main function to perform validation for Rule R4
    """

    posesivos = load_posesivos(POSESIVOS_YAML)
    pssd = load_pssd(PSSD_YAML)
    prefixes = load_prefixes(PREFIX_YAML)

    df = pd.read_parquet(POSITIVE_PARQUET)

    total_rows = len(df)

    possessive_rows = 0
    valid_candidates = 0
    examples = []

    suffix_counter = Counter()
    prefix_counter = Counter()

    for _, row in df.iterrows():
        source = str(row[COL_SOURCE]).lower()
        target = str(row[COL_TARGET]).lower()

        # Trigger estricto: posesivo español
        if any(re.search(rf"\b{re.escape(p)}\b", source) for p in posesivos):
            possessive_rows += 1

            tokens = re.findall(r"\b\w+\b", target)

            for token in tokens:
                for pref in prefixes:
                    if token.startswith(pref):
                        for suf in pssd:
                            if token.endswith(suf):
                                valid_candidates += 1
                                suffix_counter[suf] += 1
                                prefix_counter[pref] += 1

                                if len(examples) < 20:
                                    examples.append({
                                        "spanish": source,
                                        "yine_token": token,
                                        "prefix": pref,
                                        "suffix": suf
                                    })
                                break

    print("\n================ R4 STRICT VALIDATION REPORT ================\n")
    print(f"Total rows in corpus: {total_rows}")
    print(f"Rows with Spanish possessive: {possessive_rows}")
    print(f"Valid PSSD candidates (strict filter): {valid_candidates}")

    if possessive_rows > 0:
        coverage = round(valid_candidates / possessive_rows, 4)
        print(f"Coverage (strict): {coverage}")

    print("\nSuffix distribution:")
    for k, v in suffix_counter.items():
        print(f"  {k}: {v}")

    print("\nPrefix distribution:")
    for k, v in prefix_counter.items():
        print(f"  {k}: {v}")

    print("\nSample examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
