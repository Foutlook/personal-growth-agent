## Purpose

Define how the system ingests user-provided external knowledge sources into the LLM Wiki while preserving local-first traceability, direct-merge provenance, and privacy boundaries.

## Requirements

### Requirement: Ingest explicit external knowledge sources
The system SHALL ingest user-provided external knowledge sources as first-class LLM Wiki raw inputs.

#### Scenario: User ingests a note
- **WHEN** the user provides note content through a note ingest command
- **THEN** the system stores the content as an immutable raw knowledge source with source metadata, hash, sensitivity state, and ingest timestamp

#### Scenario: User ingests a local file
- **WHEN** the user provides a supported local text or Markdown file through a file ingest command
- **THEN** the system copies the source into the Wiki raw knowledge area without modifying the original file

#### Scenario: User ingests article text with an origin URL
- **WHEN** the user provides copied article text and an origin URL
- **THEN** the system records both the immutable article snapshot and the original URL in the source manifest

### Requirement: Keep external fetch explicit
The system MUST NOT perform hidden network fetching during knowledge ingestion.

#### Scenario: URL is provided without fetch approval
- **WHEN** the user provides only a URL and does not explicitly request fetching
- **THEN** the system records URL metadata or prompts for copied content without attempting a network request

#### Scenario: Fetch is explicitly requested
- **WHEN** the user requests URL fetching with an explicit fetch option
- **THEN** the system records the fetch time, final URL, content hash, and fetch status in the source manifest

### Requirement: Classify knowledge source types
The system SHALL classify external knowledge sources by source type.

#### Scenario: Knowledge source is stored
- **WHEN** external knowledge is ingested
- **THEN** the source manifest records a source type such as web_article, public_account_article, user_note, local_document, copied_excerpt, or reference_material

### Requirement: Compile ingested knowledge directly into Wiki pages
The system SHALL compile ingested knowledge directly into Wiki pages while preserving raw source traceability and write provenance.

#### Scenario: Knowledge maps to an existing page
- **WHEN** an ingested source is relevant to an existing Wiki page
- **THEN** the system directly updates the target Wiki page with source references and records the write in `data/wiki-write-log.json`

#### Scenario: Knowledge has no matching page
- **WHEN** an ingested source introduces a topic not represented in the Wiki
- **THEN** the system directly creates a new Wiki page under an appropriate knowledge category with source references and write-log provenance

### Requirement: Preserve source traceability for knowledge claims
The system MUST link every generated knowledge claim to raw source references.

#### Scenario: Knowledge Wiki page contains a claim
- **WHEN** the system writes a knowledge-derived Wiki page
- **THEN** the page includes source raw IDs or source paths for the claim

### Requirement: Support knowledge gap extraction
The system SHALL identify reusable knowledge gaps from ingested external sources and existing Wiki state.

#### Scenario: Knowledge source raises unresolved questions
- **WHEN** ingested knowledge includes uncertain concepts, missing prerequisites, or follow-up questions
- **THEN** the system records knowledge gaps as directly written Wiki content or machine-readable dashboard data with raw source references
