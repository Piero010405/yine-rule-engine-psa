"""
Load negative generators from rules YAML config.
"""

from __future__ import annotations
from pathlib import Path
import yaml

from yine_rules.negatives.registry import register
from yine_rules.negatives.generators.r8_spanish_determiner import (
    R8SpanishDeterminerInjection,
)


def load_generators_from_rules_yaml(rules_yaml_path: str, seed: int = 42) -> list[str]:
    """Load negative generators from rules YAML config."""
    data = yaml.safe_load(Path(rules_yaml_path).read_text(encoding="utf-8"))
    rules = data.get("rules", [])

    if not rules:
        raise ValueError(f"No rules found in: {rules_yaml_path}")

    loaded = []

    for r in rules:
        if not r.get("enabled", True):
            continue

        rid = r.get("rule_id")

        if rid == "R8":
            det_path = r["resources_required"]["determiners_es"]
            sev = r.get("severity", 0.6)

            gen_cfg = r.get("generation", {})
            categories = gen_cfg.get("categories", [])
            inj_rate = gen_cfg.get("injection_rate", 0.35)

            generator = R8SpanishDeterminerInjection(
                determiners_path=det_path,
                categories=categories,
                severity=sev,
                injection_rate=inj_rate,
                seed=seed,
            )

            register(generator)
            loaded.append("R8")

    return loaded
