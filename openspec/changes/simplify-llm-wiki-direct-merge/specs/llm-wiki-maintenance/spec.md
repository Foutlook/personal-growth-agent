## MODIFIED Requirements

### Requirement: Maintain an LLM Wiki workspace
The system SHALL maintain a persistent llm-wiki/ workspace separate from per-run outputs.

#### Scenario: LLM Wiki workspace is initialized
- **WHEN** the system runs and no llm-wiki/ exists
- **THEN** it creates the required top-level structure including AGENTS.md or SCHEMA.md, raw/, wiki/, machine-usable/, prompts or prompt references, report/, and data/

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

### Requirement: Include growth memory directories in LLM Wiki workspace
The system SHALL include dedicated growth memory locations in the LLM Wiki workspace while keeping automatic machine state out of the human-readable Wiki layer.

#### Scenario: LLM Wiki workspace is initialized with growth memory support
- **WHEN** the system initializes `llm-wiki/`
- **THEN** it creates directories for `raw/growth-runs/`, `raw/growth-reviews/`, `data/growth-memory/`, `wiki/profile/`, `wiki/growth/`, `wiki/growth/reviews/`, and `wiki/cases/`

### Requirement: Extend WikiPage frontmatter for growth summaries
The system SHALL support frontmatter fields needed for compiled human-readable growth Wiki pages.

#### Scenario: Growth summary page is created
- **WHEN** the system creates or updates a compiled growth Wiki page
- **THEN** the page contains type, source run ID, source evidence IDs, source raw IDs when applicable, evidence status, confidence, human confirmation state when applicable, tracks, related pages, and generated timestamp

### Requirement: Extend WikiPage frontmatter for external knowledge
The system SHALL support frontmatter fields needed for externally ingested knowledge pages.

#### Scenario: Knowledge Wiki page is directly written
- **WHEN** the system creates or updates a WikiPage from external knowledge
- **THEN** the page metadata includes type, status, source raw IDs or source paths, original URL when present, author or publisher when present, captured date, sensitivity, confidence, tags, related pages, unresolved questions when present, and generated timestamp

## REMOVED Requirements

### Requirement: Use diff-first Wiki updates
**Reason**: The product no longer requires a review gate before Wiki writes. Direct merge with write-log provenance is the chosen workflow.

**Migration**: Replace WikiUpdateProposal creation with direct Wiki writes and append-only write-log entries. Existing diff/proposal artifacts may remain readable as historical data but are no longer required for new writes.

### Requirement: Support human review states
**Reason**: The direct-merge workflow does not use proposed, approved, rejected, or applied states for Wiki writes.

**Migration**: Dashboard and audit views should show write-log entries, source references, and lint status instead of proposal review status.
