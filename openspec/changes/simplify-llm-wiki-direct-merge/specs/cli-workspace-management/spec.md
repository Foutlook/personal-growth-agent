## MODIFIED Requirements

### Requirement: Provide core user commands
The CLI SHALL provide commands for run, source scan, latest report, Wiki path discovery, and prompt-driven Wiki compilation.

#### Scenario: User inspects current setup
- **WHEN** the user runs `pga wiki path` or `pga report latest`
- **THEN** the CLI prints the resolved Wiki path or latest report path without running a new analysis

#### Scenario: User compiles raw sources into Wiki
- **WHEN** the user runs `pga wiki compile --raw <path> --prompt <path>`
- **THEN** the CLI compiles the selected raw sources with the selected prompt, writes Wiki pages directly, and prints a summary of written target paths

### Requirement: Provide knowledge ingest CLI commands
The CLI SHALL provide user-facing commands for external knowledge ingestion and direct Wiki compilation.

#### Scenario: User ingests note content
- **WHEN** the user runs a note ingest command with content or stdin input
- **THEN** the CLI stores the note in the resolved LLM Wiki, compiles the knowledge into Wiki when configured, and prints the raw source ID or written Wiki path

#### Scenario: User ingests a local file
- **WHEN** the user runs a file ingest command with a local file path
- **THEN** the CLI stores the file snapshot in the resolved LLM Wiki, compiles the knowledge into Wiki when configured, and prints the raw source ID or written Wiki path

#### Scenario: User ingests article content
- **WHEN** the user runs a web or article ingest command with copied content and source metadata
- **THEN** the CLI stores the snapshot in the resolved LLM Wiki, records source manifest metadata, compiles the knowledge into Wiki when configured, and records write provenance

### Requirement: Respect existing workspace resolution
Knowledge ingest, Wiki compile, and dashboard commands MUST use the same workspace, config, and Wiki path resolution rules as existing CLI commands.

#### Scenario: Explicit wiki path is provided
- **WHEN** the user runs an ingest, wiki compile, or dashboard command with `--wiki <path>`
- **THEN** the command uses that Wiki path instead of configured or default paths
