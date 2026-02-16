"""
Utility functions for reading the full corpus CSV.
"""
from __future__ import annotations
import pandas as pd

def read_full_corpus_csv(path: str, col_yine: str, col_spanish: str, col_source: str, encoding: str = "utf-8") -> pd.DataFrame:
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
    df = pd.read_csv(path, encoding=encoding)
    missing = [c for c in [col_yine, col_spanish, col_source] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}. Found: {list(df.columns)}")
    return df[[col_yine, col_spanish, col_source]].copy()
