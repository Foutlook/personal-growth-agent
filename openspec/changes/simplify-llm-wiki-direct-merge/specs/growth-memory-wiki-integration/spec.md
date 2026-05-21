## MODIFIED Requirements

### Requirement: Persist growth runs as immutable Wiki raw sources
The system SHALL persist each completed growth run as an immutable raw source in the LLM Wiki.

#### Scenario: Growth run completes
- **WHEN** a GrowthCycle run writes report and machine-readable outputs
- **THEN** the system stores a sanitized run snapshot under `llm-wiki/raw/growth-runs/` and records source manifest entries linking the run, evidence, diagnoses, tasks, maturity estimates, reports, growth memory state, and direct Wiki writes

### Requirement: Represent growth outputs as typed Wiki memory
The system SHALL represent GrowthCycle, Diagnosis, GrowthTask, MaturityEstimate, report summary, and GrowthReview records as machine-readable growth memory state, and compile only human-readable summaries into Wiki pages.

#### Scenario: Growth memory state is generated
- **WHEN** growth outputs are eligible for long-term memory
- **THEN** the system stores structured cycle, diagnosis, task, maturity, and report summary records under `llm-wiki/data/growth-memory/` with lifecycle status, source run ID, source evidence IDs, confidence, evidence status, and human confirmation state when applicable

#### Scenario: Growth Wiki summary is generated
- **WHEN** growth memory state should be visible in the human-readable Wiki
- **THEN** the system directly writes compiled summary pages such as `wiki/growth/overview.md` or `wiki/growth/current-focus.md` and records write provenance

### Requirement: Feed Wiki growth memory into future growth cycles
The system SHALL use historical growth memory state and curated Wiki pages as input when generating future maturity estimates, diagnoses, and growth tasks.

#### Scenario: Next growth cycle starts
- **WHEN** the system starts a new GrowthCycle and an LLM Wiki exists
- **THEN** it loads relevant active diagnoses, prior tasks, reviews, maturity snapshots, North Star goals, and action asset usage references from `data/growth-memory/`, raw snapshots, and curated Wiki pages before generating new growth outputs

### Requirement: Prevent self-reinforcing unsupported conclusions
The system MUST NOT treat prior model-generated profile, diagnosis, or maturity claims as direct evidence unless those claims are linked to original evidence or human confirmation.

#### Scenario: Prior diagnosis lacks evidence
- **WHEN** a prior Diagnosis record or compiled growth page lacks source evidence and is not human confirmed
- **THEN** the system excludes it from high-confidence diagnosis generation and records a lint issue or caution

### Requirement: Generate growth memory lint findings
The system SHALL lint growth memory for stale, unsupported, unreviewed, or inconsistent state.

#### Scenario: Growth memory lint runs
- **WHEN** Wiki lint evaluates growth memory state and compiled growth pages
- **THEN** it reports stale diagnoses, expired maturity snapshots, unreviewed completed tasks, active tasks without review deadlines, unsupported profile claims, and growth records or pages missing source references
