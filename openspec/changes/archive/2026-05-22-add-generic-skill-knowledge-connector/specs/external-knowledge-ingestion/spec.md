## ADDED Requirements

### Requirement: Ingest external skill summaries as local Wiki notes
The system SHALL ingest selected external skill knowledge items as user-readable local Wiki summary notes instead of full third-party content mirrors.

#### Scenario: User imports an external skill item summary
- **WHEN** the user selects a third-party knowledge item for local import through an approved connector
- **THEN** the system creates or updates a local Wiki knowledge page containing a human-readable summary note with source provenance and no full third-party body by default

### Requirement: Limit external skill summaries to six bullet points
The system MUST cap generated local summaries for external skill items at six bullet points.

#### Scenario: Summary is generated from external item metadata
- **WHEN** the system writes a local summary note for an external skill item
- **THEN** the summary section contains no more than six bullet points

### Requirement: Retain external skill summaries long term
The system SHALL treat imported external skill summary notes as long-lived local knowledge.

#### Scenario: Remote item changes or disappears
- **WHEN** a previously imported third-party item is no longer available or has changed remotely
- **THEN** the system preserves the local summary note and may annotate freshness or source availability without deleting the note

### Requirement: Avoid implicit full-content persistence
The system MUST NOT persist fetched third-party full content as a raw source or Wiki page unless the user explicitly requests a future full-content ingestion workflow.

#### Scenario: Full content is fetched to answer a question
- **WHEN** the system fetches third-party full content on demand for a user question
- **THEN** the fetched body is used transiently and is not stored as a local raw full-content mirror by default
