"""
R8: Spanish determiner interference (final stable version)

Method:
Insert a Spanish determiner (configurable categories) at the start
of the Yine target sentence to simulate ES→Yine interference.
"""

from __future__ import annotations

from pathlib import Path
import random
import re
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


def _load_determiners(path: str, categories: list[str]) -> list[str]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    root = data.get("determinantes_espanol", {})
    collected: list[str] = []

    for cat in categories:
        section = root.get(cat)
        if not section:
            continue

        if isinstance(section, dict):
            for sub in section.values():
                if isinstance(sub, list):
                    collected.extend(sub)
        elif isinstance(section, list):
            collected.extend(section)

    return sorted(set(w.lower() for w in collected if isinstance(w, str)))


class R8SpanishDeterminerInjection(BaseGenerator):
    """
    R8: Spanish determiner interference (final stable version)
    """
    rule_id = "R8"
    violation_type = "lexical"

    def __init__(
        self,
        determiners_path: str,
        categories: list[str],
        severity: float = 0.6,
        injection_rate: float = 0.35,
        seed: int = 42,
    ):
        self.determiners = _load_determiners(determiners_path, categories)
        if not self.determiners:
            raise ValueError(
                f"[R8] Determiner list empty. Check YAML or categories: {categories}"
            )

        self.severity = float(severity)
        self.injection_rate = float(injection_rate)
        self.rng = random.Random(seed)

    def _contains_spanish_determiner(self, text: str) -> bool:
        lower = text.lower()
        for d in self.determiners:
            if re.search(rf"\b{re.escape(d)}\b", lower):
                return True
        return False

    def generate(
        self,
        *,
        pair_id: str,
        source_text: str,
        target_text: str,
        split: str,
    ):
        # probabilistic generation
        if self.rng.random() > self.injection_rate:
            return []

        # avoid double injection
        if self._contains_spanish_determiner(target_text):
            return []

        det = self.rng.choice(self.determiners)
        negative = f"{det} {target_text}".strip()

        sample = NegativeSample(
            pair_id=pair_id,
            source_text=source_text,
            target_text=target_text,
            negative_text=negative,
            rule_id=self.rule_id,
            violation_type=self.violation_type,
            severity=self.severity,
            metadata={
                "mutation": "prefix_injection",
                "inserted_token": det,
                "categories": self.determiners,
                "injection_rate": self.injection_rate,
            },
            split=split,
        )

        return [sample]
