"""
Utility functions for reproducibility
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pandas as pd

def stable_hash_dict(d: dict) -> str:
    """
    Generate a stable hash of a dictionary.
    
    :param d: The dictionary to hash
    :type d: dict
    :return: The SHA256 hash of the dictionary
    :rtype: str
    """
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def dataframe_fingerprint(df: pd.DataFrame, cols: list[str], max_rows: int = 5000) -> str:
    """
    Fast-ish dataset fingerprint: hash of first N rows in selected columns.

    :param df: The DataFrame to hash
    :type df: pd.DataFrame
    :param cols: List of columns to include in the hash
    :type cols: list[str]
    :param max_rows: Maximum number of rows to include in the hash
    :type max_rows: int
    :return: The SHA256 hash of the DataFrame
    """
    sub = df[cols].head(max_rows).copy()
    # Normalize NaNs
    sub = sub.fillna("")
    blob = sub.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def write_json(path: str | Path, payload: dict) -> None:
    """
    Docstring para write_json
    
    :param path: The path to write the JSON file to
    :type path: str | Path
    :param payload: The dictionary to write to the JSON file
    :type payload: dict
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
