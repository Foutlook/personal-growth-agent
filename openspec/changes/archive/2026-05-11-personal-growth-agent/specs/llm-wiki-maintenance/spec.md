## ADDED Requirements

### Requirement: Maintain an LLM Wiki workspace
The system SHALL maintain a persistent llm-wiki/ workspace separate from per-run outputs.

#### Scenario: LLM Wiki workspace is initialized
- **WHEN** the system runs and no llm-wiki/ exists
- **THEN** it creates the required top-level structure including AGENTS.md or SCHEMA.md, raw/, wiki/, machine-usable/, diff/, report/, and data/

### Requirement: Preserve raw sources as read-only inputs
The system MUST treat raw sources as immutable after ingestion.

#### Scenario: Raw source already exists
- **WHEN** the system processes a RawSource that already exists
- **THEN** it does not overwrite the existing file and instead creates a new version or records a source manifest entry

### Requirement: Track source manifest entries
The system SHALL maintain SourceManifest records linking original local sources, RawSource entries, evidence IDs, and Wiki updates.

#### Scenario: Raw source is ingested
- **WHEN** a conversation, repository snapshot, growth artifact, or action asset is added to raw/
- **THEN** the system records source ID, raw source ID, original location, ingest time, source type, tool, redaction status, and hash

### Requirement: Generate Wiki pages with frontmatter
The system SHALL generate WikiPage drafts with required frontmatter fields.

#### Scenario: WikiPage draft is created
- **WHEN** the system creates a WikiPage draft
- **THEN** the page contains title, type, status, source_count, source_evidence_ids or source_paths, last_reviewed, sensitivity, confidence, tracks, and related links when applicable

### Requirement: Use diff-first Wiki updates
The system MUST NOT directly overwrite existing wiki/ pages by default.

#### Scenario: Wiki update is needed
- **WHEN** new evidence or growth artifacts should update a WikiPage
- **THEN** the system creates a WikiUpdateProposal with target path, reason, source references, diff path, risk, human review requirement, and proposed status

### Requirement: Support human review states
WikiUpdateProposal records MUST support proposed, approved, rejected, and applied states.

#### Scenario: User has not approved a proposal
- **WHEN** a WikiUpdateProposal is still proposed
- **THEN** the target wiki/ page remains unchanged

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
