## Purpose

Define how analyzer output is validated, reconciled, and attributed before it can influence evidence, signals, growth tasks, or Wiki updates.

## Requirements

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

### Requirement: Validate scenario-specific output schemas
The system MUST validate LLM output against the schema expected by the requested scenario.

#### Scenario: Role profile output is returned
- **WHEN** the role profile prompt returns output
- **THEN** the system validates it against the role profile schema before using current role, level, strengths, risks, or cautions

#### Scenario: Growth planning output is returned
- **WHEN** the growth planning prompt returns output
- **THEN** the system validates steps, done definition, review questions, track, and evidence references before accepting any GrowthTask

### Requirement: Preserve prompt provenance
The system SHALL record prompt ID, prompt version, prompt digest, scenario, provider, model, validation status, and reconciliation status for every accepted or rejected LLM output.

#### Scenario: LLM output is rejected
- **WHEN** validation rejects an LLM output
- **THEN** the audit records prompt provenance and rejection reason without using the output as high-confidence analysis

### Requirement: Reconcile LLM-first output with local rules
The system SHALL reconcile LLM-first output with local-rule signals before final growth outputs are written.

#### Scenario: LLM contradicts local evidence
- **WHEN** LLM output contradicts local-rule evidence or omits required evidence references
- **THEN** the system marks the conflict, avoids confidence amplification, and preserves local-rule evidence in the audit
