"""
W1: Possessive prefix omission

Method:
Identify Wampis target sentences where a token starts with a known possessive prefix.
Generate a negative by removing the possessive prefix, leaving the noun stem intact.

Example:
Source: "Mi casa es grande."
Target: "winu ..."
Negative: "nu ..."   [possessive prefix "wi" removed]
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class W1PossessivePrefixOmission(BaseGenerator):
    """
    W1 – Omission of possessive prefix in Wampis nouns
    """

    rule_id = "W1"
    violation_type = "morphological"

    def __init__(
        self,
        prefixes_path: str,
        severity: float = 0.95,
        seed: int = 42,
    ):
        self.severity = severity
        self.rng = random.Random(seed)

        data = yaml.safe_load(Path(prefixes_path).read_text(encoding="utf-8"))

        # Supports either:
        # 1) plain YAML list: ["wi", "ame", "ni"]
        # 2) dict format:
        #    wampis_possessive_prefixes:
        #      forms: ["wi", "ame", "ni"]
        if isinstance(data, list):
            prefixes = data
        else:
            prefixes = data["wampis_possessive_prefixes"]["forms"]

        # Order by length descending to avoid partial matching issues
        self.prefixes = sorted(
            [str(p).lower() for p in prefixes],
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
        """
        Return one negative sample at most.
        """
        # Tokenize target while keeping original text for replacement
        tokens = re.findall(r"\b\w+\b", target_text, flags=re.UNICODE)

        for token in tokens:
            token_lower = token.lower()

            for pref in self.prefixes:
                if not token_lower.startswith(pref):
                    continue

                stem = token[len(pref):]

                # basic safety checks
                if len(stem) < 3:
                    continue

                # avoid deleting the whole token or producing same token
                if stem.lower() == token_lower:
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
                        "mutation": "possessive_prefix_omission",
                        "removed_prefix": pref,
                        "original_token": token,
                        "mutated_token": stem,
                    },
                    split=split,
                )

                return [sample]

        return []