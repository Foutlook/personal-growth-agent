## ADDED Requirements

### Requirement: Defer repository knowledge capture to a future skill workflow
The system SHALL treat local repository analysis as a future structured-input workflow rather than a required first-version skill capability.

#### Scenario: User asks to analyze a project in first version
- **WHEN** the user asks the host CLI to analyze a local development project before project-analysis support is implemented
- **THEN** the skill may explain that project analysis is a future workflow and can still capture the discussion or manually provided project summary as ordinary knowledge

#### Scenario: Future project analysis is added
- **WHEN** a later project-analysis workflow is implemented
- **THEN** the host CLI inspects the repository and provides structured project analysis input for the skill scripts to persist under project-specific Wiki pages

### Requirement: Avoid automatic repository scanning from skill scripts in first version
The first-version skill scripts MUST NOT recursively scan local repositories for semantic project knowledge without explicit future workflow support.

#### Scenario: Script is run from a repository
- **WHEN** the bundled script is invoked from a directory that contains source code
- **THEN** it does not treat the repository as analysis input unless the user provides an explicit structured input file for a supported command
