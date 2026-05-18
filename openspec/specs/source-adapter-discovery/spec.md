## Purpose

Define source adapter discovery, scanning, parse status, and incremental inventory for supported AI conversation tools.

## Requirements

### Requirement: Use source adapters
The system SHALL discover and parse AI conversation sources through source adapters.

#### Scenario: Source scan runs
- **WHEN** the user runs `pga sources scan`
- **THEN** each enabled source adapter reports configured paths, discovered files, parse readiness, parse failures, and sensitivity hints

### Requirement: Support Codex, Claude Code, and opencode adapters
The system MUST include source adapters for Codex, Claude Code, and opencode.

#### Scenario: Default adapters are enabled
- **WHEN** no source configuration is provided
- **THEN** the system uses default adapter paths for Codex, Claude Code, and opencode and marks missing sources without failing the run

### Requirement: Record incremental scan metadata
The system SHALL record scan metadata for discovered source files.

#### Scenario: File was already processed
- **WHEN** a file path and content hash match a prior scan manifest entry
- **THEN** the system can skip reparsing that file while preserving its prior source reference

### Requirement: Preserve parse failures per adapter
The system MUST record parse failures without blocking other adapters or files.

#### Scenario: One adapter file is corrupt
- **WHEN** an adapter cannot parse one file
- **THEN** the source inventory records the failure and the system continues scanning remaining files

### Requirement: Avoid raw content in source inventory
The system MUST NOT include raw message content or raw code in source inventory output.

#### Scenario: Inventory is written
- **WHEN** source scan completes
- **THEN** inventory contains metadata, hashes, counts, paths, and parse status but not raw message text

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
