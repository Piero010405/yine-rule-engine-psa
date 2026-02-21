"""
Validation script for Rule R6:
Strict NP simple pattern with Spanish-Yine correspondence.
"""

from __future__ import annotations

import re
from pathlib import Path
from collections import Counter
import pandas as pd
import yaml


POSITIVE_PARQUET = "data/processed/positive/positive_corpus.v1.parquet"
DETERMINERS_YINE_YAML = "resources/lexicons/yine_determiners.yaml"
DETERMINERS_ES_YAML = "resources/lexicons/determiners_es.yaml"

COL_SOURCE = "spanish"
COL_TARGET = "yine"


def load_yine_dets(path: str) -> set[str]:
    """
    Cargamos los determinantes de Yine desde el YAML.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(data["yine_determiners"]["articles"])  # excluimos wa y pa por ahora


def load_spanish_articles(path: str) -> set[str]:
    """
    Cargamos los artículos definidos e indefinidos del español desde el YAML.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    arts = data["determinantes_espanol"]["articulos"]
    return set(
        arts["definidos"] +
        arts["indefinidos"]
    )


def main():
    """
    Main function to perform validation for Rule R6
    """

    yine_dets = load_yine_dets(DETERMINERS_YINE_YAML)
    es_articles = load_spanish_articles(DETERMINERS_ES_YAML)

    df = pd.read_parquet(POSITIVE_PARQUET)

    total_rows = len(df)
    candidate_rows = 0
    det_counter = Counter()
    examples = []

    for _, row in df.iterrows():
        source = str(row[COL_SOURCE]).lower()
        target = str(row[COL_TARGET]).lower()

        # Trigger en español
        if not any(re.search(rf"\b{art}\b", source) for art in es_articles):
            continue

        tokens = re.findall(r"\b[a-zñ]+\b", target)

        for i in range(len(tokens) - 1):
            t0 = tokens[i]
            t1 = tokens[i + 1]

            if t0 in yine_dets and len(t1) >= 3:

                candidate_rows += 1
                det_counter[t0] += 1

                if len(examples) < 30:
                    examples.append({
                        "spanish": source,
                        "yine_context": target,
                        "det": t0,
                        "noun_candidate": t1
                    })

                break

    print("\n================ R6 STRICT VALIDATION REPORT ================\n")
    print(f"Total rows in corpus: {total_rows}")
    print(f"Rows with aligned DET + N: {candidate_rows}")
    print(f"Coverage: {round(candidate_rows / total_rows, 4)}")

    print("\nDistribution:")
    for k, v in det_counter.items():
        print(f"  {k}: {v}")

    print("\nSample examples:")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
