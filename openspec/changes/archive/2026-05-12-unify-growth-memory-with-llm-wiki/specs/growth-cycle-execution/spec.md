## ADDED Requirements

### Requirement: Load historical growth memory before task generation
The system SHALL load relevant historical growth memory from the LLM Wiki before generating a new GrowthCycle.

#### Scenario: Historical growth memory exists
- **WHEN** a new GrowthCycle starts and `llm-wiki/wiki/growth/` contains active or recently reviewed growth memory
- **THEN** the system includes prior active diagnoses, unfinished tasks, recent reviews, maturity snapshots, and North Star references in the planning context

### Requirement: Distinguish new tasks from carried-forward tasks
The system SHALL distinguish tasks generated from new evidence from tasks carried forward from historical growth memory.

#### Scenario: Prior task remains active
- **WHEN** a prior GrowthTask is active and lacks a completion review
- **THEN** the system may carry it forward with updated evidence and review questions instead of creating a duplicate task

### Requirement: Use reviews as high-weight growth evidence
The system SHALL treat user GrowthReview entries as high-weight evidence for future task routing.

#### Scenario: Review reports a blocker
- **WHEN** a GrowthReview reports that a task was blocked or not useful
- **THEN** the next GrowthCycle adjusts task selection, scope, or maturity target based on the review

### Requirement: Avoid unsupported confidence amplification
The system MUST separate direct evidence, human-confirmed memory, and prior model-generated memory when estimating maturity or generating diagnoses.

#### Scenario: Maturity estimate uses prior Wiki memory
- **WHEN** a MaturityEstimate uses historical Wiki memory
- **THEN** the estimate records whether the supporting input is direct evidence, human-confirmed memory, or prior inferred memory and avoids increasing confidence from prior inferred memory alone
