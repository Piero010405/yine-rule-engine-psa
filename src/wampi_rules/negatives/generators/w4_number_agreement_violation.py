"""
W4: Verbal number agreement violation

Method:
Identify Wampis target sentences where a token contains a known verbal number marker.
Generate a negative by replacing that marker with a different number marker.

Example:
Target: "verb-plural-marker"
Negative: "verb-singular-marker"
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class W4NumberAgreementViolation(BaseGenerator):
    """
    W4 – Verbal number agreement violation in Wampis verbs
    """

    rule_id = "W4"
    violation_type = "morphological"

    def __init__(
        self,
        markers_path: str,
        severity: float = 0.9,
        seed: int = 42,
    ):
        self.severity = severity
        self.rng = random.Random(seed)

        data = yaml.safe_load(Path(markers_path).read_text(encoding="utf-8"))

        # Supports:
        # 1) plain YAML list
        # 2) dict with nested forms
        if isinstance(data, list):
            markers = data
        else:
            markers = data["wampis_number_markers"]["forms"]

        self.markers = sorted(
            [str(m).lower() for m in markers],
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

            for original_marker in self.markers:
                if original_marker not in token_lower:
                    continue

                replacement_candidates = [
                    m for m in self.markers
                    if m != original_marker
                ]
                if not replacement_candidates:
                    continue

                new_marker = self.rng.choice(replacement_candidates)

                # replace first occurrence inside token
                mutated_token = re.sub(
                    pattern=re.escape(original_marker),
                    repl=new_marker,
                    string=token,
                    count=1,
                    flags=re.IGNORECASE,
                )

                if mutated_token.lower() == token_lower:
                    continue

                # basic safety
                if len(mutated_token) < 3:
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
                        "mutation": "number_agreement_violation",
                        "original_marker": original_marker,
                        "new_marker": new_marker,
                        "original_token": token,
                        "mutated_token": mutated_token,
                    },
                    split=split,
                )

                return [sample]

        return []