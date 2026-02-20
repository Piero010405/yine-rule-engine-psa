"""
Freeze positive dataset
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import hashlib
import pandas as pd

from yine_rules.utils.hashing import make_pair_id
from yine_rules.io.writers import write_yaml

@dataclass
class FreezeConfig:
    """Configuration for freezing the positive dataset."""
    input_cleaned_parquet: str
    output_positive_parquet: str
    output_manifest_yaml: str
    col_source: str
    col_target: str
    col_source_text: str
    algo: str
    id_fields: list[str]

def sha256_file(path: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def freeze_positive(cfg: FreezeConfig) -> dict:
    """
    Freeze the positive dataset, generating pair IDs, and writing the output parquet and manifest.
    """
    in_path = Path(cfg.input_cleaned_parquet)
    if not in_path.exists():
        raise FileNotFoundError(f"Missing cleaned parquet: {in_path}")

    df = pd.read_parquet(in_path)

    for c in [cfg.col_source_text, cfg.col_target, cfg.col_source]:
        if c not in df.columns:
            raise ValueError(f"Missing column '{c}'. Found: {list(df.columns)}")

    # pair_id estable
    df = df.copy()
    df["pair_id"] = df.apply(
        lambda r: make_pair_id(
            spanish=str(r[cfg.col_source_text]),
            yine=str(r[cfg.col_target]),
            source=str(r[cfg.col_source]),
            algo=cfg.algo,
        ),
        axis=1
    )

    # reordenar columnas
    df = df[["pair_id", cfg.col_source_text, cfg.col_target, cfg.col_source]]

    out_path = Path(cfg.output_positive_parquet)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)

    manifest = {
        "name": "positive_corpus.v1",
        "path": str(out_path).replace("\\", "/"),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "hash_sha256": sha256_file(str(out_path)),
        "id_algo": cfg.algo,
        "id_fields": cfg.id_fields,
    }

    write_yaml(cfg.output_manifest_yaml, manifest)
    return manifest
