## ADDED Requirements

### Requirement: Persist growth runs as immutable Wiki raw sources
The system SHALL persist each completed growth run as an immutable raw source in the LLM Wiki.

#### Scenario: Growth run completes
- **WHEN** a GrowthCycle run writes report and machine-readable outputs
- **THEN** the system stores a sanitized run snapshot under `llm-wiki/raw/growth-runs/` and records source manifest entries linking the run, evidence, diagnoses, tasks, maturity estimates, reports, and generated Wiki proposals

### Requirement: Represent growth outputs as typed Wiki memory
The system SHALL represent GrowthCycle, Diagnosis, GrowthTask, MaturityEstimate, report summary, and GrowthReview records as typed growth memory Wiki pages or WikiUpdateProposals.

#### Scenario: Growth memory proposal is generated
- **WHEN** a growth output is eligible for long-term memory
- **THEN** the system creates a WikiUpdateProposal with target path, page type, lifecycle status, source run ID, source evidence IDs, confidence, evidence status, review state, and human confirmation state

### Requirement: Track growth memory lifecycle
The system MUST track lifecycle state for growth memory objects.

#### Scenario: Growth task is carried forward
- **WHEN** a GrowthTask has not been completed or reviewed by the next run
- **THEN** the system preserves it as active or carried_forward rather than replacing it with a new unrelated task

#### Scenario: Diagnosis expires
- **WHEN** a Diagnosis passes its validity window without fresh supporting evidence or human confirmation
- **THEN** the system marks it stale or proposes superseding it instead of using it as a high-confidence input

### Requirement: Support user growth reviews
The system SHALL support user-provided GrowthReview entries that evaluate task completion, usefulness, blockers, and follow-up evidence.

#### Scenario: User review exists
- **WHEN** a user review is available for a prior GrowthTask
- **THEN** the system links the review to the task, source run, affected diagnoses, and future task planning context

### Requirement: Feed Wiki growth memory into future growth cycles
The system SHALL use historical LLM Wiki growth memory as input when generating future maturity estimates, diagnoses, and growth tasks.

#### Scenario: Next growth cycle starts
- **WHEN** the system starts a new GrowthCycle and an LLM Wiki exists
- **THEN** it loads relevant active diagnoses, prior tasks, reviews, maturity snapshots, North Star goals, and action asset usage references before generating new growth outputs

### Requirement: Prevent self-reinforcing unsupported conclusions
The system MUST NOT treat prior model-generated profile, diagnosis, or maturity claims as direct evidence unless those claims are linked to original evidence or human confirmation.

#### Scenario: Prior diagnosis lacks evidence
- **WHEN** a prior Diagnosis page has no source evidence and is not human confirmed
- **THEN** the system excludes it from high-confidence diagnosis generation and records a lint issue or caution

### Requirement: Generate growth memory lint findings
The system SHALL lint growth memory for stale, unsupported, unreviewed, or inconsistent state.

#### Scenario: Growth memory lint runs
- **WHEN** Wiki lint evaluates growth memory pages
- **THEN** it reports stale diagnoses, expired maturity snapshots, unreviewed completed tasks, active tasks without review deadlines, unsupported profile claims, and growth pages missing source references
