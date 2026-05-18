## ADDED Requirements

### Requirement: Include external knowledge directories in LLM Wiki workspace
The system SHALL include dedicated directories for externally ingested knowledge in the LLM Wiki workspace.

#### Scenario: LLM Wiki workspace is initialized with knowledge ingestion support
- **WHEN** the system initializes `llm-wiki/`
- **THEN** it creates directories for `raw/knowledge/web/`, `raw/knowledge/notes/`, `raw/knowledge/files/`, `raw/knowledge/excerpts/`, `wiki/knowledge/`, `wiki/knowledge/concepts/`, `wiki/knowledge/sources/`, and `wiki/knowledge/gaps/`

### Requirement: Extend WikiPage frontmatter for external knowledge
The system SHALL support frontmatter fields needed for externally ingested knowledge pages.

#### Scenario: Knowledge Wiki proposal is created
- **WHEN** the system creates a WikiPage draft or WikiUpdateProposal from external knowledge
- **THEN** the page metadata includes type, status, source raw IDs or source paths, original URL when present, author or publisher when present, captured date, sensitivity, confidence, review state, tags, related pages, and unresolved questions when present

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
