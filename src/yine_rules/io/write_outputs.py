"""
Utility functions for writing outputs
"""
from __future__ import annotations
from pathlib import Path
import csv
import pandas as pd

def ensure_dir(path: str | Path) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    :param path: The path to the directory to ensure exists
    :type path: str | Path
    :return: The Path object of the ensured directory
    :rtype: Path
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_parquet(df: pd.DataFrame, path: str) -> None:
    """
    Write a DataFrame to a Parquet file.
    
    :param df: The DataFrame to write
    :type df: pd.DataFrame
    :param path: The path to the Parquet file to write
    :type path: str
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def write_csv(df: pd.DataFrame, path: str) -> None:
    """
    Write a DataFrame to a CSV file.
    
    :param df: The DataFrame to write
    :type df: pd.DataFrame
    :param path: The path to the CSV file to write
    :type path: str
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        sep=";",
        quoting=csv.QUOTE_ALL
    )
