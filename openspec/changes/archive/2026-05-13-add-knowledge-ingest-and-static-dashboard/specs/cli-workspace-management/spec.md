## ADDED Requirements

### Requirement: Provide knowledge ingest CLI commands
The CLI SHALL provide user-facing commands for external knowledge ingestion.

#### Scenario: User ingests note content
- **WHEN** the user runs a note ingest command with content or stdin input
- **THEN** the CLI stores the note in the resolved LLM Wiki and prints the raw source ID or path

#### Scenario: User ingests a local file
- **WHEN** the user runs a file ingest command with a local file path
- **THEN** the CLI stores the file snapshot in the resolved LLM Wiki and prints the raw source ID or path

#### Scenario: User ingests article content
- **WHEN** the user runs a web or article ingest command with copied content and source metadata
- **THEN** the CLI stores the snapshot in the resolved LLM Wiki and records source manifest metadata

### Requirement: Provide dashboard CLI commands
The CLI SHALL provide commands for building and opening the static dashboard.

#### Scenario: User builds dashboard
- **WHEN** the user runs `pga dashboard build`
- **THEN** the CLI generates the static dashboard under the resolved workspace and prints the dashboard entry file path

#### Scenario: User opens dashboard
- **WHEN** the user runs `pga dashboard open`
- **THEN** the CLI opens or prints the resolved dashboard entry file path without starting a server

### Requirement: Respect existing workspace resolution
Knowledge ingest and dashboard commands MUST use the same workspace, config, and Wiki path resolution rules as existing CLI commands.

#### Scenario: Explicit wiki path is provided
- **WHEN** the user runs an ingest or dashboard command with `--wiki <path>`
- **THEN** the command uses that Wiki path instead of configured or default paths
