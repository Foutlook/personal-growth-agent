## ADDED Requirements

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
