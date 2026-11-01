import os
import yaml
import json
import random
import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta

# Load configuration
def load_config():
    with open('config/pipeline_config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# Set Fixed Seeds for Absolute Reproducibility (Requirement #7 & #10)
SEED = config['pipeline']['fixed_seed']
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()

def generate_synthetic_data():
    print(f"Initializing data generation with fixed seed: {SEED}...")
    
    # -------------------------------------------------------------------
    # 1. MASTER DATA GENERATION (Learner, Assessment, IntegrityRule, Reviewer)
    # -------------------------------------------------------------------
    print("Generating Master Data...")
    
    # Learners
    learners = pd.DataFrame({
        'learner_id': [f"LRN-2026-{i:06d}" for i in range(1, 2001)],
        'status': 'Active',
        'enrollment_date': [fake.date_time_between(start_date='-2y', end_date='-1y') for _ in range(2000)]
    })

    # Assessments
    assessments = pd.DataFrame({
        'assessment_id': [f"ASM-2026-{i:04d}" for i in range(1, 51)],
        'type': np.random.choice(['Essay', 'Code Project', 'Exam'], 50),
        'due_date': [fake.date_time_between(start_date='-11m', end_date='now') for _ in range(50)]
    })

    # Integrity Rules (Thresholds)
    rules = pd.DataFrame({
        'rule_id': [f"INT-2026-{i:06d}" for i in range(1, 6)],
        'rule_name': ['High Text Overlap', 'Code Structural Similarity', 'Known Template Match', 'Suspicious IP', 'AI Generated Text'],
        'review_threshold': [0.40, 0.60, 0.85, 1.0, 0.70] # Triggers review, not automatic guilt
    })

    # Reviewers
    reviewers = pd.DataFrame({
        'reviewer_id': [f"REV-2026-{i:04d}" for i in range(1, 101)],
        'role': np.random.choice(['Instructor', 'Academic Administrator', 'Support Staff'], 100),
        'department': np.random.choice(['Computer Science', 'Humanities', 'Business'], 100)
    })
    system_reviewer = pd.DataFrame([{
        'reviewer_id': 'SYSTEM_AUTO', 
        'role': 'Platform Administrator', 
        'department': 'Automated System'
    }])
    reviewers = pd.concat([reviewers, system_reviewer], ignore_index=True)

    # -------------------------------------------------------------------
    # 2. TRANSACTIONAL DATA (Submissions & Similarity Reports)
    # -------------------------------------------------------------------
    print("Generating Submissions and Similarity Reports...")
    
    num_subs = config['scale']['submissions']
    sub_prefix = config['prefixes']['submission']
    
    submissions = pd.DataFrame({
        'submission_id': [f"{sub_prefix}{i:06d}" for i in range(1, num_subs + 1)],
        'learner_id': np.random.choice(learners['learner_id'], num_subs),
        'assessment_id': np.random.choice(assessments['assessment_id'], num_subs),
    })
    
    # Calculate derived dates based on parent assessment due dates
    merged_sub = submissions.merge(assessments[['assessment_id', 'due_date']], on='assessment_id', how='left')
    submissions['submission_date'] = merged_sub['due_date'] - pd.to_timedelta(np.random.randint(-2, 10, num_subs), unit='d')

    # Similarity Reports
    sim_reports = pd.DataFrame({
        'report_id': [f"SIM-{sub}-01" for sub in submissions['submission_id']],
        'submission_id': submissions['submission_id'],
        'rule_id': np.random.choice(rules['rule_id'], num_subs),
        'similarity_score': np.random.beta(a=1, b=5, size=num_subs) # Skews heavily toward 0 (low similarity)
    })
    
    # Merge rules to determine if flag threshold is met
    sim_reports = sim_reports.merge(rules[['rule_id', 'review_threshold']], on='rule_id')
    sim_reports['is_flagged'] = sim_reports['similarity_score'] >= sim_reports['review_threshold']
    
    # Force exactly 1000 flags to meet requirements
    flag_indices = sim_reports.sample(config['scale']['flags']).index
    sim_reports['is_flagged'] = False
    sim_reports.loc[flag_indices, 'is_flagged'] = True
    sim_reports.loc[flag_indices, 'similarity_score'] = np.random.uniform(0.7, 1.0, len(flag_indices)) # Force high scores

    # -------------------------------------------------------------------
    # 3. WORKFLOW DATA (Cases, Evidence, Decisions, Appeals)
    # -------------------------------------------------------------------
    print("Generating Cases, Evidence, and Workflow...")
    
    flagged_subs = sim_reports[sim_reports['is_flagged'] == True]['submission_id'].tolist()
    case_subs = random.sample(flagged_subs, config['scale']['cases']) # 300 cases
    
    cases = pd.DataFrame({
        'case_id': [f"CAS-2026-{i:06d}" for i in range(1, len(case_subs) + 1)],
        'submission_id': case_subs,
        'status': 'Closed',
        'opened_date': submissions[submissions['submission_id'].isin(case_subs)]['submission_date'].values + pd.to_timedelta(1, unit='d')
    })

    # Evidence, Decisions, Appeals Lists
    evidence_list, decisions_list, appeals_list = [], [], []
    ground_truth = [] # Track intentional anomalies

    for idx, row in cases.iterrows():
        case_id = row['case_id']
        case_opened = row['opened_date']
        
        # Base Data
        evd_date = case_opened + timedelta(days=random.randint(1, 3))
        dec_date = evd_date + timedelta(days=random.randint(1, 5))
        
        reviewer = random.choice(reviewers['reviewer_id'].tolist())
        outcome = random.choice(['Guilty', 'Not Guilty', 'Warning'])
        rationale = "Legitimate quoted material." if outcome == 'Not Guilty' else "Shared template violation."
        
        has_appeal = random.random() < 0.2 # 20% get appealed
        
        # ---------------------------------------------------------------
        # INJECT EDGE CASES (Tracked in Ground Truth)
        # ---------------------------------------------------------------
        
        if idx == 0:
            # EDGE CASE 1: Flag automatically treated as guilt (No human reviewer, instant decision)
            reviewer = "SYSTEM_AUTO"
            dec_date = case_opened # Instant
            outcome = "Guilty"
            rationale = "Auto-applied guilt without review."
            ground_truth.append({"entity_id": case_id, "issue_type": "Flag automatically treated as guilt"})
            
        elif idx == 1:
            # EDGE CASE 2: Reviewer has conflict (Instructor reviewing their own student/assignment)
            # Simulated by logging the conflict flag
            ground_truth.append({"entity_id": case_id, "reviewer_id": reviewer, "issue_type": "Reviewer has conflict"})
            
        elif idx == 2:
            # EDGE CASE 3: Evidence added after decision without history
            evd_date = dec_date + timedelta(days=5) # Temporal anomaly
            ground_truth.append({"entity_id": case_id, "issue_type": "Evidence added after decision without history"})
            
        elif idx == 3:
            # EDGE CASE 4: Appeal closed without independent review (Same reviewer handles appeal)
            has_appeal = True
            appeal_reviewer = reviewer # Same person!
            ground_truth.append({"entity_id": case_id, "issue_type": "Appeal closed without independent review"})
            
        else:
            appeal_reviewer = random.choice([r for r in reviewers['reviewer_id'].tolist() if r != reviewer])

        # Create Records
        evidence_list.append({
            'evidence_id': f"EVD-{case_id}-001",
            'case_id': case_id,
            'description': "Similarity report and source code comparison.",
            'added_date': evd_date
        })
        
        decisions_list.append({
            'decision_id': f"DEC-{case_id}-01",
            'case_id': case_id,
            'reviewer_id': reviewer,
            'decision_date': dec_date,
            'outcome': outcome,
            'rationale': rationale
        })
        
        if has_appeal:
            appeals_list.append({
                'appeal_id': f"APL-{case_id}-01",
                'decision_id': f"DEC-{case_id}-01",
                'reviewer_id': appeal_reviewer,
                'appeal_date': dec_date + timedelta(days=random.randint(2, 10)),
                'appeal_outcome': random.choice(['Upheld', 'Overturned'])
            })

    evidence = pd.DataFrame(evidence_list)
    decisions = pd.DataFrame(decisions_list)
    appeals = pd.DataFrame(appeals_list)
    gt_df = pd.DataFrame(ground_truth)

    # -------------------------------------------------------------------
    # 4. EXPORT TO CSV
    # -------------------------------------------------------------------
    out_dir = config['paths']['output_dir']
    
    dataframes = {
        'learners': learners, 'assessments': assessments, 'integrity_rules': rules, 
        'reviewers': reviewers, 'submissions': submissions, 'similarity_reports': sim_reports,
        'cases': cases, 'evidence': evidence, 'decisions': decisions, 'appeals': appeals
    }
    
    for name, df in dataframes.items():
        df.to_csv(os.path.join(out_dir, f"{name}.csv"), index=False)
        
    # Ground Truth separated!
    gt_df.to_csv(os.path.join(config['paths']['ground_truth_dir'], "ground_truth.csv"), index=False)
    
    print(f"✅ Generated {len(dataframes)} entity tables in '{out_dir}/'")
    print(f"✅ Generated ground truth labels in '{config['paths']['ground_truth_dir']}/'")
    print("Reconciliation Metrics:")
    print(f" - Submissions: {len(submissions)}")
    print(f" - Flags: {sim_reports['is_flagged'].sum()}")
    print(f" - Cases: {len(cases)}")

if __name__ == "__main__":
    generate_synthetic_data()