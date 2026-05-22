## ADDED Requirements

### Requirement: Avoid first-version dependency on project-owned LLM routing for skill workflows
The growth knowledge skill SHALL NOT require the project-owned LLM provider registry to perform first-version capture, ingest, review, or recall workflows.

#### Scenario: Host CLI captures current conversation
- **WHEN** Codex, Claude Code, OpenCode, or a similar host CLI uses its own configured model to generate structured input
- **THEN** the skill scripts persist that input without resolving this project's provider, model, prompt, or API key configuration

#### Scenario: No project LLM credentials exist
- **WHEN** the user has not configured DeepSeek, OpenAI, or other project-owned provider credentials
- **THEN** the skill capture, ingest, review, search, read, context, and dashboard workflows can still run locally

### Requirement: Keep skill prompts as skill references
The skill SHALL express workflow prompting guidance in `SKILL.md` and reference Markdown files instead of requiring editable project prompt registry entries for first-version workflows.

#### Scenario: Host CLI needs capture guidance
- **WHEN** the host CLI needs instructions for generating capture JSON
- **THEN** it reads the skill reference file for that workflow rather than loading a project prompt registry
