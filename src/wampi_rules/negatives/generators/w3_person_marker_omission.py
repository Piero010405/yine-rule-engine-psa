"""
W3: Verbal person marker omission

Method:
Identify Wampis target sentences where a token ends with a known verbal person marker.
Generate a negative by removing that suffix, leaving the verb stem intact.

Example:
Source: "Yo seré."
Target: "atatjai"
Negative: "atat"   [person marker "jai" removed]
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class W3PersonMarkerOmission(BaseGenerator):
    """
    W3 – Omission of verbal person marker in Wampis verbs
    """

    rule_id = "W3"
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
            markers = data["wampis_person_markers"]["forms"]

        # Longest first to avoid partial suffix matches
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

            for marker in self.markers:
                if not token_lower.endswith(marker):
                    continue

                stem = token[:-len(marker)]

                # safety checks
                if len(stem) < 3:
                    continue

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
                        "mutation": "person_marker_omission",
                        "removed_marker": marker,
                        "original_token": token,
                        "mutated_token": stem,
                    },
                    split=split,
                )

                return [sample]

        return []