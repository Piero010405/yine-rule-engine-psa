"""
Base class for negative sample generators.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from yine_rules.negatives.types import NegativeSample

class BaseGenerator(ABC):
    """
    Base class for negative sample generators. Each generator implements a specific rule
    """
    rule_id: str
    violation_type: str
    severity: float

    @abstractmethod
    def generate(self,
                *,
                pair_id: str,
                source_text: str,
                target_text: str,
                split: str
                ) -> List[NegativeSample]:
        """
        Return 0..k negative samples for this (source,target).
        If rule doesn't apply, return [].
        """
        raise NotImplementedError
