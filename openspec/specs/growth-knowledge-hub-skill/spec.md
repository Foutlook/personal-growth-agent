# growth-knowledge-hub-skill Specification

## Purpose

Define the Growth Knowledge Hub skill package: a host-CLI-loadable memory layer for capturing, ingesting, reviewing, recording project lessons, recalling, indexing, and dashboarding local personal growth knowledge.

## Requirements

### Requirement: Provide a host-loadable skill package
The system SHALL provide a `growth-knowledge-hub/` skill package that Codex, Claude Code, OpenCode, or similar host AI CLIs can load without installing this repository as an application package.

#### Scenario: Host CLI scans the skill
- **WHEN** a host CLI scans the skill directory
- **THEN** it can read `SKILL.md`, `skill.json`, workflow references, and the bundled local script

#### Scenario: User asks to preserve growth knowledge
- **WHEN** the user asks to save, capture, 沉淀, 复盘, 整理到学习库, or recall personal growth knowledge
- **THEN** the skill metadata and `SKILL.md` identify Growth Knowledge Hub as the matching workflow

### Requirement: Keep workflow instructions progressively disclosed
The skill SHALL keep `SKILL.md` concise and route detailed instructions into intent-specific reference files.

#### Scenario: Conversation capture is requested
- **WHEN** the host CLI determines the user wants to capture the current discussion
- **THEN** the skill directs the host to `references/conversation-capture.md`

#### Scenario: External material ingestion is requested
- **WHEN** the host CLI determines the user wants to preserve an article, note, third-party knowledge result, or document summary
- **THEN** the skill directs the host to `references/material-ingest.md`

#### Scenario: Growth review is requested
- **WHEN** the host CLI determines the user wants a growth review, weekly review, bottleneck review, or next-action planning
- **THEN** the skill directs the host to `references/growth-review.md`

#### Scenario: Recall is requested
- **WHEN** the user asks what they previously decided, learned, reviewed, or planned
- **THEN** the skill directs the host to `references/recall.md`

#### Scenario: Project analysis is requested
- **WHEN** the user asks to analyze a local project and preserve reusable lessons
- **THEN** the skill directs the host to `references/project-analysis.md`

#### Scenario: Host CLI history analysis is requested
- **WHEN** the user asks to analyze prior Codex, Claude Code, OpenCode, or all supported host CLI conversations
- **THEN** the skill directs the host to a history-analysis reference workflow before invoking `analyze-history`

### Requirement: Bundle a lightweight deterministic script
The skill SHALL bundle `scripts/gkh.py` with Python standard-library-only behavior for local deterministic operations.

#### Scenario: Supported command is run
- **WHEN** the host CLI runs `gkh.py` with `init`, `capture`, `ingest`, `review`, `project`, `analyze-history`, `search`, `read`, `context`, `index`, or `dashboard`
- **THEN** the script performs the requested local operation without importing the removed standalone application package

#### Scenario: Unsupported command is requested
- **WHEN** the host CLI runs an unsupported command
- **THEN** the script returns a non-zero exit code and does not write partial data

### Requirement: Accept host-generated structured input
The skill SHALL rely on the host CLI's model to summarize and structure current conversations, materials, reviews, and project lessons before local persistence.

#### Scenario: Valid structured input is provided
- **WHEN** the host CLI invokes `capture`, `ingest`, `review`, or `project` with valid JSON input
- **THEN** the script validates the input, redacts unsafe content, writes local Wiki artifacts, updates provenance, and rebuilds the local index

#### Scenario: Structured input is invalid
- **WHEN** required fields are missing or malformed
- **THEN** the script rejects the input with a non-zero exit code and avoids partial Wiki writes

### Requirement: Keep intelligence boundaries explicit
The skill MUST NOT implement a standalone chat loop, remote LLM provider registry, host CLI replacement, arbitrary skill runtime, or hidden semantic analyzer.

#### Scenario: Semantic interpretation is needed
- **WHEN** an operation requires summarizing raw content, choosing growth meaning, inspecting files, or deciding tool use
- **THEN** the host CLI performs that reasoning and passes structured input to the skill script

#### Scenario: User expects an agent conversation
- **WHEN** the user continues a natural-language conversation
- **THEN** the host CLI remains the agent and Growth Knowledge Hub remains the local memory layer

### Requirement: Resolve data home outside the skill directory
The skill SHALL store user data outside the installed skill package.

#### Scenario: Explicit data home is configured
- **WHEN** `--home` is passed or `GKH_HOME` is set
- **THEN** the script stores `llm-wiki/`, indexes, write logs, manifests, and dashboard output under that data home

#### Scenario: Project scope is requested
- **WHEN** `--scope project` is used
- **THEN** the script resolves an existing ancestor `.growth-knowledge/` directory or creates `.growth-knowledge/` in the current project

#### Scenario: No data home is configured
- **WHEN** no explicit or project-local data home applies
- **THEN** the script uses `~/.growth-knowledge-hub/`

### Requirement: Capture current conversations as growth knowledge
The skill SHALL support capturing the current host CLI discussion as durable local growth knowledge.

#### Scenario: Conversation capture completes
- **WHEN** valid capture input contains title, summary, decisions, insights, open questions, next actions, growth tracks, and tags
- **THEN** the script writes a raw capture, a human-readable growth page, source manifest entries, write-log entries, and an updated index

### Requirement: Keep current conversation capture separate from history analysis
The skill SHALL keep `capture` scoped to host-generated current conversation input and SHALL use `analyze-history` for explicit historical session scanning.

#### Scenario: Current conversation is captured
- **WHEN** the host CLI invokes `capture` with valid structured input
- **THEN** the script writes only the provided current-conversation capture data and does not scan host CLI history directories

#### Scenario: Historical conversations are analyzed
- **WHEN** the host CLI invokes `analyze-history`
- **THEN** the script follows the explicit history analysis workflow instead of the current conversation capture workflow

### Requirement: Ingest external material as learning knowledge
The skill SHALL support persisting host-summarized external material into the local Wiki without mirroring full third-party content by default.

#### Scenario: Material ingestion completes
- **WHEN** valid material input contains title, source locator, summary points, concepts, application ideas, open questions, and tags
- **THEN** the script writes a summary-first knowledge page, source manifest entries, write-log entries, optional knowledge gap page, and an updated index

#### Scenario: Summary points exceed the policy
- **WHEN** material input contains more than six summary points
- **THEN** the script caps persisted summary points to six

### Requirement: Record growth reviews and next actions
The skill SHALL support writing user-visible growth reviews and task records from host-generated review input.

#### Scenario: Growth review completes
- **WHEN** valid review input contains observations, progress, bottlenecks, knowledge gaps, next tasks, related pages, and tags
- **THEN** the script writes a growth review page, task pages for next tasks, source manifest entries, write-log entries, and an updated index

### Requirement: Record host-generated project lessons
The skill SHALL support writing project-level memory from host-generated project analysis input without scanning repositories itself.

#### Scenario: Project analysis completes
- **WHEN** valid project input contains project name, summary, architecture, decisions, lessons, risks, next actions, source paths, and tags
- **THEN** the script writes raw project analysis, project overview, architecture, decisions, lessons, and risks pages, source manifest entries, write-log entries, and an updated index

#### Scenario: Project code inspection is needed
- **WHEN** project analysis requires reading source files or understanding architecture
- **THEN** the host CLI performs that inspection and passes structured project lessons to the skill script

### Requirement: Preserve privacy and provenance for writes
The skill MUST apply privacy checks and provenance recording before local writes are committed.

#### Scenario: Input contains secrets
- **WHEN** structured input contains API keys, tokens, private keys, email addresses, URLs, or phone numbers
- **THEN** the script redacts safe-to-redact items or rejects local-only private key content before writing

#### Scenario: Wiki page is written
- **WHEN** the script creates or updates a Wiki page
- **THEN** it records source manifest metadata and a direct write-log entry with target path, operation, source raw IDs, content hash, and timestamp
