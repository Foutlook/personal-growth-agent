## ADDED Requirements

### Requirement: Provide an installable growth knowledge skill
The system SHALL provide a skill package that host AI CLIs can load to capture, ingest, review, and recall personal growth knowledge.

#### Scenario: Host CLI lists available skills
- **WHEN** Codex, Claude Code, OpenCode, or a similar host CLI scans the installed skill package
- **THEN** the skill exposes metadata with a clear name, description, trigger contexts, and a `SKILL.md` body explaining the growth knowledge workflows

#### Scenario: User asks to preserve growth knowledge
- **WHEN** the user asks to save, capture,沉淀,复盘,整理到学习库, or recall personal growth knowledge
- **THEN** the host CLI can identify this skill as the appropriate workflow entry point

### Requirement: Use progressive workflow references
The skill SHALL keep `SKILL.md` concise and route detailed instructions into workflow-specific reference files.

#### Scenario: Conversation capture is requested
- **WHEN** the host CLI determines the user wants to capture the current discussion
- **THEN** the skill instructs it to read the conversation capture reference before generating structured capture input

#### Scenario: External material ingestion is requested
- **WHEN** the host CLI determines the user wants to save an article, external knowledge result, document, or copied material
- **THEN** the skill instructs it to read the material ingestion reference before generating structured material input

#### Scenario: Growth review is requested
- **WHEN** the host CLI determines the user wants a growth review, weekly review, or next-action planning
- **THEN** the skill instructs it to read the growth review reference before generating structured review input

### Requirement: Bundle lightweight deterministic scripts
The skill SHALL bundle local scripts that can initialize, write, index, recall, and render the local knowledge base without requiring package installation.

#### Scenario: Script is run from the skill directory
- **WHEN** the host CLI runs the bundled script with a supported command
- **THEN** the script executes using its bundled code and Python standard library dependencies without requiring `pip install personal-growth-agent`

#### Scenario: Unsupported command is requested
- **WHEN** the host CLI runs the bundled script with an unknown command
- **THEN** the script returns a non-zero exit code and a user-facing usage message without writing data

### Requirement: Accept host-generated structured input
The skill SHALL rely on the host CLI's model to generate structured JSON inputs from current context and materials.

#### Scenario: Structured capture input is provided
- **WHEN** the host CLI invokes the script with a valid capture JSON input
- **THEN** the script validates the input and writes deterministic local Wiki artifacts without calling a remote model

#### Scenario: Structured input is invalid
- **WHEN** required fields are missing or malformed
- **THEN** the script rejects the input with validation errors and does not create partial Wiki writes

### Requirement: Keep intelligence boundaries explicit
The skill MUST NOT implement a standalone chat loop, remote LLM provider registry, arbitrary skill runtime, or host CLI replacement in first-version workflows.

#### Scenario: User opens the skill workflow
- **WHEN** the host CLI uses the skill
- **THEN** the skill delegates language understanding, current-context summarization, file inspection, and tool orchestration to the host CLI

#### Scenario: Script needs semantic interpretation
- **WHEN** an operation would require summarizing raw content, choosing growth meaning, or analyzing a project semantically
- **THEN** the skill instructs the host CLI to generate structured input rather than making the bundled script perform model calls

### Requirement: Resolve data home outside the skill directory
The skill SHALL store user data outside the installed skill package.

#### Scenario: Explicit data home is configured
- **WHEN** `GKH_HOME` is set
- **THEN** the bundled script stores the `llm-wiki/`, indexes, and dashboard under that directory

#### Scenario: Project-local memory exists
- **WHEN** the current working directory or an ancestor contains `.growth-knowledge/`
- **THEN** the bundled script may use that directory as the project-local data home when the command requests project scope

#### Scenario: No data home is configured
- **WHEN** no explicit or project-local data home applies
- **THEN** the bundled script uses a stable user-level data home outside the skill install directory

### Requirement: Capture current conversations as growth knowledge
The skill SHALL support capturing the current host CLI discussion as durable local growth knowledge.

#### Scenario: Conversation capture completes
- **WHEN** the host CLI provides a valid capture input containing title, summary, decisions, insights, open questions, next actions, tags, and source metadata
- **THEN** the script writes a raw conversation capture, one or more human-readable Wiki pages, source manifest entries, write-log entries, and updated indexes

#### Scenario: Capture contains no useful knowledge
- **WHEN** the host CLI determines the discussion has no durable growth value
- **THEN** the skill may advise answering without writing to the local knowledge base

### Requirement: Ingest external material as durable learning knowledge
The skill SHALL support persisting host-summarized external material into the local Wiki.

#### Scenario: Material ingestion completes
- **WHEN** the host CLI provides a valid material input with source locator, summary points, key concepts, application ideas, open questions, and tags
- **THEN** the script writes a local knowledge page and provenance records without requiring the full original body by default

#### Scenario: Summary points exceed the policy
- **WHEN** material input contains more than six summary points
- **THEN** the script caps or rejects the summary according to the configured summary policy before writing the Wiki page

### Requirement: Record growth reviews and next actions
The skill SHALL support writing user-visible growth reviews and next-action records.

#### Scenario: Growth review completes
- **WHEN** the host CLI provides valid review input with observations, progress, bottlenecks, knowledge gaps, and next tasks
- **THEN** the script writes growth review pages, task pages or task records, manifest entries, write logs, and updated indexes

#### Scenario: Review references prior pages
- **WHEN** review input links existing Wiki pages or prior tasks
- **THEN** the written review preserves those links as local memory context

### Requirement: Preserve privacy and provenance for skill writes
The skill MUST apply privacy checks and provenance recording before local writes are committed.

#### Scenario: Input contains secrets
- **WHEN** structured input contains API keys, tokens, private keys, or other unsafe sensitive content
- **THEN** the script redacts or rejects the content before writing and reports the privacy decision

#### Scenario: Wiki page is written
- **WHEN** the script creates or updates a Wiki page
- **THEN** it records source manifest metadata and a direct write-log entry with target path, operation, source IDs, content hash, and timestamp
