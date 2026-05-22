## ADDED Requirements

### Requirement: De-emphasize standalone interactive REPL for skill workflows
The system SHALL treat host AI CLIs as the primary conversational interface for growth knowledge workflows.

#### Scenario: User installs the growth knowledge skill
- **WHEN** the user wants conversational capture, ingestion, review, or recall
- **THEN** the documented primary path is to use Codex, Claude Code, OpenCode, or a similar host CLI with the skill loaded

#### Scenario: Standalone REPL remains present during migration
- **WHEN** legacy `pga` interactive mode still exists
- **THEN** it is documented as non-primary for the redesigned skill-first workflow and MUST NOT be required for skill usage

### Requirement: Avoid building a new skill runtime in the REPL
The standalone REPL MUST NOT become the first-version runtime for loading arbitrary configured skills.

#### Scenario: Multiple host skills are installed
- **WHEN** the user wants a CLI that can load and orchestrate many skills
- **THEN** the system relies on mature host CLIs rather than implementing a parallel skill manager inside this project
