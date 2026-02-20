"""
Registry for negative sample generators.
"""
from __future__ import annotations
from typing import Dict
from yine_rules.negatives.base_generator import BaseGenerator

_REGISTRY: Dict[str, BaseGenerator] = {}

def register(gen: BaseGenerator) -> None:
    """
    Register a negative sample generator.
    """
    _REGISTRY[gen.rule_id] = gen

def get(rule_id: str) -> BaseGenerator:
    """
    Get a registered negative sample generator by rule_id.
    """
    if rule_id not in _REGISTRY:
        raise KeyError(f"Rule generator not registered: {rule_id}")
    return _REGISTRY[rule_id]

def available() -> list[str]:
    """
    List available rule generators.
    """
    return sorted(_REGISTRY.keys())
