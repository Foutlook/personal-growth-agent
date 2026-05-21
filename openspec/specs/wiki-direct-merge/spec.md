## Purpose

TBD. Synced from change simplify-llm-wiki-direct-merge.

## Requirements

### Requirement: Directly merge compiled Wiki pages
The system SHALL directly write compiled Wiki content into `llm-wiki/wiki/` without requiring a proposal approval workflow.

#### Scenario: New Wiki page is compiled
- **WHEN** a raw source or growth artifact is compiled into a new Wiki page
- **THEN** the system writes the page directly to the target path under `wiki/`

#### Scenario: Existing Wiki page is compiled
- **WHEN** compiled content targets an existing Wiki page
- **THEN** the system applies the configured direct write operation and records whether the operation created, updated, or overwrote the page

### Requirement: Record direct Wiki write provenance
The system SHALL append a machine-readable write record for every direct Wiki write.

#### Scenario: Wiki page is written
- **WHEN** the system writes a compiled Wiki page
- **THEN** it appends an entry to `llm-wiki/data/wiki-write-log.json` with target path, operation, source raw IDs, source evidence IDs, prompt metadata when available, compiler, provider and model when available, content hash, and write timestamp

#### Scenario: Write log already exists
- **WHEN** a new Wiki write occurs and `wiki-write-log.json` already contains entries
- **THEN** the system preserves existing entries and appends the new entry without rewriting historical records

### Requirement: Preserve raw-source traceability for direct writes
The system MUST link directly written Wiki pages back to raw sources or evidence sources.

#### Scenario: Knowledge Wiki page is directly written
- **WHEN** a knowledge-derived Wiki page is written
- **THEN** the page frontmatter or body references the source raw IDs or source paths used to generate the content

#### Scenario: Growth Wiki summary is directly written
- **WHEN** a growth summary page is written
- **THEN** the page references the source run ID, source evidence IDs, or growth run snapshot used to generate the summary

### Requirement: Block unsafe direct Wiki writes
The system MUST run privacy checks before direct Wiki writes are persisted.

#### Scenario: Compiled page contains unsafe content
- **WHEN** compiled Wiki content contains unredacted secrets, raw code, private identifiers, local-only content, or other unsafe material
- **THEN** the system prevents the Wiki write and records the privacy decision in the run or ingest audit output
