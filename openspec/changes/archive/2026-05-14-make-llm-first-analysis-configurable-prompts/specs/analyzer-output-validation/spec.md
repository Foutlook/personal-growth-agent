## ADDED Requirements

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
