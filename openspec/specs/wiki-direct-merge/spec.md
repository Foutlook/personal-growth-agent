# wiki-direct-merge Specification

## Purpose

Define how Growth Knowledge Hub directly writes accepted structured memory into `llm-wiki/wiki/` with append-only provenance.

## Requirements

### Requirement: Directly write accepted Wiki pages
The system SHALL directly write skill-managed capture, material, review, gap, and task pages into `llm-wiki/wiki/`.

#### Scenario: New page is written
- **WHEN** valid structured input maps to a new target path
- **THEN** the script creates the page and records the operation as `create`

#### Scenario: Existing page is written
- **WHEN** valid structured input maps to an existing target path
- **THEN** the script updates the page and records the operation as `update`

### Requirement: Record direct Wiki write provenance
The system SHALL append a machine-readable write record for every direct Wiki write.

#### Scenario: Wiki page is written
- **WHEN** the script creates or updates a Wiki page
- **THEN** it appends an entry to `llm-wiki/data/wiki-write-log.json` with target path, operation, source raw IDs, source evidence IDs, compiler, provider label, content hash, and write timestamp

#### Scenario: Write log already exists
- **WHEN** a new Wiki write occurs and `wiki-write-log.json` already contains entries
- **THEN** the system preserves existing entries and appends the new entry

### Requirement: Preserve raw-source traceability
The system MUST link directly written Wiki pages back to raw sources.

#### Scenario: Page is written from capture, material, or review input
- **WHEN** a Wiki page is created
- **THEN** its frontmatter or body references the source raw IDs used to create the page

### Requirement: Block unsafe direct writes
The system MUST run privacy checks before direct Wiki writes are persisted.

#### Scenario: Unsafe content is detected
- **WHEN** page content contains private-key-like local-only material
- **THEN** the script prevents the write and returns an error

### Requirement: Keep write paths deterministic
The skill-managed direct write path SHALL produce stable target paths from titles.

#### Scenario: Same title and workflow are written repeatedly
- **WHEN** the same valid input title is processed repeatedly
- **THEN** the resulting target path remains stable and the write log records the create or update operation
