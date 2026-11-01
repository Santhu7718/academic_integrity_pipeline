# Academic Integrity & Appeals Workflow (Synthetic Data Pipeline)

## 📌 Objective
A relational synthetic data generator and validation pipeline modeling an academic integrity workflow. It generates 10 linked entities handling submissions, automated similarity flags, manual reviews, evidence gathering, and appeals.

## ⚙️ Reproducibility & Generation
To satisfy Step 10, this data is strictly reproducible. It utilizes a fixed random seed (`20261022`) defined in `config/pipeline_config.yaml`. Running the generator twice will produce the exact same row counts and checksums.

```bash
# Generate the data (10k submissions, 1k flags, 300 cases)
python src/generator.py

# Run the integrity validator
python src/validator.py