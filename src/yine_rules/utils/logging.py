"""
Utility functions for logging
"""
from __future__ import annotations
import logging
import logging.config
from pathlib import Path
import yaml

def setup_logging(logging_cfg_path: str | None = None) -> None:
    """
    Setup logging configuration.
    
    :param logging_cfg_path: Path to the logging configuration YAML file
    :type logging_cfg_path: str | None
    """
    if logging_cfg_path and Path(logging_cfg_path).exists():
        with open(logging_cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        # Ensure parent directory exists for file handler
        file_handler = cfg.get("handlers", {}).get("file", {})
        filename = file_handler.get("filename")
        if filename:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
