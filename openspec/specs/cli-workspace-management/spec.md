## Purpose

Define installable CLI behavior, workspace configuration, and user-level defaults for Personal Growth Agent.

## Requirements

### Requirement: Provide installable CLI entrypoint
The system SHALL expose an installable `pga` command for running Personal Growth Agent workflows and launching interactive mode.

#### Scenario: CLI is installed
- **WHEN** the package is installed in editable or packaged mode
- **THEN** the user can run `pga --help` and see available commands without using `python -m`

#### Scenario: Interactive entrypoint is launched
- **WHEN** the user runs `pga` without a subcommand
- **THEN** the CLI starts the interactive REPL instead of requiring the user to choose a subcommand first

#### Scenario: Existing subcommands remain available
- **WHEN** the user runs `pga run`, `pga sources scan`, `pga report latest`, `pga wiki path`, `pga dashboard open`, or another existing subcommand
- **THEN** the CLI executes the requested subcommand using the existing workspace and config resolution rules

### Requirement: Initialize user workspace
The system SHALL provide `pga init` to create a default user workspace and configuration file.

#### Scenario: User initializes workspace
- **WHEN** the user runs `pga init`
- **THEN** the system creates a user-level workspace, default `llm-wiki/`, `runs/`, and config file unless they already exist

### Requirement: Resolve workspace and wiki paths predictably
The system MUST resolve workspace and Wiki paths from command flags, config, environment variables, and defaults in a deterministic order.

#### Scenario: Explicit wiki path is provided
- **WHEN** the user passes `--wiki <path>`
- **THEN** the system uses that Wiki path instead of the configured or default Wiki path

### Requirement: Provide core user commands
The CLI SHALL provide commands for run, source scan, latest report, Wiki path discovery, and prompt-driven Wiki compilation.

#### Scenario: User inspects current setup
- **WHEN** the user runs `pga wiki path` or `pga report latest`
- **THEN** the CLI prints the resolved Wiki path or latest report path without running a new analysis

#### Scenario: User compiles raw sources into Wiki
- **WHEN** the user runs `pga wiki compile --raw <path> --prompt <path>`
- **THEN** the CLI compiles the selected raw sources with the selected prompt, writes Wiki pages directly, and prints a summary of written target paths

### Requirement: Store configuration locally
The system SHALL store user configuration in a local TOML file.

#### Scenario: Config file exists
- **WHEN** the CLI starts
- **THEN** it loads workspace, Wiki path, source paths, provider settings, and default analysis mode from the config file

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

### Requirement: Provide dashboard CLI commands
The CLI SHALL provide commands for building and opening the static dashboard.

#### Scenario: User builds dashboard
- **WHEN** the user runs `pga dashboard build`
- **THEN** the CLI generates the static dashboard under the resolved workspace and prints the dashboard entry file path

#### Scenario: User opens dashboard
- **WHEN** the user runs `pga dashboard open`
- **THEN** the CLI opens or prints the resolved dashboard entry file path without starting a server

### Requirement: Respect existing workspace resolution
Knowledge ingest, Wiki compile, and dashboard commands MUST use the same workspace, config, and Wiki path resolution rules as existing CLI commands.

#### Scenario: Explicit wiki path is provided
- **WHEN** the user runs an ingest, wiki compile, or dashboard command with `--wiki <path>`
- **THEN** the command uses that Wiki path instead of configured or default paths

### Requirement: Initialize editable prompt directory
The system SHALL initialize an editable prompt directory for scenario prompt overrides.

#### Scenario: Workspace is initialized
- **WHEN** the user runs `pga init`
- **THEN** the workspace contains or references editable prompt files for supported analyzer scenarios

### Requirement: Configure default LLM analysis
The CLI SHALL support configuration for default LLM provider, model, analysis mode, prompt directory, scenario routing, model presets, and credential sources.

#### Scenario: Config file exists
- **WHEN** the CLI starts a run
- **THEN** it loads default LLM and prompt settings from the config before applying command-line overrides

#### Scenario: Default config is initialized
- **WHEN** the user runs `pga init`
- **THEN** the generated config includes DeepSeek default model `deepseek-v4-flash`, model presets for `flash` and `pro`, an editable `api_key = ""` placeholder, and the configured `api_key_env`

#### Scenario: User edits file API key
- **WHEN** the user writes a DeepSeek API key into the generated `api_key` field
- **THEN** subsequent CLI runs can use that key without requiring a source code change or environment variable update

#### Scenario: Missing API key is reported
- **WHEN** a remote LLM provider is selected and no API key can be resolved
- **THEN** the CLI tells the user which config file field or environment variable to configure before retrying remote analysis

### Requirement: Expose prompt inspection commands
The CLI SHALL expose commands or outputs that help users locate and edit prompt files.

#### Scenario: User inspects prompt path
- **WHEN** the user asks for prompt paths
- **THEN** the CLI prints the workspace prompt directory or prompt file path for the requested scenario
