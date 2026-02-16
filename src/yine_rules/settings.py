"""
Settings management for the Yine Rule Engine.
This module provides a Settings class that can load configuration from a YAML file
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class Settings:
    """
    Settings class
    
    :var Example: 
        >>> from yine_rules.settings import Settings
        >>> settings = Settings.load("configs/default.yaml")
    """
    config: dict

    @staticmethod
    def load(path: str | Path) -> "Settings":
        """
        Load settings from a YAML file.
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return Settings(config=cfg)

    def p(self, key_path: str, default=None):
        """
        Get nested config keys using dot notation.
        Example: p("paths.raw_csv")
        """
        node = self.config
        for key in key_path.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node
