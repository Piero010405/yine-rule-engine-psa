"""
Generates preprocessing report for corpus v1.
Compatible with columns: yine / spanish
Outputs figures directly into Figuras/
"""

import json
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# =============================
# CONFIG
# =============================

POSITIVE_PATH = "data/processed/positive/positive_corpus.v1.parquet"
CLEAN_AUDIT_PATH = "data/processed/reports/audit_cleaned.json"
SPLIT_PATH = "data/processed/splits/split_v1.json"

OUTPUT_FIG_DIR = Path("Figuras")
OUTPUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

# =============================
# LOAD DATA
# =============================

df = pd.read_parquet(POSITIVE_PATH)

with open(CLEAN_AUDIT_PATH, "r", encoding="utf-8") as f:
    audit = json.load(f)

with open(SPLIT_PATH, "r", encoding="utf-8") as f:
    split = json.load(f)

# =============================
# TOKEN LENGTHS
# =============================

if "yine" not in df.columns or "spanish" not in df.columns:
    raise ValueError("Expected columns 'yine' and 'spanish' not found in parquet.")

df["len_yine"] = df["yine"].astype(str).str.split().apply(len)
df["len_spanish"] = df["spanish"].astype(str).str.split().apply(len)

# =============================
# SUMMARY STATS
# =============================

summary = {
    "total_rows_final": len(df),
    "yine_mean": round(df["len_yine"].mean(), 2),
    "spanish_mean": round(df["len_spanish"].mean(), 2),
    "yine_median": int(df["len_yine"].median()),
    "spanish_median": int(df["len_spanish"].median()),
    "yine_std": round(df["len_yine"].std(), 2),
    "spanish_std": round(df["len_spanish"].std(), 2),
    "yine_min": int(df["len_yine"].min()),
    "spanish_min": int(df["len_spanish"].min()),
    "yine_max": int(df["len_yine"].max()),
    "spanish_max": int(df["len_spanish"].max()),
}

with open("data/processed/positive/stats_v1.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

# =============================
# HISTOGRAM YINE
# =============================

plt.figure()
sns.histplot(df["len_yine"], bins=40)
plt.title("Distribución de longitud - Yine (Corpus v1)")
plt.xlabel("Número de tokens")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig(OUTPUT_FIG_DIR / "hist_yine_v1.pdf")
plt.close()

# =============================
# HISTOGRAM SPANISH
# =============================

plt.figure()
sns.histplot(df["len_spanish"], bins=40)
plt.title("Distribución de longitud - Español (Corpus v1)")
plt.xlabel("Número de tokens")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig(OUTPUT_FIG_DIR / "hist_spanish_v1.pdf")
plt.close()

# =============================
# BOXPLOT COMPARISON
# =============================

plt.figure()
sns.boxplot(data=df[["len_yine", "len_spanish"]])
plt.title("Comparación de longitudes - Yine vs Español (v1)")
plt.tight_layout()
plt.savefig(OUTPUT_FIG_DIR / "boxplot_lengths_v1.pdf")
plt.close()

# =============================
# SPLIT DISTRIBUTION
# =============================

split_counts = {
    "train": len(split["train_ids"]),
    "dev": len(split["dev_ids"]),
    "test": len(split["test_ids"]),
}

plt.figure()
plt.bar(split_counts.keys(), split_counts.values())
plt.title("Distribución de partición del corpus (v1)")
plt.xlabel("Split")
plt.ylabel("Número de pares")
plt.tight_layout()
plt.savefig(OUTPUT_FIG_DIR / "split_distribution_v1.pdf")
plt.close()

# =============================
# AUDIT ANOMALIES BARPLOT
# =============================

anomaly_counts = {
    "Unbalanced double quotes (Yine)": audit["unbalanced_double_quotes_yine"],
    "Unbalanced double quotes (Spanish)": audit["unbalanced_double_quotes_spanish"],
    "Unbalanced single quotes (Yine)": audit["unbalanced_single_quotes_yine"],
    "Unbalanced single quotes (Spanish)": audit["unbalanced_single_quotes_spanish"],
}

plt.figure(figsize=(8,5))
plt.barh(list(anomaly_counts.keys()), list(anomaly_counts.values()))
plt.title("Anomalías estructurales detectadas (v1)")
plt.tight_layout()
plt.savefig(OUTPUT_FIG_DIR / "structural_anomalies_v1.pdf")
plt.close()

print("Preprocessing report generated successfully.")
