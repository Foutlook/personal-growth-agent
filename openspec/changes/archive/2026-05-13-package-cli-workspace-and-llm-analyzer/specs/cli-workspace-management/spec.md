## ADDED Requirements

### Requirement: Provide installable CLI entrypoint
The system SHALL expose an installable `pga` command for running Personal Growth Agent workflows.

#### Scenario: CLI is installed
- **WHEN** the package is installed in editable or packaged mode
- **THEN** the user can run `pga --help` and see available commands without using `python -m`

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
The CLI SHALL provide commands for run, source scan, latest report, and Wiki path discovery.

#### Scenario: User inspects current setup
- **WHEN** the user runs `pga wiki path` or `pga report latest`
- **THEN** the CLI prints the resolved Wiki path or latest report path without running a new analysis

### Requirement: Store configuration locally
The system SHALL store user configuration in a local TOML file.

#### Scenario: Config file exists
- **WHEN** the CLI starts
- **THEN** it loads workspace, Wiki path, source paths, provider settings, and default analysis mode from the config file
