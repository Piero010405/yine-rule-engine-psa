"""
Utility functions for reading the full corpus CSV.
"""
from __future__ import annotations
import csv
import pandas as pd
from pathlib import Path

def detect_delimiter(path: str) -> str:
    """
    Detect CSV delimiter using csv.Sniffer.
    :param path: The path to the CSV file
    :type path: str
    """
    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(4096)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";"])
        return dialect.delimiter

def read_full_corpus_csv(
    path: str,
    col_yine: str,
    col_spanish: str,
    col_source: str,
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """
    Read the full corpus CSV.
    
    :param path: The path to the full corpus CSV file
    :type path: str
    :param col_yine: The name of the Yine column in the CSV
    :type col_yine: str
    :param col_spanish: The name of the Spanish column in the CSV
    :type col_spanish: str
    :param col_source: The name of the source column in the CSV
    :type col_source: str
    :param encoding: The encoding of the CSV file
    :type encoding: str
    :return: The DataFrame with only the specified columns
    :rtype: DataFrame
    """

    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"CSV not found at: {path}")

    delimiter = detect_delimiter(path)

    try:
        df = pd.read_csv(
            path,
            encoding=encoding,
            sep=delimiter,
            engine="python",   # robust parsing
            quotechar='"'
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed reading CSV with detected delimiter '{delimiter}': {e}"
        ) from e

    missing = [c for c in [col_yine, col_spanish, col_source] if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in CSV: {missing}. "
            f"Found: {list(df.columns)}"
        )

    return df[[col_yine, col_spanish, col_source]].copy()
