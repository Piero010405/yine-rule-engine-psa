"""
Final structural validation for R7:
Check whether flip-candidate adjectives occur inside NP contexts.

We verify adjacency patterns:
  ADJ + N
  N + ADJ

Heuristic NP detection (no POS tagging).
"""

from __future__ import annotations

from collections import Counter
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

# Small functional word filter (expandable)
STOPWORDS_YINE = {
    "wa", "ga", "gi", "wane", "wale", "giyagni",
    "satu", "sato", "pa"
}

# Very light verbal suffix heuristic (to exclude obvious verbs)
VERBAL_SUFFIXES = ("ta", "na", "kalu", "luwa", "tka")


def load_adj_seed(path: str) -> set[str]:
    """Load the seed adjectives from the YAML file and return a set of lowercase words."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(w.lower() for w in data["r7_adjectives_seed"]["adjectives"])


def load_enabled_suffixes(path: str) -> set[str]:
    """
    Load the agreement suffix pairs from the YAML file and return a set of enabled suffixes.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = data["r7_agreement_suffixes"]
    enabled = set()
    for p in root["pairs"]:
        if p.get("enabled", True):
            enabled.add(p["masc"].lower())
            enabled.add(p["fem"].lower())
    return enabled


def looks_like_noun(tok: str) -> bool:
    """Heuristic to check if a token looks like a noun (for NP context detection)."""
    if tok in STOPWORDS_YINE:
        return False
    if len(tok) < 3:
        return False
    if tok.endswith(VERBAL_SUFFIXES):
        return False
    return True


def main():
    """
    Perform the structural validation for R7 candidates based on seed adjectives and agreement 
    suffixes.
    """
    adjs = load_adj_seed(ADJ_YAML)
    suffixes = load_enabled_suffixes(SUFFIX_YAML)

    df = pd.read_parquet(POSITIVE_PARQUET)

    total_flip_candidates = 0
    np_context_count = 0

    pattern_counter = Counter()
    examples_np = []
    examples_non_np = []

    for _, row in df.iterrows():
        tgt = str(row[COL_TARGET]).lower()
        tokens = [t.lower() for t in TOKEN_RE.findall(tgt)]

        for i, tok in enumerate(tokens):
            if tok not in adjs:
                continue

            # Check if token is flipable
            hit_suffix = None
            for suf in suffixes:
                if tok.endswith(suf) and len(tok) > len(suf) + 1:
                    hit_suffix = suf
                    break

            if not hit_suffix:
                continue

            total_flip_candidates += 1

            left = tokens[i - 1] if i > 0 else None
            right = tokens[i + 1] if i < len(tokens) - 1 else None

            in_np = False
            pattern = None

            # ADJ + N
            if right and looks_like_noun(right):
                in_np = True
                pattern = "ADJ+N"

            # N + ADJ
            elif left and looks_like_noun(left):
                in_np = True
                pattern = "N+ADJ"

            if in_np:
                np_context_count += 1
                pattern_counter[pattern] += 1
                if len(examples_np) < 20:
                    examples_np.append({
                        "context": " ".join(tokens),
                        "adj": tok,
                        "pattern": pattern
                    })
            else:
                if len(examples_non_np) < 15:
                    examples_non_np.append({
                        "context": " ".join(tokens),
                        "adj": tok
                    })

    print("\n================ R7 NP STRUCTURAL VALIDATION ================\n")
    print(f"Total flip-candidates detected: {total_flip_candidates}")
    print(f"Flip-candidates in NP context: {np_context_count}")

    if total_flip_candidates:
        print(f"NP ratio: {round(np_context_count / total_flip_candidates, 4)}")

    print("\nNP Pattern distribution:")
    for k, v in pattern_counter.items():
        print(f"  {k}: {v}")

    print("\nExamples (NP context):")
    for ex in examples_np:
        print(ex)

    print("\nExamples (Non-NP context):")
    for ex in examples_non_np:
        print(ex)


if __name__ == "__main__":
    main()
