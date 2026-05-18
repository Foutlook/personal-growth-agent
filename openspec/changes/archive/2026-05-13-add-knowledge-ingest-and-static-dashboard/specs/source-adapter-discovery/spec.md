## ADDED Requirements

### Requirement: Keep conversation adapters separate from explicit knowledge ingestion
The system SHALL keep Codex, Claude Code, and opencode conversation source adapters separate from explicit external knowledge ingestion commands.

#### Scenario: Source scan runs
- **WHEN** the user runs `pga sources scan`
- **THEN** the command reports AI conversation source adapter inventory and does not automatically ingest web articles, notes, or arbitrary local documents as knowledge sources

### Requirement: Reuse manifest conventions for knowledge sources
External knowledge ingestion SHALL reuse source manifest conventions where they help traceability without changing conversation adapter semantics.

#### Scenario: Knowledge source is recorded
- **WHEN** an external knowledge source is added to the LLM Wiki
- **THEN** its manifest entry uses compatible fields for source ID, raw source ID, original location, ingest time, source type, redaction status, and hash
