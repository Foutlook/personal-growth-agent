## Purpose

Define the opt-in, shallow repository analysis used to supplement personal growth evidence for programmer and AI Agent engineering roles.

## Requirements

### Requirement: Require user confirmation before repository analysis
The system MUST NOT scan repositories until the user confirms one or more repository paths.

#### Scenario: Programmer role signal is detected
- **WHEN** the system detects programmer or AI Agent engineering signals
- **THEN** it requests repository path confirmation before repository analysis starts

### Requirement: Limit repository analysis scope
The system SHALL limit MVP repository analysis to Git metadata, directory structure, file type distribution, language distribution, and engineering signal presence.

#### Scenario: Repository path is confirmed
- **WHEN** the user confirms a repository path
- **THEN** the system analyzes commit timing, commit messages, language and file type distribution, top-level structure, test presence, docs presence, CI presence, scripts, config files, and Agent rule files

### Requirement: Avoid deep code review
The system MUST NOT evaluate business code correctness, security vulnerabilities, performance bottlenecks, or detailed style quality in MVP repository analysis.

#### Scenario: Source files are present
- **WHEN** repository source files are found
- **THEN** the system uses them only for file type, language, structure, and high-level engineering signal extraction unless a later capability explicitly allows deeper review

### Requirement: Produce repository evidence pack
The system SHALL produce a repository evidence pack that can be converted into EvidenceItem and EvidenceSignal records.

#### Scenario: Repository analysis completes
- **WHEN** repository analysis finishes
- **THEN** the system outputs repository path, Git summary, structure summary, engineering signals, sensitivity notes, skipped paths, and source references

### Requirement: Handle large repositories safely
The system MUST degrade repository analysis when a repository is too large or contains high-risk content.

#### Scenario: Repository exceeds analysis limits
- **WHEN** repository size, file count, or sensitivity exceeds configured limits
- **THEN** the system restricts analysis to metadata, top-level structure, and sampled safe summaries, and records the limitation in the report

### Requirement: Detect Agent workflow files
The system SHALL detect files that indicate Agent workflow practices.

#### Scenario: Agent rule file exists
- **WHEN** AGENTS.md, CLAUDE.md, opencode configuration, prompt templates, checklist files, or rule files are present
- **THEN** the system records an Agent engineering practice signal for downstream evidence extraction
