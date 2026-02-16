"""
Utility functions for text normalization in DataFrames.
"""
from __future__ import annotations
import unicodedata
import pandas as pd
import regex as re

_WS_RE = re.compile(r"[ \t\u00A0\u2000-\u200B\u202F\u205F\u3000]+")  # includes NBSP and thin spaces

def _normalize_text(
    s: str,
    unicode_form: str = "NFC",
    trim: bool = True,
    collapse_spaces: bool = True,
    normalize_newlines: bool = True,
    replace_tabs: bool = True
) -> str:
    """
    Normalize text.
    
    :param s: The text to normalize
    :type s: str
    :param unicode_form: The Unicode form to use for normalization (e.g., "NFC", "NFD")
    :type unicode_form: str
    :param trim: Whether to trim whitespace from the beginning and end of each line
    :type trim: bool
    :param collapse_spaces: Whether to collapse multiple spaces into a single space
    :type collapse_spaces: bool
    :param normalize_newlines: Whether to normalize newlines (i.e., replace \r\n and \r with \n)
    :type normalize_newlines: bool
    :param replace_tabs: Whether to replace tabs with spaces
    :type replace_tabs: bool
    :return: The normalized text
    :rtype: str
    """
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)

    # Normalize newlines first
    if normalize_newlines:
        s = s.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with spaces
    if replace_tabs:
        s = s.replace("\t", " ")

    # Unicode normalization (keeps diacritics, but canonicalizes)
    s = unicodedata.normalize(unicode_form, s)

    # Collapse weird whitespace to single spaces (but keep newlines if any)
    if collapse_spaces:
        # Replace all non-newline whitespace runs with a single space
        parts = s.split("\n")
        parts = [_WS_RE.sub(" ", p) for p in parts]
        s = "\n".join(parts)

    if trim:
        # Trim each line, then trim whole
        lines = [ln.strip() for ln in s.split("\n")]
        s = "\n".join(lines).strip()

    return s

def normalize_dataframe_text(
    df: pd.DataFrame,
    text_cols: list[str],
    unicode_form: str,
    trim_whitespace: bool,
    collapse_spaces: bool,
    normalize_newlines: bool,
    replace_tabs: bool
) -> tuple[pd.DataFrame, dict]:
    """
    Returns normalized df and a normalization summary.

    :param df: The DataFrame to normalize
    :type df: pd.DataFrame
    :param text_cols: List of columns to normalize
    :type text_cols: list[str]
    :param unicode_form: The Unicode form to use for normalization (e.g., "NFC", "NFD")
    :type unicode_form: str
    :param trim_whitespace: Whether to trim whitespace from the beginning and end of each line
    :type trim_whitespace: bool
    :param collapse_spaces: Whether to collapse multiple spaces into a single space
    :type collapse_spaces: bool
    :param normalize_newlines: Whether to normalize newlines (i.e., replace \r\n and \r with \n)
    :type normalize_newlines: bool
    :param replace_tabs: Whether to replace tabs with spaces
    :type replace_tabs: bool
    :return: A tuple of the normalized DataFrame and a summary dictionary
    """
    summary = {"changed_rows": 0, "per_column_changed": {}}
    out = df.copy()

    for col in text_cols:
        before = out[col].fillna("").astype(str)
        after = before.map(lambda s: _normalize_text(
            s,
            unicode_form=unicode_form,
            trim=trim_whitespace,
            collapse_spaces=collapse_spaces,
            normalize_newlines=normalize_newlines,
            replace_tabs=replace_tabs
        ))
        changed = before != after
        summary["per_column_changed"][col] = int(changed.sum())
        out[col] = after

    summary["changed_rows"] = int(
        ((df[text_cols].
          fillna("").astype(str) != out[text_cols].fillna("").astype(str)).any(axis=1)).sum()
    )
    return out, summary
