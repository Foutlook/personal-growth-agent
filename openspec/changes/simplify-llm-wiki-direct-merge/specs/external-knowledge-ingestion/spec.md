## MODIFIED Requirements

### Requirement: Generate reviewable Wiki proposals from knowledge
The system SHALL compile ingested knowledge directly into Wiki pages while preserving raw source traceability and write provenance.

#### Scenario: Knowledge maps to an existing page
- **WHEN** an ingested source is relevant to an existing Wiki page
- **THEN** the system directly updates the target Wiki page with source references and records the write in `data/wiki-write-log.json`

#### Scenario: Knowledge has no matching page
- **WHEN** an ingested source introduces a topic not represented in the Wiki
- **THEN** the system directly creates a new Wiki page under an appropriate knowledge category with source references and write-log provenance

### Requirement: Preserve source traceability for knowledge claims
The system MUST link every generated knowledge claim to raw source references.

#### Scenario: Knowledge Wiki page contains a claim
- **WHEN** the system writes a knowledge-derived Wiki page
- **THEN** the page includes source raw IDs or source paths for the claim

### Requirement: Support knowledge gap extraction
The system SHALL identify reusable knowledge gaps from ingested external sources and existing Wiki state.

#### Scenario: Knowledge source raises unresolved questions
- **WHEN** ingested knowledge includes uncertain concepts, missing prerequisites, or follow-up questions
- **THEN** the system records knowledge gaps as directly written Wiki content or machine-readable dashboard data with raw source references
