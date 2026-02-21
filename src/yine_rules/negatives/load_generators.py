"""
Dynamic loader for negative generators.
"""

from __future__ import annotations
from pathlib import Path
import yaml

from yine_rules.negatives.registry import register

# Import all generator classes here
from yine_rules.negatives.generators.r4_pssd_omission import R4PSSDOmission
from yine_rules.negatives.generators.r8_spanish_determiner import R8SpanishDeterminerInjection


# Central rule → class mapping
GENERATOR_CLASSES = {
    "R4": R4PSSDOmission,
    "R8": R8SpanishDeterminerInjection,
}


def load_generators_from_rules_yaml(rules_yaml_path: str, seed: int = 42) -> list[str]:
    """
    Load generators from a YAML file.
    """

    data = yaml.safe_load(Path(rules_yaml_path).read_text(encoding="utf-8"))
    rules = data.get("rules", [])

    if not rules:
        raise ValueError(f"No rules found in: {rules_yaml_path}")

    loaded = []

    for r in rules:
        if not r.get("enabled", True):
            continue

        rid = r.get("rule_id")

        if rid not in GENERATOR_CLASSES:
            raise ValueError(f"Generator class not registered for rule: {rid}")

        cls = GENERATOR_CLASSES[rid]

        # ---------- R4 ----------
        if rid == "R4":
            gen = cls(
                posesivos_path="resources/lexicons/posesivos_es.yaml",
                prefixes_path="resources/lexicons/possessive_prefixes_yine.yaml",
                pssd_path="resources/lexicons/pssd_suffixes.yaml",
                severity=r.get("severity", 0.9),
                seed=seed,
            )

        # ---------- R8 ----------
        elif rid == "R8":
            gen_cfg = r.get("generation", {})

            gen = cls(
                determiners_path=r["resources_required"]["determiners_es"],
                categories=gen_cfg.get("categories", []),
                severity=r.get("severity", 0.6),
                injection_rate=gen_cfg.get("injection_rate", 0.35),
                seed=seed,
            )

        else:
            raise ValueError(f"Unhandled rule_id: {rid}")

        register(gen)
        loaded.append(rid)

    return loaded
