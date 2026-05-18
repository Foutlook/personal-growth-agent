## ADDED Requirements

### Requirement: Enrich local evidence with LLM analysis
The system SHALL allow an LLM analyzer to enrich local EvidenceItem and EvidenceSignal outputs.

#### Scenario: Assist mode runs
- **WHEN** analysis mode is `assist`
- **THEN** the LLM may propose role inference, strengths, risks, candidate signals, growth tasks, and Wiki update suggestions without directly replacing local evidence

### Requirement: Support hybrid analysis mode
The system SHALL support a hybrid mode where local-rules and LLM analysis jointly inform diagnosis and growth task generation.

#### Scenario: Hybrid mode has matching evidence
- **WHEN** local-rules and LLM output support the same signal with valid evidence references
- **THEN** the reconciled signal may receive higher confidence within configured limits

### Requirement: Preserve evidence references in LLM output
The LLM analyzer MUST reference existing EvidenceItem IDs or safe source summary IDs for every claim it proposes.

#### Scenario: LLM proposes a new strength
- **WHEN** LLM output includes a strength, risk, role inference, candidate signal, or growth task rationale
- **THEN** the output includes evidence IDs that exist in the current run context

### Requirement: Prevent raw content dependency
The LLM analyzer MUST operate on redacted evidence summaries and allowed Wiki memory by default.

#### Scenario: External LLM payload is prepared
- **WHEN** provider is not local
- **THEN** the payload excludes raw messages, raw code, local_only evidence, and private identifiers unless explicitly approved by a future capability

### Requirement: Generate LLM-backed growth suggestions
The system SHALL transform validated LLM growth suggestions into candidate Diagnosis, GrowthTask, ActionAsset, or WikiUpdateProposal inputs.

#### Scenario: LLM suggests a growth task
- **WHEN** a validated LLM response includes a growth task with steps, done definition, evidence references, and target track
- **THEN** the system can include it as a candidate task with LLM provenance and confidence
