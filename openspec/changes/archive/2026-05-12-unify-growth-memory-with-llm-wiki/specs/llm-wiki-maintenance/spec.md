## ADDED Requirements

### Requirement: Include growth memory directories in LLM Wiki workspace
The system SHALL include dedicated growth memory locations in the LLM Wiki workspace.

#### Scenario: LLM Wiki workspace is initialized with growth memory support
- **WHEN** the system initializes `llm-wiki/`
- **THEN** it creates directories for `raw/growth-runs/`, `raw/growth-reviews/`, `wiki/profile/`, `wiki/growth/cycles/`, `wiki/growth/tasks/`, `wiki/growth/diagnoses/`, `wiki/growth/reviews/`, `wiki/growth/maturity-snapshots/`, and `wiki/cases/`

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
