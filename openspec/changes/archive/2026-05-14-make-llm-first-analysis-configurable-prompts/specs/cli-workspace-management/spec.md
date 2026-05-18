## ADDED Requirements

### Requirement: Initialize editable prompt directory
The system SHALL initialize an editable prompt directory for scenario prompt overrides.

#### Scenario: Workspace is initialized
- **WHEN** the user runs `pga init`
- **THEN** the workspace contains or references editable prompt files for supported analyzer scenarios

### Requirement: Configure default LLM analysis
The CLI SHALL support configuration for default LLM provider, model, analysis mode, prompt directory, and scenario routing.

#### Scenario: Config file exists
- **WHEN** the CLI starts a run
- **THEN** it loads default LLM and prompt settings from the config before applying command-line overrides

### Requirement: Expose prompt inspection commands
The CLI SHALL expose commands or outputs that help users locate and edit prompt files.

#### Scenario: User inspects prompt path
- **WHEN** the user asks for prompt paths
- **THEN** the CLI prints the workspace prompt directory or prompt file path for the requested scenario
