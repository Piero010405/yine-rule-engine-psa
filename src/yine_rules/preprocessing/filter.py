"""
Utility functions for filtering DataFrames based on various criteria.
"""
from __future__ import annotations
import pandas as pd
import regex as re

_TOKEN_RE = re.compile(r"\p{L}+|\p{N}+|[^\s]")

def token_count(s: str) -> int:
    """
    Returns the number of tokens in a string
    
    :param s: The string to count tokens in
    :type s: str
    :return: The number of tokens in the string
    :rtype: int
    """
    if not s:
        return 0
    return len(_TOKEN_RE.findall(s))

def apply_filters(
    df: pd.DataFrame,
    col_yine: str,
    col_spanish: str,
    drop_empty: bool,
    min_chars: int,
    min_tokens: int,
    max_tokens: int,
    length_ratio_enabled: bool,
    min_ratio: float,
    max_ratio: float,
    dedup_enabled: bool,
    dedup_subset: list[str]
) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """
    Apply various filters to the DataFrame and return the filtered DataFrame

    :param df: The DataFrame to filter
    :type df: pd.DataFrame
    :param col_yine: The name of the Yine column in the DataFrame
    :type col_yine: str
    :param col_spanish: The name of the Spanish column in the DataFrame
    :type col_spanish: str
    :param drop_empty: Whether to drop rows where either column is empty
    :type drop_empty: bool
    :param min_chars: Minimum number of characters required in each column
    :type min_chars: int
    :param min_tokens: Minimum number of tokens required in each column
    :type min_tokens: int
    :param max_tokens: Maximum number of tokens allowed in each column
    :type max_tokens: int
    :param length_ratio_enabled: Whether to enable filtering based on the ratio of token
    counts between the columns
    :type length_ratio_enabled: bool
    :param min_ratio: Minimum ratio of token counts between the two columns
    :type min_ratio: float
    :param max_ratio: Maximum ratio of token counts between the two columns
    :type max_ratio: float
    :param dedup_enabled: Whether to enable deduplication based on a subset of columns
    :type dedup_enabled: bool
    :param dedup_subset: List of columns to use for deduplication
    :type dedup_subset: list[str]
    :return: A tuple of the filtered DataFrame, a report dictionary, 
    and a DataFrame of removed rows with reasons
    :rtype: tuple[pd.DataFrame, dict, pd.DataFrame]
    """
    report = {"start_rows": int(len(df)), "removed": {}}
    removed_parts = []

    work = df.copy()
    y = work[col_yine].fillna("").astype(str)
    es = work[col_spanish].fillna("").astype(str)

    # 1) Drop empty
    if drop_empty:
        mask_empty = (y.str.strip() == "") | (es.str.strip() == "")
        removed_parts.append(work[mask_empty].assign(reason="empty_row"))
        work = work[~mask_empty].copy()
        report["removed"]["empty_row"] = int(mask_empty.sum())

    # Refresh
    y = work[col_yine].fillna("").astype(str)
    es = work[col_spanish].fillna("").astype(str)

    # 2) Min chars
    mask_min_chars = (y.str.len() < min_chars) | (es.str.len() < min_chars)
    removed_parts.append(work[mask_min_chars].assign(reason="min_chars"))
    work = work[~mask_min_chars].copy()
    report["removed"]["min_chars"] = int(mask_min_chars.sum())

    # 3) Token length filter
    y_tok = y.map(token_count)
    es_tok = es.map(token_count)
    mask_tok = (
                (y_tok < min_tokens) |
                (es_tok < min_tokens) |
                (y_tok > max_tokens) |
                (es_tok > max_tokens)
                )
    removed_parts.append(work[mask_tok].assign(reason="token_length"))
    work = work[~mask_tok].copy()
    report["removed"]["token_length"] = int(mask_tok.sum())

    # Refresh
    y = work[col_yine].fillna("").astype(str)
    es = work[col_spanish].fillna("").astype(str)
    y_tok = y.map(token_count)
    es_tok = es.map(token_count)

    # 4) Length ratio filter
    if length_ratio_enabled:
        ratio = (y_tok / es_tok.replace(0, pd.NA)).astype("float").fillna(0.0)
        mask_ratio = (ratio != 0.0) & ((ratio < min_ratio) | (ratio > max_ratio))
        removed_parts.append(work[mask_ratio].assign(reason="length_ratio"))
        work = work[~mask_ratio].copy()
        report["removed"]["length_ratio"] = int(mask_ratio.sum())

    # 5) Dedup
    if dedup_enabled:
        dup_mask = work.duplicated(subset=dedup_subset, keep="first")
        removed_parts.append(work[dup_mask].assign(reason="duplicate"))
        work = work[~dup_mask].copy()
        report["removed"]["duplicate"] = int(dup_mask.sum())

    report["end_rows"] = int(len(work))
    removed_df = pd.concat(removed_parts, ignore_index=True) if removed_parts else pd.DataFrame()
    return work, report, removed_df
