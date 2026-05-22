## ADDED Requirements

### Requirement: Search local growth knowledge
The skill SHALL provide a local search workflow that lets host CLIs find relevant Wiki pages without reading the entire knowledge base.

#### Scenario: User asks about prior thinking
- **WHEN** the user asks what they previously decided, learned, reviewed, or captured about a topic
- **THEN** the host CLI can call the recall search command with the user's query and receive ranked, sanitized matches

#### Scenario: No relevant pages exist
- **WHEN** a search query has no matching local Wiki pages or indexes
- **THEN** the recall command returns an empty result with a clear message and does not fabricate memory

### Requirement: Return compact context packs
The skill SHALL provide a context command that returns a small, sanitized set of relevant memory snippets for the current task.

#### Scenario: Context is requested for a task
- **WHEN** the host CLI calls the context command with a query and limit
- **THEN** the command returns page titles, paths, types, summaries, highlights, tags, and source metadata suitable for model context

#### Scenario: Context limit is provided
- **WHEN** a limit is specified
- **THEN** the command returns no more than that number of context items

### Requirement: Read selected Wiki pages safely
The skill SHALL allow host CLIs to read selected local Wiki pages by explicit path or ID.

#### Scenario: User requests details from a result
- **WHEN** the host CLI calls the read command for a specific search result path
- **THEN** the command returns sanitized page content and metadata for that page

#### Scenario: Page is local-only
- **WHEN** the selected page is marked local_only or contains local-only sensitivity
- **THEN** the read command withholds the body or returns a local-only placeholder unless an explicit future workflow permits local-only reads

### Requirement: Avoid full Wiki context dumps
The skill MUST NOT return the entire local Wiki as model context by default.

#### Scenario: Broad query is requested
- **WHEN** the user asks a broad question that could match many pages
- **THEN** the recall workflow returns compact search or context results and asks the host CLI to narrow or read selected pages for detail

#### Scenario: Host CLI asks for all pages
- **WHEN** a command attempts to read all Wiki pages into one response
- **THEN** the skill rejects or truncates the request according to recall limits

### Requirement: Index skill-managed knowledge
The skill SHALL maintain or rebuild a lightweight local index for skill-managed Wiki pages.

#### Scenario: Wiki write completes
- **WHEN** capture, ingest, review, or project analysis writes Wiki pages
- **THEN** the script updates the local index or marks it rebuildable

#### Scenario: Index command is run
- **WHEN** the host CLI or user runs the index command
- **THEN** the script scans eligible Wiki pages and writes a deterministic index with titles, paths, types, tags, summaries, hashes, and timestamps

### Requirement: Preserve recall provenance
The skill SHALL include provenance in recall results.

#### Scenario: Context result is returned
- **WHEN** the context command returns a memory item
- **THEN** the item includes enough page path, source IDs, source locator, or write-log metadata for the host CLI to cite where the memory came from

#### Scenario: Recall result uses external material summary
- **WHEN** a result comes from an external material or external skill summary page
- **THEN** the result indicates that full original content is not persisted by default and may require source-specific retrieval outside the local Wiki
