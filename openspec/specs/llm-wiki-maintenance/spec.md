# llm-wiki-maintenance Specification

## Purpose

Define the local `llm-wiki/` maintained by Growth Knowledge Hub as the durable personal growth knowledge store.

## Requirements

### Requirement: Initialize a local LLM Wiki
The system SHALL initialize a persistent `llm-wiki/` workspace under the resolved data home.

#### Scenario: Wiki is initialized
- **WHEN** the host CLI or user runs `gkh.py init`
- **THEN** the script creates the data directory and required top-level guidance files without requiring an installed application package

### Requirement: Preserve raw sources as traceable inputs
The system SHALL write raw capture, material, and review sources with source metadata before writing human-readable Wiki pages.

#### Scenario: Raw source is written
- **WHEN** `capture`, `ingest`, or `review` accepts valid input
- **THEN** the script writes a raw source file with title, source type, original location, captured timestamp, sensitivity, tags, and hash-derived ID

### Requirement: Track source manifest entries
The system SHALL maintain `llm-wiki/data/source-manifest.json` for local provenance.

#### Scenario: Source is ingested
- **WHEN** the script writes a raw source
- **THEN** it appends a source manifest entry with source ID, raw source ID, original location, source type, tool, redaction status, hash, tags, and path

### Requirement: Generate Wiki pages with frontmatter
The system SHALL write user-readable Markdown pages with frontmatter metadata.

#### Scenario: Wiki page is created
- **WHEN** the script writes a capture, material, review, gap, or task page
- **THEN** the page includes type, status, source raw IDs, captured date or period when applicable, sensitivity, tags, and workflow-specific metadata

### Requirement: Represent external summaries as Wiki knowledge notes
The system SHALL represent imported external material and third-party skill summaries as user-readable Wiki knowledge notes.

#### Scenario: External summary page is written
- **WHEN** material ingestion writes a local summary note
- **THEN** the page includes source locator, summary policy, full-content fetch policy, retention policy, captured date, sensitivity, tags, and source raw IDs

### Requirement: Represent growth reviews and tasks as Wiki pages
The system SHALL represent host-generated growth reviews and next actions in the Wiki.

#### Scenario: Growth review is written
- **WHEN** review input is accepted
- **THEN** the script writes a review page under `wiki/growth/reviews/` and task pages under `wiki/growth/tasks/` for next tasks

### Requirement: Preserve indexed knowledge for recall
The system SHALL maintain machine-readable indexes for eligible Wiki pages.

#### Scenario: Index is rebuilt
- **WHEN** the script runs `index`, `dashboard`, or finishes a write workflow
- **THEN** it writes `llm-wiki/data/index.json` with page titles, paths, types, tags, summaries, source raw IDs, content hashes, and timestamps

### Requirement: Prevent unsupported full-Wiki dumping
The system MUST keep the Wiki readable by humans while recall commands expose only selected compact context to host models.

#### Scenario: Host needs memory context
- **WHEN** the host CLI needs prior knowledge for a conversation
- **THEN** it uses search, context, and selected read workflows rather than loading the entire Wiki
