## MODIFIED Requirements

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

### Requirement: Ingest external skill summaries as local Wiki notes
The system SHALL ingest selected external skill knowledge items as user-readable local Wiki summary notes instead of full third-party content mirrors.

#### Scenario: User imports an external skill item summary
- **WHEN** the user selects a third-party knowledge item for local import through an approved connector
- **THEN** the system creates or updates a local Wiki knowledge page containing a human-readable summary note with source provenance and no full third-party body by default

### Requirement: Limit external skill summaries to six bullet points
The system MUST cap generated local summaries for external skill items at six bullet points.

#### Scenario: Summary is generated from external item metadata
- **WHEN** the system writes a local summary note for an external skill item
- **THEN** the summary section contains no more than six bullet points

### Requirement: Retain external skill summaries long term
The system SHALL treat imported external skill summary notes as long-lived local knowledge.

#### Scenario: Remote item changes or disappears
- **WHEN** a previously imported third-party item is no longer available or has changed remotely
- **THEN** the system preserves the local summary note and may annotate freshness or source availability without deleting the note

### Requirement: Avoid implicit full-content persistence
The system MUST NOT persist fetched third-party full content as a raw source or Wiki page unless the user explicitly requests a future full-content ingestion workflow.

#### Scenario: Full content is fetched to answer a question
- **WHEN** the system fetches third-party full content on demand for a user question
- **THEN** the fetched body is used transiently and is not stored as a local raw full-content mirror by default

## ADDED Requirements

### Requirement: Ingest host-summarized material through the skill
The system SHALL accept host-generated structured material summaries as a first-version external material ingestion path.

#### Scenario: Host CLI provides material summary input
- **WHEN** the host CLI has already read an article, document, external knowledge result, or copied material and provides structured material input
- **THEN** the system persists the summary, concepts, application ideas, source locator, provenance, and knowledge gaps into the local Wiki without requiring the script to perform semantic summarization

#### Scenario: Host CLI provides external source locator only
- **WHEN** the source is a third-party item whose full body should not be mirrored
- **THEN** the system writes a summary-first local note with `full_content_policy: fetch_on_demand` or equivalent provenance metadata
