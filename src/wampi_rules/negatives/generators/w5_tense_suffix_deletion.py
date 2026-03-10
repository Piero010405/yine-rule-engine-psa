"""
W5: Verbal tense suffix deletion

Method:
Identify Wampis target sentences where a token ends with a known tense/aspect suffix.
Generate a negative by removing that suffix, leaving the verb stem intact.

Example:
Target: "atatjai"
Negative: "atat"
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class W5TenseSuffixDeletion(BaseGenerator):
    """
    W5 – Deletion of tense/aspect suffix in Wampis verbs
    """

    rule_id = "W5"
    violation_type = "morphological"

    def __init__(
        self,
        suffixes_path: str,
        severity: float = 0.85,
        seed: int = 42,
    ):
        self.severity = severity
        self.rng = random.Random(seed)

        data = yaml.safe_load(Path(suffixes_path).read_text(encoding="utf-8"))

        if isinstance(data, list):
            suffixes = data
        else:
            suffixes = data["wampis_tense_suffixes"]["forms"]

        # ordenar por longitud para evitar conflictos
        self.suffixes = sorted(
            [str(s).lower() for s in suffixes],
            key=len,
            reverse=True,
        )

    def generate(
        self,
        *,
        pair_id: str,
        source_text: str,
        target_text: str,
        split: str,
    ):
        tokens = re.findall(r"\b\w+\b", target_text, flags=re.UNICODE)

        for token in tokens:
            token_lower = token.lower()

            for suffix in self.suffixes:
                if not token_lower.endswith(suffix):
                    continue

                stem = token[:-len(suffix)]

                # safety checks
                if len(stem) < 3:
                    continue

                negative_text = target_text.replace(token, stem, 1)

                sample = NegativeSample(
                    pair_id=pair_id,
                    source_text=source_text,
                    target_text=target_text,
                    negative_text=negative_text,
                    rule_id=self.rule_id,
                    violation_type=self.violation_type,
                    severity=self.severity,
                    metadata={
                        "mutation": "tense_suffix_deletion",
                        "removed_suffix": suffix,
                        "original_token": token,
                        "mutated_token": stem,
                    },
                    split=split,
                )

                return [sample]

        return []