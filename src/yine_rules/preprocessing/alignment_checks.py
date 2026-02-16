"""
Checks for alignment issues between Yine and Spanish columns in a DataFrame.
"""
from __future__ import annotations
import pandas as pd
import regex as re

def find_alignment_suspects(df: pd.DataFrame, col_yine: str, col_spanish: str) -> pd.DataFrame:
    """
    Returns a dataframe of suspects with reasons (non-destructive).
    """
    suspects = []

    y = df[col_yine].fillna("").astype(str)
    es = df[col_spanish].fillna("").astype(str)

    # Quote balance suspects
    def odd_quotes(s: str, q: str) -> bool:
        return (s.count(q) % 2) != 0

    quote_mask = (
        y.map(lambda s: odd_quotes(s, '"') or odd_quotes(s, "'")) |
        es.map(lambda s: odd_quotes(s, '"') or odd_quotes(s, "'"))
    )
    if quote_mask.any():
        suspects.append(df[quote_mask].assign(suspect_reason="unbalanced_quotes"))

    # Parentheses balance
    def paren_unbalanced(s: str) -> bool:
        bal = 0
        for ch in s:
            if ch == "(":
                bal += 1
            elif ch == ")":
                bal -= 1
            if bal < 0:
                return True
        return bal != 0

    par_mask = y.map(paren_unbalanced) | es.map(paren_unbalanced)
    if par_mask.any():
        suspects.append(df[par_mask].assign(suspect_reason="unbalanced_parentheses"))

    # Punctuation mismatch heuristic: one has many parentheses or quotes, the other none
    mismatch_mask = (
        (y.str.contains(r"\(", regex=True) & ~es.str.contains(r"\(", regex=True)) |
        (~y.str.contains(r"\(", regex=True) & es.str.contains(r"\(", regex=True)) |
        (y.str.contains(r"\"", regex=True) & ~es.str.contains(r"\"", regex=True)) |
        (~y.str.contains(r"\"", regex=True) & es.str.contains(r"\"", regex=True))
    )
    if mismatch_mask.any():
        suspects.append(df[mismatch_mask].assign(suspect_reason="punctuation_side_mismatch"))

    if not suspects:
        return pd.DataFrame(columns=list(df.columns) + ["suspect_reason"])

    out = pd.concat(suspects, ignore_index=True)
    # Remove duplicates if a row appears in multiple suspect sets
    out = out.drop_duplicates(subset=[col_yine, col_spanish]).reset_index(drop=True)
    return out
