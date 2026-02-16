"""
Utility functions for audit
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import pandas as pd
import regex as re

@dataclass(frozen=True)
class AuditResult:
    """
    Audit results
    """
    total_rows: int
    empty_yine: int
    empty_spanish: int
    unbalanced_double_quotes_yine: int
    unbalanced_double_quotes_spanish: int
    unbalanced_single_quotes_yine: int
    unbalanced_single_quotes_spanish: int
    unbalanced_parens_yine: int
    unbalanced_parens_spanish: int
    rows_with_newlines_yine: int
    rows_with_newlines_spanish: int
    punctuation_heavy_yine: int
    punctuation_heavy_spanish: int
    token_len_stats: dict
    length_ratio_stats: dict
    char_top_yine: list[tuple[str,int]]
    char_top_spanish: list[tuple[str,int]]

_PUNCT_RE = re.compile(r"\p{P}+")
_TOKEN_RE = re.compile(r"\p{L}+|\p{N}+|[^\s]")  # rough tokenization

def _count_unbalanced_pairs(text: str, open_ch: str, close_ch: str) -> int:
    bal = 0
    for ch in text:
        if ch == open_ch:
            bal += 1
        elif ch == close_ch:
            bal -= 1
        if bal < 0:
            return 1  # early negative balance counts as unbalanced
    return 1 if bal != 0 else 0

def _count_unbalanced_quotes(text: str, quote_ch: str) -> int:
    return 1 if (text.count(quote_ch) % 2 != 0) else 0

def _token_count(s: str) -> int:
    if not s:
        return 0
    return len(_TOKEN_RE.findall(s))

def _punct_ratio(s: str) -> float:
    if not s:
        return 0.0
    punct = len(_PUNCT_RE.findall(s))
    return punct / max(1, len(s))

def run_audit(df: pd.DataFrame, col_yine: str, col_spanish: str) -> AuditResult:
    """
    Run audit on a DataFrame with two text columns.
    
    :param df: The DataFrame to audit
    :type df: pd.DataFrame
    :param col_yine: The name of the Yine column
    :type col_yine: str
    :param col_spanish: The name of the Spanish column
    :type col_spanish: str
    :return: The audit results
    :rtype: AuditResult
    """
    y = df[col_yine].fillna("").astype(str)
    es = df[col_spanish].fillna("").astype(str)

    empty_y = int((y.str.strip() == "").sum())
    empty_es = int((es.str.strip() == "").sum())

    uqy = int(y.map(lambda s: _count_unbalanced_quotes(s, '"')).sum())
    uqes = int(es.map(lambda s: _count_unbalanced_quotes(s, '"')).sum())
    usqy = int(y.map(lambda s: _count_unbalanced_quotes(s, "'")).sum())
    usqes = int(es.map(lambda s: _count_unbalanced_quotes(s, "'")).sum())

    upy = int(y.map(lambda s: _count_unbalanced_pairs(s, "(", ")")).sum())
    upes = int(es.map(lambda s: _count_unbalanced_pairs(s, "(", ")")).sum())

    nly = int(y.str.contains("\n").sum())
    nles = int(es.str.contains("\n").sum())

    punct_heavy_y = int(y.map(lambda s: _punct_ratio(s) > 0.25).sum())
    punct_heavy_es = int(es.map(lambda s: _punct_ratio(s) > 0.25).sum())

    y_tok = y.map(_token_count)
    es_tok = es.map(_token_count)

    # Ratio stats (token-based)
    ratio = (y_tok / es_tok.replace(0, pd.NA)).astype("float").fillna(0.0)

    token_stats = {
        "yine": {
            "min": int(y_tok.min()),
            "p50": float(y_tok.median()),
            "p95": float(y_tok.quantile(0.95)),
            "max": int(y_tok.max())
        },
        "spanish": {
            "min": int(es_tok.min()),
            "p50": float(es_tok.median()),
            "p95": float(es_tok.quantile(0.95)),
            "max": int(es_tok.max())
        },
    }
    ratio_stats = {
        "min": float(ratio.min()),
        "p50": float(ratio.median()),
        "p95": float(ratio.quantile(0.95)),
        "max": float(ratio.max()),
        "zeros_due_to_empty": int((ratio == 0.0).sum())
    }

    # Char distributions (top 30) — helps spot weird symbols
    y_chars = Counter("".join(y.head(2000).tolist()))
    es_chars = Counter("".join(es.head(2000).tolist()))
    top_y = y_chars.most_common(30)
    top_es = es_chars.most_common(30)

    return AuditResult(
        total_rows=int(len(df)),
        empty_yine=empty_y,
        empty_spanish=empty_es,
        unbalanced_double_quotes_yine=uqy,
        unbalanced_double_quotes_spanish=uqes,
        unbalanced_single_quotes_yine=usqy,
        unbalanced_single_quotes_spanish=usqes,
        unbalanced_parens_yine=upy,
        unbalanced_parens_spanish=upes,
        rows_with_newlines_yine=nly,
        rows_with_newlines_spanish=nles,
        punctuation_heavy_yine=punct_heavy_y,
        punctuation_heavy_spanish=punct_heavy_es,
        token_len_stats=token_stats,
        length_ratio_stats=ratio_stats,
        char_top_yine=top_y,
        char_top_spanish=top_es
    )
