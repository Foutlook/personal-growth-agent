## MODIFIED Requirements

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
