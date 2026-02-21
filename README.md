# YINE-RULE-ENGINE-PSA

Rule-based negative sample generator for Yine–Spanish parallel corpus

Designed for controlled linguistic contrastive learning in Machine Translation.

## 👤 Author

**D'Alessandro del Piero Sarmiento Ayala** Software Engineering Student  
Universidad San Ignacio de Loyola (USIL)  
Peru

---

## 📌 Project Overview

`yine-rule-engine-psa` is a deterministic rule-based negative sample generator built over a cleaned Yine–Spanish parallel corpus.

**The objective is to:**

* Generate linguistically grounded negative examples.
* Introduce controlled morphological, syntactic and lexical violations.
* Build contrastive datasets for Machine Translation research.
* Enable reproducible experimentation with rule-based perturbations.

**This repository implements:**

* Corpus conditioning pipeline.
* Deterministic ID freezing.
* Reproducible data splits.
* Ratio-controlled negative sampling engine.
* Linguistically motivated rule generators (R4, R6, R7, R8).

---

## 🧱 Project Structure

```text
yine-rule-engine/
│
├── configs/
│   ├── default.yaml
│   └── experiments/
│       ├── dataset_v1.yaml
│       └── negatives_v1.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── resources/
│   └── lexicons/
│
├── src/yine_rules/
│   ├── preprocessing/
│   ├── datasets/
│   ├── negatives/
│   │   ├── generators/
│   │   ├── engine.py
│   │   ├── registry.py
│   │   └── reporting.py
│   └── cli.py
│
└── README.md
```

---

## 🧪 Corpus Statistics (v1)

### Positive Corpus

* **Rows:** 9592
* **Audit:** 1633 alignment suspects flagged.
* **Stable IDs:** Deterministic `pair_id`.

### Splits

| Split | Count |
| :--- | :--- |
| Train | 7673 |
| Dev | 959 |
| Test | 960 |

### Negatives

* **Total negatives:** 2323
* **Ratio actual:** 0.2422
* **k:** ∈ [1,3] per positive.

**By rule:**

| Rule | Rows |
| :--- | :--- |
| **R8** | 1633 |
| **R4** | 351 |
| **R6** | 295 |
| **R7** | 44 |

---

## 🧬 Implemented Linguistic Rules

### R4 — Possessive State Suffix Omission

* **Type:** Morphological | **Severity:** High
* Violates obligatory possessive suffix marking.

### R6 — NP Internal Determiner Order

* **Type:** Syntactic | **Severity:** Medium
* Swaps determiner–noun order inside noun phrases.

### R7 — Gender Agreement in Adjectives

* **Type:** Morphological | **Severity:** High
* Flips agreement suffix: `lu ↔ lo` / `tu ↔ to`.

### R8 — Spanish Determiner Injection

* **Type:** Lexical-contrastive | **Severity:** Medium
* Injects Spanish determiners into Yine target sentences.

---

## 🔄 Full Reproducible Pipeline

### 0️⃣ Activate environment

```bash
cd D:\Personal\TESIS\Yine\yine-rule-engine
.venv\Scripts\activate
```

### 1️⃣ Conditioning (Cleaning + Normalization)

```bash
yine-rules condition --config configs/default.yaml
```

### 2️⃣ Freeze Positive Dataset (Stable IDs)

```bash
yine-rules freeze-positive --exp-config configs/experiments/dataset_v1.yaml
```

### 3️⃣ Create Reproducible Splits

```bash
yine-rules make-splits \
   --positive data/processed/positive/positive_corpus.v1.parquet \
   --out data/processed/splits/split_v1.json \
   --seed 42
```

### 4️⃣ Generate Negative Samples

```bash
yine-rules gen-negatives \
   --exp-config configs/experiments/negatives_v1.yaml \
   --logging-config configs/logging.yaml
```

---

## ⚙️ Negative Sampling Engine Design

* **Uniform rule selection** e incrementos de `k ~ Uniform(k_min, k_max)`.
* **Global ratio control** y semillas deterministas.
* **Deduplicación:** Basada en `(pair_id, rule_id, negative_text)`.

---

## 📊 Output Schema

Cada muestra negativa contiene:

```json
{
  "pair_id": "str",
  "source_text": "str",
  "target_text": "str",
  "negative_text": "str",
  "rule_id": "str",
  "violation_type": "str",
  "severity": "float",
  "metadata": "dict",
  "split": "str"
}
```

---

## 🏁 Phase Status

* Corpus cleaned
* IDs frozen
* Splits reproducible
* Negative rules implemented
* Sampling corrected
* Deduplication enforced
* Stats validated

**Dataset v1 complete.**

---

## 📜 License

Academic research use only.
