"""
Structural cleanup, such as collapsing repeated quotes and removing orphan quotes or parentheses.
"""
from __future__ import annotations
import pandas as pd
import regex as re

def clean_bible_structural_artifacts(
    df: pd.DataFrame,
    col_text: str,
    col_source: str,
    bible_label: str = "bible"
) -> tuple[pd.DataFrame, dict]:
    """
    Clean structural artifacts in Bible verses, such as collapsing repeated quotes and removing 
    orphan quotes or parentheses.
    
    :param df: The DataFrame to clean
    :type df: pd.DataFrame
    :param col_text: The name of the column containing the text to clean
    :type col_text: str
    :param col_source: The name of the column containing the source label
    :type col_source: str
    :param bible_label: The value of the source label for Bible verses
    :type bible_label: str
    :return: The cleaned DataFrame and a summary of changes made
    :rtype: tuple[DataFrame, dict]
    """

    out = df.copy()
    summary = {
        "double_quote_collapsed": 0,
        "leading_orphan_quote_removed": 0,
        "trailing_orphan_quote_removed": 0,
        "leading_orphan_paren_removed": 0,
        "trailing_orphan_paren_removed": 0
    }

    def fix_text(text: str) -> str:
        original = text

        # Collapse repeated quotes
        new = re.sub(r'"+', '"', text)
        if new != text:
            summary["double_quote_collapsed"] += 1
        text = new

        # Leading orphan quote
        if text.startswith('"') and text.count('"') == 1:
            text = text[1:]
            summary["leading_orphan_quote_removed"] += 1

        # Trailing orphan quote
        if text.endswith('"') and text.count('"') == 1:
            text = text[:-1]
            summary["trailing_orphan_quote_removed"] += 1

        # Leading orphan parenthesis
        if text.startswith("(") and text.count("(") == 1 and text.count(")") == 0:
            text = text[1:]
            summary["leading_orphan_paren_removed"] += 1

        # Trailing orphan parenthesis
        if text.endswith(")") and text.count(")") == 1 and text.count("(") == 0:
            text = text[:-1]
            summary["trailing_orphan_paren_removed"] += 1

        return text.strip()

    mask = out[col_source] == bible_label
    out.loc[mask, col_text] = out.loc[mask, col_text].astype(str).apply(fix_text)

    return out, summary
