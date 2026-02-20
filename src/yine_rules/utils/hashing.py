"""
Utilities for hashing and generating unique IDs for Spanish-Yine pairs.
"""
from __future__ import annotations
import hashlib

def stable_hash(text: str, algo: str = "sha1") -> str:
    """Generates a stable hash for the given text using the specified algorithm."""
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def make_pair_id(spanish: str, yine: str, source: str, algo: str = "sha1") -> str:
    """Generates a unique ID for a Spanish-Yine pair based on the input strings."""
    # separador explícito para evitar colisiones
    key = f"{spanish}\n||\n{yine}\n||\n{source}"
    return stable_hash(key, algo=algo)
