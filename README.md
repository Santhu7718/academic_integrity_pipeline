# 🎓 Academic Integrity & Appeals Workflow: Synthetic Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.2.1-green)
![Status](https://img.shields.io/badge/Status-Validation_Passed-brightgreen)

## 📌 Business Context & Objective
This project implements an end-to-end synthetic data generation and validation pipeline for an **Academic Integrity and Appeals Workflow**. 

The system models the lifecycle of academic submissions, automated similarity flagging, manual investigations, evidence gathering, adjudications, and independent appeals. It is designed to generate deterministic, relationally sound data while deliberately injecting targeted edge cases to test downstream analytical systems.

## 🚀 Quick Start & Reproducibility

This pipeline guarantees **100% reproducibility**. By utilizing a fixed random seed (`20261022`), executing the generator multiple times will yield the exact same row counts, checksums, and edge cases.

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt