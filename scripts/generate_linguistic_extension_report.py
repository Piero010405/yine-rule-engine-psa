"""
Generates quantitative report for linguistic rule-based negative generation.
Outputs figures in Figuras/
"""

import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

NEGATIVES_PATH = "data/processed/negatives/v1/negatives.parquet"
OUTPUT_DIR = Path("Figuras")
OUTPUT_DIR.mkdir(exist_ok=True)

# =============================
# LOAD DATA
# =============================

df = pd.read_parquet(NEGATIVES_PATH)

# =============================
# COUNTS BY RULE
# =============================

rule_counts = df["rule_id"].value_counts().sort_index()

plt.figure()
rule_counts.plot(kind="bar")
plt.title("Distribución de ejemplos negativos por regla morfológica")
plt.xlabel("Regla")
plt.ylabel("Número de ejemplos")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "negatives_by_rule.pdf")
plt.close()

# =============================
# COUNTS BY SPLIT
# =============================

split_counts = df["split"].value_counts()

plt.figure()
split_counts.plot(kind="bar")
plt.title("Distribución de ejemplos negativos por partición")
plt.xlabel("Split")
plt.ylabel("Número de ejemplos")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "negatives_by_split.pdf")
plt.close()

# =============================
# COUNTS BY SEVERITY
# =============================

if "severity" in df.columns:
    severity_counts = df["severity"].value_counts()

    plt.figure()
    severity_counts.plot(kind="bar")
    plt.title("Distribución de severidad de violaciones morfológicas")
    plt.xlabel("Severidad")
    plt.ylabel("Número de ejemplos")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "negatives_by_severity.pdf")
    plt.close()
else:
    severity_counts = {}

# =============================
# SAVE SUMMARY JSON
# =============================

summary = {
    "total_negatives": int(len(df)),
    "by_rule": rule_counts.to_dict(),
    "by_split": split_counts.to_dict(),
    "by_severity": severity_counts if isinstance(severity_counts, dict) else severity_counts.to_dict(),
}

with open("data/processed/negatives/linguistic_extension_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print("Linguistic extension report generated successfully.")
