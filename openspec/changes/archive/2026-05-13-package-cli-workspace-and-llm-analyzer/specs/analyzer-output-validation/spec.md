## ADDED Requirements

### Requirement: Validate analyzer output schema
The system MUST validate LLM analyzer output against a strict schema before using it.

#### Scenario: LLM output is malformed
- **WHEN** the provider returns invalid JSON or fields outside the allowed schema
- **THEN** the system rejects the output, records an analyzer validation issue, and continues with local analysis

### Requirement: Validate evidence references
The system MUST verify that every analyzer claim references known evidence or safe source summary IDs.

#### Scenario: Claim has missing evidence reference
- **WHEN** LLM output includes a claim without valid evidence references
- **THEN** the system excludes the claim from high-confidence analysis and records a caution

### Requirement: Reconcile local and LLM signals
The system SHALL reconcile local-rules and LLM signals using explicit confidence and conflict rules.

#### Scenario: Local and LLM disagree
- **WHEN** local-rules detects a signal and LLM contradicts it
- **THEN** the system preserves the local evidence, marks a conflict, and avoids automatically increasing confidence

### Requirement: Preserve missing-evidence semantics
The system MUST NOT let LLM output convert missing evidence into negative evidence.

#### Scenario: Business evidence remains absent
- **WHEN** LLM output infers a business-depth weakness without direct evidence
- **THEN** the system records the conclusion as unknown or inferred caution rather than a confirmed weakness

### Requirement: Track analyzer provenance
The system SHALL record provider, model, analysis mode, prompt version, validation status, and reconciliation status for LLM-derived outputs.

#### Scenario: LLM-derived signal is accepted
- **WHEN** a candidate signal from LLM output is accepted
- **THEN** the signal or related audit record includes analyzer provenance and validation status
