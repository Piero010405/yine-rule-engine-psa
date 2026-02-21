"""
R4:  Omission of obligatory Possessed Status Suffix (PSSD)

Method:
Identify Yine target sentences where a token has both a possessive prefix and a PSSD suffix.
Generate a negative by removing the PSSD suffix, leaving the possessive prefix intact.
Example:
Source: "Mi casa es grande." (My house is big.)
Target: "N-mi-kasa-Ø es grande." (My house is big.)
Negative: "N-mi-kasa es grande." (My house is big.) [PSSD suffix "-Ø" removed]
"""
from __future__ import annotations

import re
from pathlib import Path
import random
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


class R4PSSDOmission(BaseGenerator):
    """
    R4 – Omission of obligatory Possessed Status Suffix (PSSD)
    """

    rule_id = "R4"
    violation_type = "morphological"

    def __init__(
        self,
        posesivos_path: str,
        prefixes_path: str,
        pssd_path: str,
        severity: float = 0.9,
        seed: int = 42,
    ):
        self.severity = severity
        self.rng = random.Random(seed)

        # Load Spanish possessives
        posesivos_data = yaml.safe_load(Path(posesivos_path).read_text(encoding="utf-8"))
        self.posesivos = set(w.lower() for w in posesivos_data["posesivos_espanol"]["formas"])

        # Load prefixes
        prefixes_data = yaml.safe_load(Path(prefixes_path).read_text(encoding="utf-8"))
        self.prefixes = [
            str(p) for p in prefixes_data["possessive_prefixes_yine"]["observable_prefixes"]
        ]

        # Load PSSD suffixes
        pssd_data = yaml.safe_load(Path(pssd_path).read_text(encoding="utf-8"))
        self.pssd = pssd_data["pssd"]["suffixes"]

    def generate(self, *, pair_id: str, source_text: str, target_text: str, split: str):

        source_lower = source_text.lower()

        # Trigger: Spanish possessive must appear
        if not any(re.search(rf"\b{re.escape(p)}\b", source_lower) for p in self.posesivos):
            return []

        tokens = re.findall(r"\b\w+\b", target_text)
        generated = []

        for token in tokens:

            for pref in self.prefixes:
                if token.startswith(pref):

                    for suf in self.pssd:
                        if token.endswith(suf):

                            root = token[:-len(suf)]

                            if len(root) < 3:
                                continue

                            negative = target_text.replace(token, root, 1)

                            generated.append(
                                NegativeSample(
                                    pair_id=pair_id,
                                    source_text=source_text,
                                    target_text=target_text,
                                    negative_text=negative,
                                    rule_id=self.rule_id,
                                    violation_type=self.violation_type,
                                    severity=self.severity,
                                    metadata={
                                        "mutation": "pssd_omission",
                                        "removed_suffix": suf,
                                        "prefix": pref,
                                        "original_token": token,
                                    },
                                    split=split,
                                )
                            )

                            return generated  # one mutation per sentence

        return []
