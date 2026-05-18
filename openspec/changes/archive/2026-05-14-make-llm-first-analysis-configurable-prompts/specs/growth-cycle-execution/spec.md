## ADDED Requirements

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
