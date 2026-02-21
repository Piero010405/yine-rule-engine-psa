"""
R7: Gender agreement violation in adjective modifiers.

Method:
Flip agreement suffix (lu↔lo, tu↔to) only when the adjective
appears inside NP context (adjacent to noun-like token).
"""

from __future__ import annotations

from pathlib import Path
import random
import re
import yaml

from yine_rules.negatives.base_generator import BaseGenerator
from yine_rules.negatives.types import NegativeSample


TOKEN_RE = re.compile(r"\b[a-zñáéíóúü]+\b", re.IGNORECASE)

STOPWORDS_YINE = {
    "wa", "ga", "gi", "wane", "wale",
    "satu", "sato", "pa"
}

VERBAL_SUFFIXES = ("ta", "na", "kalu", "luwa", "tka")


def looks_like_noun(tok: str) -> bool:
    """Heuristic to check if a token looks like a noun (for NP context detection)."""
    if tok in STOPWORDS_YINE:
        return False
    if len(tok) < 3:
        return False
    if tok.endswith(VERBAL_SUFFIXES):
        return False
    return True


class R7GenderAgreementFlip(BaseGenerator):
    """Generator for R7"""

    rule_id = "R7"
    violation_type = "morphological"

    def __init__(
        self,
        adjectives_path: str,
        suffixes_path: str,
        severity: float = 0.9,
        seed: int = 42,
    ):
        self.severity = float(severity)
        self.rng = random.Random(seed)

        # Load adjective whitelist
        adj_data = yaml.safe_load(Path(adjectives_path).read_text(encoding="utf-8"))
        self.adjectives = set(
            w.lower() for w in adj_data["r7_adjectives_seed"]["adjectives"]
        )

        # Load suffix pairs
        suf_data = yaml.safe_load(Path(suffixes_path).read_text(encoding="utf-8"))
        self.flip_map = {}
        self.enabled_suffixes = set()

        for p in suf_data["r7_agreement_suffixes"]["pairs"]:
            if not p.get("enabled", True):
                continue
            masc = p["masc"].lower()
            fem = p["fem"].lower()
            self.flip_map[masc] = fem
            self.flip_map[fem] = masc
            self.enabled_suffixes.add(masc)
            self.enabled_suffixes.add(fem)

    def generate(
        self,
        *,
        pair_id: str,
        source_text: str,
        target_text: str,
        split: str,
    ):

        # Tokenize preserving original tokens (not lowercased)
        original_tokens = re.findall(r"\b[a-zñáéíóúü]+\b", target_text, flags=re.IGNORECASE)
        if not original_tokens:
            return []

        lowered_tokens = [t.lower() for t in original_tokens]

        for i, tok_lower in enumerate(lowered_tokens):

            if tok_lower not in self.adjectives:
                continue

            hit_suffix = None
            for suf in self.enabled_suffixes:
                if tok_lower.endswith(suf) and len(tok_lower) > len(suf) + 1:
                    hit_suffix = suf
                    break

            if not hit_suffix:
                continue

            left = lowered_tokens[i - 1] if i > 0 else None
            right = lowered_tokens[i + 1] if i < len(lowered_tokens) - 1 else None

            # NP structural check
            in_np = False
            if right and looks_like_noun(right):
                in_np = True
            elif left and looks_like_noun(left):
                in_np = True

            if not in_np:
                continue

            # Flip suffix
            flipped_lower = tok_lower[:-len(hit_suffix)] + self.flip_map[hit_suffix]

            # Preserve original casing
            original_tok = original_tokens[i]
            if original_tok[0].isupper():
                flipped = flipped_lower.capitalize()
            else:
                flipped = flipped_lower

            # Reconstruct text safely
            def replace_nth_word(text, index, new_word):
                words = list(re.finditer(r"\b[a-zñáéíóúü]+\b", text, flags=re.IGNORECASE))
                if index >= len(words):
                    return text
                match = words[index]
                start, end = match.span()
                return text[:start] + new_word + text[end:]

            negative = replace_nth_word(target_text, i, flipped)

            # Safety check (avoid identical outputs)
            if negative == target_text:
                return []

            sample = NegativeSample(
                pair_id=pair_id,
                source_text=source_text,
                target_text=target_text,
                negative_text=negative,
                rule_id=self.rule_id,
                violation_type=self.violation_type,
                severity=self.severity,
                metadata={
                    "mutation": "gender_agreement_flip",
                    "original_token": original_tok,
                    "flipped_token": flipped,
                    "suffix_changed": hit_suffix,
                },
                split=split,
            )

            return [sample]

        return []
