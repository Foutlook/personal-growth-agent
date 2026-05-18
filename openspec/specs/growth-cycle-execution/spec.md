## Purpose

Define how evidence-backed diagnoses become bounded, executable growth cycles aligned to the user's long-term growth goals.

## Requirements

### Requirement: Maintain three-track growth North Star
The system SHALL evaluate growth against three tracks: AI Agent engineering, business depth expertise, and AI system management and optimization.

#### Scenario: Growth cycle is created
- **WHEN** the system generates a GrowthCycle
- **THEN** the cycle includes references to the three growth tracks and identifies the primary track, secondary track, or balanced focus for the cycle

### Requirement: Estimate maturity with evidence status
The system SHALL produce MaturityEstimate outputs that include level range, confidence, observed signals, missing next-level signals, and evidence status.

#### Scenario: Evidence is direct
- **WHEN** source evidence directly demonstrates a maturity behavior
- **THEN** the system marks the maturity estimate status as Observed

#### Scenario: Evidence is insufficient
- **WHEN** source evidence does not support a maturity conclusion
- **THEN** the system marks the maturity estimate status as Unknown and avoids strong claims

### Requirement: Generate diagnosis from signals
The system SHALL generate Diagnosis records from EvidenceSignal combinations before generating growth tasks.

#### Scenario: Diagnosis is generated
- **WHEN** EvidenceSignal combinations indicate a bottleneck, leverage point, knowledge gap, or risk pattern
- **THEN** the system creates a Diagnosis with target tracks, confidence, supporting signal IDs, supporting evidence IDs, and recommended focus

### Requirement: Generate executable growth tasks
The system SHALL generate GrowthTask records that are actionable, scoped, and reviewable.

#### Scenario: Growth task is valid
- **WHEN** a GrowthTask is included in the output
- **THEN** it includes target track, maturity move, time budget, steps, done definition, review questions, source diagnosis IDs, and expected artifacts

### Requirement: Enforce task executability
The system MUST reject or revise any GrowthTask that lacks a done definition, review questions, time budget, or evidence basis.

#### Scenario: Task lacks done definition
- **WHEN** a generated task has no doneDefinition
- **THEN** the system marks it invalid and does not include it in the final growth task package

### Requirement: Generate a bounded MVP growth cycle
The system SHALL generate at least one GrowthCycle with three initial tasks for the MVP flow.

#### Scenario: MVP growth cycle succeeds
- **WHEN** sufficient evidence exists for at least one complex AI collaboration case
- **THEN** the system generates one Agent engineering task, one business depth task, and one AI system management task tied to that case

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

### Requirement: Use validated analyzer output in growth cycle generation
The system SHALL use validated LLM analyzer output as candidate input for maturity estimates, diagnoses, growth tasks, and Wiki update suggestions.

#### Scenario: Validated LLM task exists
- **WHEN** validated analyzer output includes a growth task with evidence references and done definition
- **THEN** GrowthCycle generation can include or merge that task while preserving evidence basis and analyzer provenance

### Requirement: Keep local fallback for growth cycle generation
The system MUST generate a GrowthCycle using local-rules output when LLM analysis is unavailable or rejected.

#### Scenario: External analyzer is not approved
- **WHEN** outbound approval is missing for a non-local provider
- **THEN** the system skips external analysis and generates the GrowthCycle from local evidence and historical Wiki memory

### Requirement: Use LLM-first analyzer output for growth cycles
The system SHALL use validated LLM-first analyzer output as the primary candidate input for GrowthCycle generation.

#### Scenario: Validated LLM analysis exists
- **WHEN** role profile, maturity scoring, diagnoses, and growth planning outputs pass validation
- **THEN** the GrowthCycle uses those outputs while preserving source evidence IDs and analyzer provenance

### Requirement: Preserve local maturity fallback
The system MUST preserve local-rule maturity and task generation when LLM-first analysis is unavailable.

#### Scenario: LLM-first analysis is unavailable
- **WHEN** remote approval is missing, provider call fails, or validation rejects output
- **THEN** the system generates GrowthCycle output from local-rule evidence, local signals, and historical Wiki memory

### Requirement: Prevent LLM-only unsupported maturity claims
The system MUST NOT treat LLM conclusions as observed maturity evidence unless they reference direct evidence or human-confirmed memory.

#### Scenario: LLM infers seniority without evidence
- **WHEN** LLM output infers a role level without valid evidence references
- **THEN** the system records the inference as a caution or rejects the maturity claim
