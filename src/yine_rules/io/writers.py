"""
Write outputs to disk
"""
from __future__ import annotations
import json
from pathlib import Path
import yaml

def ensure_parent(path: str | Path) -> Path:
    """
    Ensure that the parent directory of the given path exists, creating it if necessary.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def write_json(path: str | Path, obj) -> None:
    """
    Write a Python object to a JSON file, ensuring that the parent directory exists.
    """
    p = ensure_parent(path)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def write_yaml(path: str | Path, obj) -> None:
    """
    Write a Python object to a YAML file, ensuring that the parent directory exists.
    """
    p = ensure_parent(path)
    p.write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), encoding="utf-8")
