## ADDED Requirements

### Requirement: Run LLM-first analysis
The system SHALL support an LLM-first analysis mode where validated LLM output is the primary source for role inference, maturity scoring, diagnoses, growth tasks, and Wiki suggestions.

#### Scenario: LLM-first mode succeeds
- **WHEN** the configured LLM provider returns valid output with valid evidence references
- **THEN** the system uses the validated LLM output as primary analyzer input while retaining local-rule provenance

### Requirement: Use local rules as LLM context
The system SHALL use local-rule evidence and signals as structured context for LLM prompts.

#### Scenario: Analyzer prompt is built
- **WHEN** the system builds an LLM prompt for a scenario
- **THEN** it includes redacted evidence summaries, local signals, allowed Wiki memory, knowledge gaps, and repository summaries as structured context

### Requirement: Use scenario-specific prompts
The system SHALL use different prompts for different analyzer scenarios.

#### Scenario: Maturity scoring runs
- **WHEN** the system requests maturity scoring from an LLM
- **THEN** it uses the maturity scoring prompt rather than the role profile or Wiki maintenance prompt

#### Scenario: Knowledge ingestion enrichment runs
- **WHEN** the system requests knowledge ingestion enrichment from an LLM
- **THEN** it uses the knowledge ingestion prompt and expected Wiki proposal schema

### Requirement: Keep local fallback available
The system MUST keep local-rule outputs available when LLM-first analysis cannot be used.

#### Scenario: Remote LLM fails validation
- **WHEN** the remote LLM returns invalid JSON, invalid schema, missing evidence references, or unsafe content
- **THEN** the system records the failure and generates outputs using local-rule evidence and existing growth memory
