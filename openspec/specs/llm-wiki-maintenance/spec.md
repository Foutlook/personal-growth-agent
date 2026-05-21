## Purpose

Define how the system maintains a persistent LLM Wiki as the user's long-lived, directly written knowledge base.

## Requirements

### Requirement: Maintain an LLM Wiki workspace
The system SHALL maintain a persistent llm-wiki/ workspace separate from per-run outputs.

#### Scenario: LLM Wiki workspace is initialized
- **WHEN** the system runs and no llm-wiki/ exists
- **THEN** it creates the required top-level structure including AGENTS.md or SCHEMA.md, raw/, wiki/, machine-usable/, prompts or prompt references, report/, and data/

### Requirement: Preserve raw sources as read-only inputs
The system MUST treat raw sources as immutable after ingestion.

#### Scenario: Raw source already exists
- **WHEN** the system processes a RawSource that already exists
- **THEN** it does not overwrite the existing file and instead creates a new version or records a source manifest entry

### Requirement: Track source manifest entries
The system SHALL maintain SourceManifest records linking original local sources, RawSource entries, evidence IDs, and direct Wiki writes.

#### Scenario: Raw source is ingested
- **WHEN** a conversation, repository snapshot, growth artifact, or action asset is added to raw/
- **THEN** the system records source ID, raw source ID, original location, ingest time, source type, tool, redaction status, and hash

#### Scenario: Wiki page is directly written from sources
- **WHEN** the system writes compiled content into `wiki/`
- **THEN** the system records direct write provenance in `data/wiki-write-log.json` and links the write to relevant source manifest entries when available

### Requirement: Generate Wiki pages with frontmatter
The system SHALL generate directly written Wiki pages with required frontmatter fields.

#### Scenario: WikiPage is created or updated
- **WHEN** the system directly writes a WikiPage
- **THEN** the page contains title, type, status, source_count, source_evidence_ids or source_paths, last_reviewed or generated_at, sensitivity, confidence, tracks, and related links when applicable

### Requirement: Generate Wiki lint reports
The system SHALL generate Wiki Lint reports for the LLM Wiki workspace.

#### Scenario: Wiki lint runs
- **WHEN** lint is requested or a GrowthCycle completes
- **THEN** the system reports missing sources, broken links, stale claims, duplicate pages, privacy risks, and invalid frontmatter

### Requirement: Prevent unsupported deletion
The system MUST NOT delete Wiki pages as part of LLM-generated maintenance.

#### Scenario: Page should no longer be used
- **WHEN** a WikiPage is obsolete
- **THEN** the system proposes marking it deprecated rather than deleting it

### Requirement: Include growth memory directories in LLM Wiki workspace
The system SHALL include dedicated growth memory locations in the LLM Wiki workspace while keeping automatic machine state out of the human-readable Wiki layer.

#### Scenario: LLM Wiki workspace is initialized with growth memory support
- **WHEN** the system initializes `llm-wiki/`
- **THEN** it creates directories for `raw/growth-runs/`, `raw/growth-reviews/`, `data/growth-memory/`, `wiki/profile/`, `wiki/growth/`, `wiki/growth/reviews/`, and `wiki/cases/`

### Requirement: Extend WikiPage frontmatter for growth memory
The system SHALL support growth memory frontmatter fields for WikiPage drafts.

#### Scenario: Growth memory page is created
- **WHEN** the system creates a WikiPage for a growth memory object
- **THEN** the page contains type, lifecycle status, source run ID, source evidence IDs, source raw IDs, evidence status, confidence, human confirmation state, validity window, review state, tracks, and related pages

### Requirement: Preserve growth run snapshots as raw inputs
The system MUST treat growth run snapshots and user growth reviews as raw inputs with immutable source references.

#### Scenario: Growth run snapshot already exists
- **WHEN** the system processes a previously stored growth run snapshot
- **THEN** it does not overwrite the raw snapshot and records any new linkage through source manifest entries or new versions

### Requirement: Lint growth memory pages
The system SHALL include growth memory checks in Wiki Lint reports.

#### Scenario: Growth memory page is missing traceability
- **WHEN** a growth memory page lacks source evidence, source raw IDs, or source run metadata
- **THEN** Wiki Lint reports a traceability issue with a suggested fix

### Requirement: Include external knowledge directories in LLM Wiki workspace
The system SHALL include dedicated directories for externally ingested knowledge in the LLM Wiki workspace.

#### Scenario: LLM Wiki workspace is initialized with knowledge ingestion support
- **WHEN** the system initializes `llm-wiki/`
- **THEN** it creates directories for `raw/knowledge/web/`, `raw/knowledge/notes/`, `raw/knowledge/files/`, `raw/knowledge/excerpts/`, `wiki/knowledge/`, `wiki/knowledge/concepts/`, `wiki/knowledge/sources/`, and `wiki/knowledge/gaps/`

### Requirement: Extend WikiPage frontmatter for external knowledge
The system SHALL support frontmatter fields needed for externally ingested knowledge pages.

#### Scenario: Knowledge Wiki page is directly written
- **WHEN** the system creates or updates a WikiPage from external knowledge
- **THEN** the page metadata includes type, status, source raw IDs or source paths, original URL when present, author or publisher when present, captured date, sensitivity, confidence, tags, related pages, unresolved questions when present, and generated timestamp

### Requirement: Lint external knowledge pages
The system SHALL include external knowledge checks in Wiki Lint reports.

#### Scenario: Knowledge page lacks provenance
- **WHEN** a knowledge page lacks raw source references or original source metadata
- **THEN** Wiki Lint reports a provenance issue with a suggested fix

#### Scenario: Knowledge page contains unsupported claims
- **WHEN** a knowledge page contains claims without source references or uncertainty markers
- **THEN** Wiki Lint reports an unsupported claim issue

### Requirement: Maintain knowledge indexes
The system SHALL maintain machine-readable indexes for knowledge pages and source relationships.

#### Scenario: Knowledge proposal is generated
- **WHEN** external knowledge is ingested or a dashboard build runs
- **THEN** the system can produce indexes for knowledge pages, source manifest entries, backlinks, tags, and unresolved knowledge gaps

### Requirement: Extend WikiPage frontmatter for growth summaries
The system SHALL support frontmatter fields needed for compiled human-readable growth Wiki pages.

#### Scenario: Growth summary page is created
- **WHEN** the system creates or updates a compiled growth Wiki page
- **THEN** the page contains type, source run ID, source evidence IDs, source raw IDs when applicable, evidence status, confidence, human confirmation state when applicable, tracks, related pages, and generated timestamp
