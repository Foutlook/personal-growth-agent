# growth-knowledge-recall Specification

## Purpose

Define how host AI CLIs search, read, and assemble compact context from Growth Knowledge Hub without loading the full local Wiki into model context.

## Requirements

### Requirement: Search local growth knowledge
The skill SHALL provide a local search command that finds relevant skill-managed Wiki pages from a lightweight index.

#### Scenario: User asks about prior thinking
- **WHEN** the user asks what they previously decided, learned, reviewed, or captured about a topic
- **THEN** the host CLI can call `gkh.py search --query <query>` and receive ranked sanitized matches

#### Scenario: No relevant pages exist
- **WHEN** a query has no matching local Wiki pages
- **THEN** search returns an empty result without fabricating memory

### Requirement: Return compact context packs
The skill SHALL provide a context command that returns a small, sanitized set of relevant snippets for the current task.

#### Scenario: Context is requested
- **WHEN** the host CLI calls `gkh.py context --query <query> --limit <n>`
- **THEN** the command returns no more than the requested number of page titles, paths, types, summaries, highlights, tags, and source IDs

### Requirement: Read selected Wiki pages safely
The skill SHALL allow host CLIs to read a selected local Wiki page by explicit path.

#### Scenario: User requests details from a result
- **WHEN** the host CLI calls `gkh.py read --path <path>` for a specific search result
- **THEN** the command returns sanitized page content and metadata for that page

#### Scenario: Page is local-only
- **WHEN** the selected page is marked `local_only` or contains private-key-like local-only content
- **THEN** the read command withholds the body and returns a local-only placeholder

#### Scenario: Requested path escapes the Wiki
- **WHEN** the requested path resolves outside the local `llm-wiki/`
- **THEN** the read command rejects the request

### Requirement: Avoid full Wiki context dumps
The skill MUST NOT return the entire local Wiki as model context by default.

#### Scenario: Broad query is requested
- **WHEN** the user asks a broad question that could match many pages
- **THEN** the recall workflow returns compact search or context results and lets the host CLI select pages for detail

### Requirement: Maintain a lightweight local index
The skill SHALL maintain or rebuild `llm-wiki/data/index.json` for skill-managed Wiki pages.

#### Scenario: Wiki write completes
- **WHEN** capture, ingest, or review writes Wiki pages
- **THEN** the script updates or rebuilds the local index

#### Scenario: Index command is run
- **WHEN** the host CLI or user runs `gkh.py index`
- **THEN** the script scans eligible Wiki pages and writes deterministic index records with titles, paths, types, tags, summaries, source IDs, hashes, and timestamps

### Requirement: Preserve recall provenance
The skill SHALL include provenance in recall results.

#### Scenario: Context result is returned
- **WHEN** the context command returns a memory item
- **THEN** the item includes page path and source raw IDs so the host CLI can cite where the memory came from

#### Scenario: Result comes from an external summary
- **WHEN** a result represents third-party or external material
- **THEN** the result keeps the local summary separate from the original full content and indicates that details may require source-specific retrieval by the host CLI
