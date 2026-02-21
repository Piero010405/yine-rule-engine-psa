"""
Strict validation script for R7:
Gender agreement suffix flipping on adjective-like tokens.

Strategy (high precision):
- Only consider tokens that match a curated adjective seed list.
- From those, accept only tokens that end with enabled agreement suffixes (pairs).
- Report context windows for manual inspection.

This avoids false positives from generic endings (e.g., -ne is too common).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd
import yaml

POSITIVE_PARQUET = "data/processed/positive/positive_corpus.v1.parquet"

ADJ_YAML = "resources/lexicons/r7_adjectives_yine.yaml"
SUFFIX_YAML = "resources/lexicons/r7_agreement_suffixes.yaml"

COL_SOURCE = "spanish"
COL_TARGET = "yine"

TOKEN_RE = re.compile(r"\b[a-zñáéíóúü]+\b", re.IGNORECASE)


@dataclass(frozen=True)
class Pair:
    """Pair of agreement suffixes."""
    masc: str
    fem: str


def load_adj_seed(path: str) -> set[str]:
    """Load the seed adjectives from the YAML file and return a set of lowercase words."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(w.lower() for w in data["r7_adjectives_seed"]["adjectives"])


def load_pairs(path: str) -> tuple[list[Pair], int]:
    """
    Load the agreement suffix pairs from the YAML file and return a list of Pair objects and minimum 
    token length.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = data["r7_agreement_suffixes"]
    min_len = int(root.get("min_token_len", 4))

    pairs = []
    for p in root["pairs"]:
        if not p.get("enabled", True):
            continue
        pairs.append(Pair(masc=str(p["masc"]).lower(), fem=str(p["fem"]).lower()))
    return pairs, min_len


def window(tokens: list[str], i: int, w: int = 4) -> str:
    """Window of tokens around index i with width w."""
    lo = max(0, i - w)
    hi = min(len(tokens), i + w + 1)
    return " ".join(tokens[lo:hi])


def main():
    """
    Perform the strict validation for R7 candidates based on seed adjectives and agreement suffixes.
    """
    adjs = load_adj_seed(ADJ_YAML)
    pairs, min_len = load_pairs(SUFFIX_YAML)

    enabled_suffixes = set()
    flip_map = {}
    for p in pairs:
        enabled_suffixes.add(p.masc)
        enabled_suffixes.add(p.fem)
        flip_map[p.masc] = p.fem
        flip_map[p.fem] = p.masc

    df = pd.read_parquet(POSITIVE_PARQUET)

    total_rows = len(df)
    rows_with_seed_adj = 0
    rows_with_flip_candidate = 0

    by_suffix = Counter()
    by_adj = Counter()
    examples = []

    for _, row in df.iterrows():
        src = str(row[COL_SOURCE]).lower()
        tgt = str(row[COL_TARGET]).lower()

        tokens = [t.lower() for t in TOKEN_RE.findall(tgt)]
        if not tokens:
            continue

        seed_positions = [(i, t) for i, t in enumerate(tokens) if t in adjs]
        if not seed_positions:
            continue

        rows_with_seed_adj += 1

        # Look for flip candidates among the seed adjectives
        found_in_row = False
        for i, tok in seed_positions:
            if len(tok) < min_len:
                continue

            # check if token ends with any enabled suffix
            hit_suffix = None
            for suf in enabled_suffixes:
                if tok.endswith(suf) and len(tok) > len(suf) + 1:
                    hit_suffix = suf
                    break

            if not hit_suffix:
                continue

            found_in_row = True
            rows_with_flip_candidate += 1
            by_suffix[hit_suffix] += 1
            by_adj[tok] += 1

            if len(examples) < 35:
                flipped = tok[: -len(hit_suffix)] + flip_map[hit_suffix]
                examples.append(
                    {
                        "spanish": src,
                        "yine_context": " ".join(tokens),
                        "hit_token": tok,
                        "hit_suffix": hit_suffix,
                        "would_flip_to": flipped,
                        "window": window(tokens, i, w=4),
                    }
                )

            # count at most 1 candidate per row for coverage
            break

        if found_in_row:
            # already incremented rows_with_flip_candidate inside loop once,
            # but that was per hit; ensure per-row behavior:
            # We used break, so it is already per-row.
            pass

    print("\n================ R7 STRICT VALIDATION REPORT ================\n")
    print(f"Total rows in corpus: {total_rows}")
    print(f"Rows with seed adjective present: {rows_with_seed_adj}")
    print(f"Rows with flip-candidate (seed + suffix-pair): {rows_with_flip_candidate}")

    if total_rows:
        print(f"Coverage (flip-candidate / total): {round(
            rows_with_flip_candidate / total_rows, 4)
            }"
        )
    if rows_with_seed_adj:
        print(f"Precision proxy (flip-candidate / seed-adj rows): {round(
            rows_with_flip_candidate / rows_with_seed_adj, 4)
            }"
        )

    print("\nEnabled suffixes used:")
    print(sorted(enabled_suffixes))

    print("\nDistribution by suffix:")
    for k, v in by_suffix.most_common():
        print(f"  {k}: {v}")

    print("\nTop adjective tokens that are flip-candidates:")
    for k, v in by_adj.most_common(20):
        print(f"  {k}: {v}")

    print("\nSample examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
