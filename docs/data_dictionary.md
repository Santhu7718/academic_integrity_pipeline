# Academic Integrity Workflow - Data Dictionary

## Master Entities

### 1. Learner
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `learner_id` | String | Yes | Format: LRN-2026-XXXXXX (Unique) | Primary Key. |
| `status` | Enum | Yes | Active, Suspended, Alumni | Enrollment status. |
| `enrollment_date` | Date | Yes | Past 2 years | Date learner joined. |

### 2. Assessment
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `assessment_id` | String | Yes | Format: ASM-2026-XXXX (Unique) | Primary Key. |
| `type` | Enum | Yes | Essay, Code Project, Exam | Type of work assessed. |
| `due_date` | Date | Yes | Past 11 months | Deadline for submission. |

### 3. IntegrityRule
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `rule_id` | String | Yes | Format: INT-2026-XXXXXX (Unique) | Primary Key. |
| `rule_name` | String | Yes | High Text Overlap, Code Similarity... | Business name of the rule. |
| `review_threshold` | Float | Yes | 0.0 to 1.0 | Score threshold triggering manual review (not automatic guilt). |

### 4. Reviewer
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `reviewer_id` | String | Yes | Format: REV-2026-XXXX (Unique) | Primary Key (includes SYSTEM_AUTO). |
| `role` | Enum | Yes | Instructor, Academic Admin, Support | Job function. |

## Transactional / Event Entities

### 5. Submission
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `submission_id` | String | Yes | Format: SUB-2026-XXXXXX (Unique) | Primary Key. |
| `learner_id` | String | Yes | Valid Learner PK | Foreign Key. |
| `assessment_id` | String | Yes | Valid Assessment PK | Foreign Key. |
| `submission_date` | Date | Yes | <= Assessment due_date | Chronological validation rule applies. |

### 6. SimilarityReport
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `report_id` | String | Yes | Format: SIM-<submission_id>-01 | Primary Key. |
| `submission_id` | String | Yes | Valid Submission PK | Foreign Key. |
| `rule_id` | String | Yes | Valid IntegrityRule PK | Foreign Key. |
| `similarity_score` | Float | Yes | 0.0 to 1.0 | Continuous score from scan. |
| `is_flagged` | Bool | Yes | True/False | Derived: True if >= rule review_threshold. |

### 7. Case
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `case_id` | String | Yes | Format: CAS-2026-XXXXXX (Unique) | Primary Key. |
| `submission_id` | String | Yes | Valid Submission PK | Foreign Key. |
| `status` | Enum | Yes | Open, Under Review, Closed | Lifecycle state. |
| `opened_date` | Date | Yes | > submission_date | Triggered by a flagged report. |

### 8. EvidenceItem
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `evidence_id` | String | Yes | Format: EVD-<case_id>-XXX | Primary Key. |
| `case_id` | String | Yes | Valid Case PK | Foreign Key. |
| `added_date` | Date | Yes | >= case opened_date | Audit history date. |

### 9. Decision
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `decision_id` | String | Yes | Format: DEC-<case_id>-01 | Primary Key. |
| `case_id` | String | Yes | Valid Case PK | Foreign Key. |
| `reviewer_id` | String | Yes | Valid Reviewer PK | Foreign Key. |
| `outcome` | Enum | Yes | Guilty, Not Guilty, Warning | Adjudication result. |

### 10. Appeal
| Field | Type | Required | Allowed Values / Validation | Description |
| :--- | :--- | :--- | :--- | :--- |
| `appeal_id` | String | Yes | Format: APL-<case_id>-01 | Primary Key. |
| `decision_id` | String | Yes | Valid Decision PK | Foreign Key. |
| `reviewer_id` | String | Yes | Valid Reviewer PK | Must NOT equal Decision reviewer_id. |
| `appeal_outcome`| Enum | Yes | Upheld, Overturned | Final outcome. |