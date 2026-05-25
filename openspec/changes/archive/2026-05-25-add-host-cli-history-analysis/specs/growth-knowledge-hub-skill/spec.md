## MODIFIED Requirements

### Requirement: Bundle a lightweight deterministic script
The skill SHALL bundle `scripts/gkh.py` with Python standard-library-only behavior for local deterministic operations.

#### Scenario: Supported command is run
- **WHEN** the host CLI runs `gkh.py` with `init`, `capture`, `ingest`, `review`, `project`, `analyze-history`, `search`, `read`, `context`, `index`, or `dashboard`
- **THEN** the script performs the requested local operation without importing the removed standalone application package

#### Scenario: Unsupported command is requested
- **WHEN** the host CLI runs an unsupported command
- **THEN** the script returns a non-zero exit code and does not write partial data

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

## ADDED Requirements

### Requirement: Keep current conversation capture separate from history analysis
The skill SHALL keep `capture` scoped to host-generated current conversation input and SHALL use `analyze-history` for explicit historical session scanning.

#### Scenario: Current conversation is captured
- **WHEN** the host CLI invokes `capture` with valid structured input
- **THEN** the script writes only the provided current-conversation capture data and does not scan host CLI history directories

#### Scenario: Historical conversations are analyzed
- **WHEN** the host CLI invokes `analyze-history`
- **THEN** the script follows the explicit history analysis workflow instead of the current conversation capture workflow
