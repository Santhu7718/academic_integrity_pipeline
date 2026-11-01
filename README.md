# 🎓 Academic Integrity & Appeals Workflow: Synthetic Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.2.1-green)
![Status](https://img.shields.io/badge/Status-Validation_Passed-brightgreen)

## 📌 Business Context & Objective
This project implements an end-to-end synthetic data generation and validation pipeline for an **Academic Integrity and Appeals Workflow**. The system models the lifecycle of academic submissions, automated similarity flagging, manual investigations, evidence gathering, adjudications, and independent appeals. 

## ⚙️ Environment Needs & Limitations
* **Environment Needs:** Python 3.10+, standard libraries (`os`, `json`, `random`), and third-party packages: `pandas`, `pyarrow` (for fast I/O if needed), `numpy`, `Faker`, and `PyYAML`.
* **Limitations:** The data generation runs entirely in memory using pandas DataFrames. While this easily handles the requested volume (10k submissions, 300 cases) in seconds, scaling to millions of rows would require refactoring to chunked processing or a distributed engine (e.g., PySpark/DuckDB) to avoid out-of-memory (OOM) errors.

## 🚀 Setup & Verification Instructions

This pipeline guarantees **100% reproducibility**. By utilizing a fixed random seed (`20261022`), executing the generator multiple times yields the exact same row counts, checksums, and edge cases.

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Data (Core Functionality)
```bash
python src/generator.py
```
*Expected Output: Logs indicating the generation of 10,000 Submissions, 1,000 Flags, and 300 Cases generated in `data/output/`.*

### 3. Verify Integrity (Demonstration of Core Functionality)
To verify the core functionality, I built a custom validation engine (`src/validator.py`) that strictly checks the generated outputs against relational database rules. 
```bash
python src/validator.py
```
*Verification Checks Performed:*
1. **PK Uniqueness:** Ensures no duplicate IDs exist in any entity.
2. **FK Integrity:** Scans all joins to ensure zero orphaned records (e.g., a Decision linked to a non-existent Reviewer).
3. **Enum Validation:** Verifies categorical fields (e.g., Decision outcomes must only be Guilty, Not Guilty, or Warning).
4. **Lifecycle Chronology:** Confirms dates follow logical progression (e.g., Case Opened -> Evidence Added -> Decision).

---

## 🏗️ Data Architecture & Entities

The relational schema spans 10 distinct entities, strictly adhering to custom ID nomenclatures (e.g., `SUB-2026-000001`, `SIM-<submission_id>-01`).

* **Master Data:** `Learner`, `Assessment`, `IntegrityRule`, `Reviewer`
* **Transactional Data:** `Submission`, `SimilarityReport`
* **Workflow / Event Data:** `Case`, `EvidenceItem`, `Decision`, `Appeal`

*Note: For granular field-level definitions, types, and constraints, please reference `docs/data_dictionary.md`.*

---

## ⚖️ Business Logic & Due Process Rules

1. **Thresholds, not Guilt:** A high `similarity_score` on a report flags the submission for review based on a defined `review_threshold`, but it does not automatically assign guilt. 
2. **Chronological Consistency:** Derived dates are mathematically constrained. A decision cannot precede a case opening, and evidence cannot predate a case.
3. **Audit Traceability:** State changes are captured as explicit, immutable event records (`EvidenceItem`, `Decision`, `Appeal`) rather than overwriting historical row states.

---

## 🧪 Edge Cases & Ground Truth Isolation

Specific negative scenarios are injected into the dataset. **Crucially, these anomalies are tracked in a standalone `data/ground_truth/ground_truth.csv` file to prevent data leakage into input features during downstream ML/analytical tasks.**

| Injected Edge Case | Implementation Method | Ground Truth Tracking |
| :--- | :--- | :--- |
| **1. Flag treated as auto-guilt** | Bypassed manual review utilizing a `SYSTEM_AUTO` reviewer ID with an instant decision. | Logged via `case_id`. |
| **2. Reviewer Conflict** | Simulated an instructor handling a case for their own enrolled student. | Logged via `case_id` & `reviewer_id`. |
| **3. Temporal Anomaly** | `EvidenceItem` timestamp deliberately generated *after* the `Decision` timestamp. | Logged via `case_id`. |
| **4. Biased Appeal Process** | The `reviewer_id` assigned to the `Appeal` is identical to the reviewer on the original `Decision`. | Logged via `case_id`. |

---

## 🤖 AI Usage Disclosure & Prompt History

In completing this assignment, I utilized AI (Google Gemini) as a productivity accelerator, dividing the effort approximately **70% personal work / 30% AI assistance**. 

**Where I led the work (70%):**
* **System Design & Architecture:** I designed the relational schema, defined the cardinality between the 10 entities, and established the chronological business logic.
* **Edge Case Engineering:** I formulated the exact logic required to inject the edge cases without breaking the primary relational model. 
* **Validation & Debugging:** I personally reviewed the outputs, wrote the validation requirements, and manually corrected foreign key integrity issues (specifically ensuring the `SYSTEM_AUTO` reviewer was added to the Master Reviewer table to pass FK constraints).

**Where AI accelerated my work (30%):**
* **Boilerplate Code Generation:** I relied heavily on AI to write the repetitive `pandas` and `Faker` library syntax for generating thousands of synthetic names, dates, and IDs.
* **Markdown Formatting:** Generating the structural formatting of this README and the Data Dictionary.

### Prompt History
*Note: Prompts are summarized for brevity as the workflow was highly iterative.*

1. **Prompt 1 (Data Generation Boilerplate):** *"I have designed a relational schema for an Academic Integrity workflow with 10 tables: Learner, Assessment, Submission, SimilarityReport, IntegrityRule, Case, EvidenceItem, Reviewer, Decision, Appeal. Write a Python script using Faker and Pandas to generate synthetic data for these. Enforce specific ID formats like SUB-2026-000001 and SIM-<submission-id>-01."*
2. **Prompt 2 (Edge Case Injection):** *"Update the python generator to inject 4 specific edge cases: Flag automatically treated as guilt, Reviewer has conflict, Evidence added after decision without history, Appeal closed without independent review. Ensure these anomaly IDs are exported to a separate ground_truth.csv file."*
3. **Prompt 3 (Validation Logic):** *"Write a validation script in Python using pandas that loads the 10 CSVs and checks for Primary Key uniqueness, Foreign Key integrity (no orphan records), and ensures that decision dates occur strictly after case opened dates."*
4. **Prompt 4 (Documentation):** *"Format my schema definitions and edge case logic into a professional Markdown README and Data Dictionary."*

---

## 👨‍💻 Author
**D SANTHOSH KUMAR**