## ADDED Requirements

### Requirement: Use adapter-based source ingestion
The system SHALL implement Codex, Claude Code, and opencode ingestion through source adapters rather than a single generic JSON scan.

#### Scenario: Adapter ingestion runs
- **WHEN** a source adapter discovers records
- **THEN** it returns source metadata, parse candidates, parse failures, and normalized ConversationSession records through a shared adapter contract

### Requirement: Support incremental source inventory
The system SHALL persist source scan manifests to avoid reprocessing unchanged records.

#### Scenario: Source record is unchanged
- **WHEN** a discovered source file has the same hash and modification metadata as a prior scan
- **THEN** the system marks it unchanged and may reuse prior parse status
