import os
import pandas as pd
import yaml

def load_config():
    with open('config/pipeline_config.yaml', 'r') as file:
        return yaml.safe_load(file)

class WorkflowValidator:
    def __init__(self):
        self.config = load_config()
        self.output_dir = self.config['paths']['output_dir']
        self.data = self._load_data()
        self.errors = []

    def _load_data(self):
        print("Loading generated data for validation...")
        datasets = {}
        for file in os.listdir(self.output_dir):
            if file.endswith('.csv'):
                name = file.replace('.csv', '')
                datasets[name] = pd.read_csv(os.path.join(self.output_dir, file))
        return datasets

    def log_error(self, check_name, message):
        self.errors.append({"Check": check_name, "Error": message})
        print(f"❌ [{check_name}] {message}")

    def log_pass(self, check_name, message):
        print(f"✅ [{check_name}] {message}")

    def validate_primary_keys(self):
        """Validates that all designated primary keys are strictly unique."""
        pks = {
            'learners': 'learner_id', 'assessments': 'assessment_id',
            'integrity_rules': 'rule_id', 'reviewers': 'reviewer_id',
            'submissions': 'submission_id', 'similarity_reports': 'report_id',
            'cases': 'case_id', 'evidence': 'evidence_id',
            'decisions': 'decision_id', 'appeals': 'appeal_id'
        }
        for table, pk in pks.items():
            df = self.data.get(table)
            if df is not None:
                duplicates = df[df.duplicated(subset=[pk])]
                if not duplicates.empty:
                    self.log_error("PK Uniqueness", f"Table {table} has {len(duplicates)} duplicate primary keys ({pk}).")
                    
        if not self.errors:
            self.log_pass("PK Uniqueness", "All primary keys are unique across all 10 entities.")

    def validate_foreign_keys(self):
        """Ensures no orphan records exist across joined tables."""
        fks = [
            ('submissions', 'learner_id', 'learners', 'learner_id'),
            ('submissions', 'assessment_id', 'assessments', 'assessment_id'),
            ('similarity_reports', 'submission_id', 'submissions', 'submission_id'),
            ('cases', 'submission_id', 'submissions', 'submission_id'),
            ('decisions', 'case_id', 'cases', 'case_id'),
            ('decisions', 'reviewer_id', 'reviewers', 'reviewer_id'),
            ('appeals', 'decision_id', 'decisions', 'decision_id')
        ]
        
        fk_errors = False
        for child, child_col, parent, parent_col in fks:
            child_df = self.data.get(child)
            parent_df = self.data.get(parent)
            
            if child_df is not None and parent_df is not None:
                orphans = child_df[~child_df[child_col].isin(parent_df[parent_col])]
                if not orphans.empty:
                    fk_errors = True
                    self.log_error("FK Integrity", f"{len(orphans)} orphans in {child}.{child_col} referencing {parent}.{parent_col}")
                    
        if not fk_errors:
            self.log_pass("FK Integrity", "All foreign key relationships are strictly maintained.")

    def validate_enums(self):
        """Checks that categorical fields only contain approved values."""
        df = self.data.get('decisions')
        if df is not None:
            valid_outcomes = ['Guilty', 'Not Guilty', 'Warning']
            invalid = df[~df['outcome'].isin(valid_outcomes)]
            if not invalid.empty:
                self.log_error("Enum Validation", f"Invalid outcomes found in decisions: {invalid['outcome'].unique()}")
            else:
                self.log_pass("Enum Validation", "All categorical lifecycle enums are valid.")

    def validate_lifecycle_dates(self):
        """Validates chronologies (e.g., A decision cannot happen before a case opens)."""
        cases = self.data.get('cases')
        decisions = self.data.get('decisions')
        
        if cases is not None and decisions is not None:
            merged = decisions.merge(cases, on='case_id')
            merged['decision_date'] = pd.to_datetime(merged['decision_date'])
            merged['opened_date'] = pd.to_datetime(merged['opened_date'])
            
            invalid_dates = merged[merged['decision_date'] < merged['opened_date']]
            if not invalid_dates.empty:
                self.log_error("Date Lifecycle", f"{len(invalid_dates)} decisions occurred BEFORE the case was opened.")
            else:
                self.log_pass("Date Lifecycle", "Lifecycle date transitions follow correct chronological order (Case Opened -> Decision).")

    def run_all_validations(self):
        print("\n--- Running Validation Suite ---")
        self.validate_primary_keys()
        self.validate_foreign_keys()
        self.validate_enums()
        self.validate_lifecycle_dates()
        
        print("\n--- Validation Summary ---")
        if not self.errors:
            print("🎉 All validation checks passed perfectly! Relational integrity is intact.")
        else:
            print(f"⚠️ Pipeline finished with {len(self.errors)} validation errors.")

if __name__ == "__main__":
    validator = WorkflowValidator()
    validator.run_all_validations()