"""
R6: Determiner-Noun order violation (NP simple)

Transforms:
DET + N  →  N + DET

Applies only when:
- Spanish side contains article (defined or indefinite)
- Yine side contains satu|sato + N
- N length >= 3
"""

from __future__ import annotations

from pathlib import Path
import random
import re
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


def _load_yine_dets(path: str) -> set[str]:
    """
    Cargamos los determinantes de Yine desde el YAML.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return set(data["yine_determiners"]["articles"])


def _load_spanish_articles(path: str) -> set[str]:
    """
    Cargamos los artículos definidos e indefinidos del español desde el YAML.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    arts = data["determinantes_espanol"]["articulos"]
    return set(
        arts["definidos"] +
        arts["indefinidos"]
    )


class R6DeterminantSwap(BaseGenerator):
    """
    R6: NP determiner swap (syntactic violation)
    """

    rule_id = "R6"
    violation_type = "syntactic"

    def __init__(
        self,
        yine_dets_path: str,
        spanish_dets_path: str,
        severity: float = 0.8,
        seed: int = 42,
    ):
        self.yine_dets = _load_yine_dets(yine_dets_path)
        self.spanish_articles = _load_spanish_articles(spanish_dets_path)
        self.severity = float(severity)
        self.rng = random.Random(seed)

    def _spanish_has_article(self, text: str) -> bool:
        lower = text.lower()
        for art in self.spanish_articles:
            if re.search(rf"\b{re.escape(art)}\b", lower):
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

        if not self._spanish_has_article(source_text):
            return []

        tokens = re.findall(r"\b[a-zñ]+\b", target_text.lower())

        for i in range(len(tokens) - 1):
            t0 = tokens[i]
            t1 = tokens[i + 1]

            if t0 in self.yine_dets and len(t1) >= 3:

                # reconstruimos texto original respetando mayúsculas
                pattern = re.compile(rf"\b{t0}\s+{t1}\b", re.IGNORECASE)

                def swap(match):
                    original = match.group(0)
                    parts = original.split()
                    return f"{parts[1]} {parts[0]}"

                negative_text = pattern.sub(swap, target_text, count=1)

                sample = NegativeSample(
                    pair_id=pair_id,
                    source_text=source_text,
                    target_text=target_text,
                    negative_text=negative_text,
                    rule_id=self.rule_id,
                    violation_type=self.violation_type,
                    severity=self.severity,
                    metadata={
                        "mutation": "np_det_swap",
                        "original_order": f"{t0} {t1}",
                        "swapped_order": f"{t1} {t0}",
                    },
                    split=split,
                )

                return [sample]

        return []
