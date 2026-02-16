"""
Pipeline for conditioning data
"""
from __future__ import annotations
from pathlib import Path
import logging

from yine_rules.preprocessing.audit import run_audit
from yine_rules.preprocessing.normalize import normalize_dataframe_text
from yine_rules.preprocessing.structural_cleanup import clean_bible_structural_artifacts
from yine_rules.preprocessing.filter import apply_filters
from yine_rules.preprocessing.alignment_checks import find_alignment_suspects
from yine_rules.io.read_corpus import read_full_corpus_csv
from yine_rules.io.write_outputs import write_parquet, write_csv
from yine_rules.utils.reproducibility import stable_hash_dict, dataframe_fingerprint, write_json

log = logging.getLogger("yine_rules.preprocessing")

def run_conditioning(settings: dict) -> None:
    """
    Run the conditioning pipeline on a dataset.

    :param settings: The settings dictionary containing paths, dataset, normalization, filtering,
    reproducibility, and alignment checks configurations.
    :type settings: dict
    """
    paths = settings["paths"]
    ds = settings["dataset"]
    norm = settings["normalization"]
    filt = settings["filtering"]
    repro = settings["reproducibility"]
    checks = settings["alignment_checks"]

    # Ensure dirs
    Path(paths["interim_dir"]).mkdir(parents=True, exist_ok=True)
    Path(paths["reports_dir"]).mkdir(parents=True, exist_ok=True)
    Path(paths["suspects_dir"]).mkdir(parents=True, exist_ok=True)

    col_y = ds["columns"]["yine"]
    col_es = ds["columns"]["spanish"]
    col_src = ds["columns"]["source"]

    # Load raw
    log.info("Loading raw corpus: %s", paths["raw_csv"])
    df = read_full_corpus_csv(
        paths["raw_csv"],
        col_y,
        col_es,
        col_src,
        encoding=ds.get("encoding", "utf-8")
    )

    # Fingerprint + config hash (provenance)
    cfg_hash = stable_hash_dict(settings)
    fp = dataframe_fingerprint(
        df,
        [col_y, col_es, col_src],
        max_rows=int(repro.get("fingerprint_rows", 5000))
    )
    provenance = {"config_sha256": cfg_hash, "dataset_fingerprint_sha256": fp}
    write_json(Path(paths["reports_dir"]) / "provenance.json", provenance)

    # AUDIT pre
    pre_audit = run_audit(df, col_y, col_es)
    write_json(Path(paths["reports_dir"]) / "audit_raw.json", pre_audit.__dict__)
    log.info("Audit raw saved.")

    # NORMALIZE (non-destructive)
    df_norm, norm_summary = normalize_dataframe_text(
        df=df,
        text_cols=[col_y, col_es],
        unicode_form=norm["unicode_form"],
        trim_whitespace=bool(norm["trim_whitespace"]),
        collapse_spaces=bool(norm["collapse_spaces"]),
        normalize_newlines=bool(norm["normalize_newlines"]),
        replace_tabs=bool(norm["replace_tabs"])
    )
    write_json(Path(paths["reports_dir"]) / "normalization_summary.json", norm_summary)
    log.info("Normalization done. Changed rows: %s", norm_summary["changed_rows"])

    # STRUCTURAL CLEANUP (bible-specific)
    df_cleaned_struct, cleanup_summary = clean_bible_structural_artifacts(
        df_norm,
        col_text=col_y,
        col_source=col_src
    )

    write_json(Path(paths["reports_dir"]) / "structural_cleanup_summary.json", cleanup_summary)
    log.info("Structural cleanup done.")

    df_norm = df_cleaned_struct
    
    # FILTER
    df_filt, filt_report, removed_df = apply_filters(
        df=df_norm,
        col_yine=col_y,
        col_spanish=col_es,
        drop_empty=bool(filt["drop_empty"]),
        min_chars=int(filt["min_chars"]),
        min_tokens=int(filt["min_tokens"]),
        max_tokens=int(filt["max_tokens"]),
        length_ratio_enabled=bool(filt["length_ratio"]["enabled"]),
        min_ratio=float(filt["length_ratio"]["min_ratio"]),
        max_ratio=float(filt["length_ratio"]["max_ratio"]),
        dedup_enabled=bool(filt["duplicates"]["enabled"]),
        dedup_subset=list(filt["duplicates"]["subset"])
    )
    write_json(Path(paths["reports_dir"]) / "filter_report.json", filt_report)
    if not removed_df.empty:
        write_csv(removed_df, str(Path(paths["reports_dir"]) / "removed_rows.csv"))
    log.info("Filtering done. Rows: %s -> %s", filt_report["start_rows"], filt_report["end_rows"])

    # Alignment checks (suspects, non-destructive)
    if checks.get("enabled", True):
        suspects_df = find_alignment_suspects(df_filt, col_y, col_es)
        write_csv(suspects_df, str(Path(paths["suspects_dir"]) / "alignment_suspects.csv"))
        log.info("Alignment suspects saved: %s", len(suspects_df))

    # AUDIT post
    post_audit = run_audit(df_filt, col_y, col_es)
    write_json(Path(paths["reports_dir"]) / "audit_cleaned.json", post_audit.__dict__)
    log.info("Audit cleaned saved.")

    # Export cleaned
    write_parquet(df_filt, paths["cleaned_parquet"])
    write_csv(df_filt, paths["cleaned_csv"])
    log.info("Cleaned corpus exported: %s", paths["cleaned_parquet"])
