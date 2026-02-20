"""
Negative samples dataclass
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class NegativeSample:
    """
    Represents a negative sample for a Spanish-Yine pair.
    """
    pair_id: str
    source_text: str       # spanish
    target_text: str       # gold yine
    negative_text: str     # violated yine
    rule_id: str
    violation_type: str    # morph/morphophon/syntax/lexical
    severity: float
    metadata: Dict[str, Any]
    split: str             # train/dev/test
