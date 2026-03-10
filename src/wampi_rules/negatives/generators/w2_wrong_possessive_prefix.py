"""
W2: Incorrect possessive prefix substitution

Method:
Identify Wampis target sentences where a token starts with a known possessive prefix.
Generate a negative by replacing that prefix with a different possessive prefix.

Example:
Source: "Tu casa es grande."
Target: "amenu ..."
Negative: "winu ..."   [prefix "ame" replaced by "wi"]
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class W2WrongPossessivePrefix(BaseGenerator):
    """
    W2 – Incorrect possessive prefix substitution in Wampis nouns
    """

    rule_id = "W2"
    violation_type = "morphological"

    def __init__(
        self,
        prefixes_path: str,
        severity: float = 0.9,
        seed: int = 42,
    ):
        self.severity = severity
        self.rng = random.Random(seed)

        data = yaml.safe_load(Path(prefixes_path).read_text(encoding="utf-8"))

        # Supports:
        # 1) plain YAML list
        # 2) dict with nested forms
        if isinstance(data, list):
            prefixes = data
        else:
            prefixes = data["wampis_possessive_prefixes"]["forms"]

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
        tokens = re.findall(r"\b\w+\b", target_text, flags=re.UNICODE)

        for token in tokens:
            token_lower = token.lower()

            for original_pref in self.prefixes:
                if not token_lower.startswith(original_pref):
                    continue

                stem = token[len(original_pref):]

                # safety checks
                if len(stem) < 3:
                    continue

                replacement_candidates = [
                    p for p in self.prefixes
                    if p != original_pref
                ]
                if not replacement_candidates:
                    continue

                new_pref = self.rng.choice(replacement_candidates)
                mutated_token = new_pref + stem

                if mutated_token.lower() == token_lower:
                    continue

                negative_text = target_text.replace(token, mutated_token, 1)

                sample = NegativeSample(
                    pair_id=pair_id,
                    source_text=source_text,
                    target_text=target_text,
                    negative_text=negative_text,
                    rule_id=self.rule_id,
                    violation_type=self.violation_type,
                    severity=self.severity,
                    metadata={
                        "mutation": "wrong_possessive_prefix",
                        "original_prefix": original_pref,
                        "new_prefix": new_pref,
                        "original_token": token,
                        "mutated_token": mutated_token,
                    },
                    split=split,
                )

                return [sample]

        return []