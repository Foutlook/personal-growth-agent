## Purpose

Define the interactive terminal REPL experience for Personal Growth Agent, including slash commands, streaming chat, controlled local tool calls, and local conversation retention.

## Requirements

### Requirement: Launch interactive REPL
The system SHALL provide an interactive terminal REPL for Personal Growth Agent.

#### Scenario: User starts interactive mode
- **WHEN** the user runs `pga` without a subcommand
- **THEN** the system enters an interactive terminal session using the resolved workspace, Wiki path, and configuration

#### Scenario: User exits interactive mode
- **WHEN** the user enters `/exit` or `/quit`
- **THEN** the system ends the interactive session without running additional analysis

### Requirement: Route slash commands locally
The interactive REPL MUST route inputs beginning with `/` to deterministic local command handlers instead of sending them to the LLM.

#### Scenario: User lists local commands
- **WHEN** the user enters `/help`
- **THEN** the system displays the available interactive commands

#### Scenario: User lists growth tasks
- **WHEN** the user enters `/tasks`
- **THEN** the system displays active growth tasks from the resolved workspace

#### Scenario: User completes a growth task
- **WHEN** the user enters `/task complete <task-id>`
- **THEN** the system marks the matching task completed using the same task archive behavior as the CLI task completion command

#### Scenario: User inspects knowledge indexes
- **WHEN** the user enters `/wiki` or `/gaps`
- **THEN** the system displays the Wiki page index or knowledge gap index from local workspace data

#### Scenario: User runs common workflows
- **WHEN** the user enters `/summary`, `/run`, or `/dashboard`
- **THEN** the system executes the corresponding local report summary, growth cycle run, or dashboard open workflow

### Requirement: Support free-form streaming chat
The interactive REPL SHALL send non-command user input to the configured LLM provider as free-form chat and stream assistant output to the terminal.

#### Scenario: User asks a free-form question
- **WHEN** the user enters text that does not begin with `/`
- **THEN** the system sends an interactive chat request using the configured default provider and model
- **AND** the system displays the assistant response incrementally as streamed content is received

#### Scenario: Chat provider credentials are missing
- **WHEN** the configured non-local provider has no resolvable API key
- **THEN** the system displays a configuration message naming the missing config field or environment variable

### Requirement: Allow chat to call whitelisted local tools
The interactive chat loop SHALL expose only approved local tools to the LLM.

#### Scenario: LLM requests an approved read tool
- **WHEN** the LLM requests `get_latest_report`, `list_growth_tasks`, `list_wiki_pages`, `read_wiki_page`, or `list_knowledge_gaps`
- **THEN** the system executes the local tool and returns a compact result to the chat loop

#### Scenario: LLM requests an approved action tool
- **WHEN** the LLM requests `complete_growth_task`, `run_growth_cycle`, or `build_open_dashboard`
- **THEN** the system executes the controlled local action and records the tool call in the conversation log

#### Scenario: LLM requests an unapproved tool
- **WHEN** the LLM requests any tool outside the approved whitelist
- **THEN** the system rejects the tool call and records the rejection in the conversation log

### Requirement: Store interactive conversation records locally
The system SHALL persist interactive conversation records under the resolved workspace outside the LLM Wiki.

#### Scenario: Interactive session records messages
- **WHEN** a user message, assistant response, tool call, tool result, or chat error occurs
- **THEN** the system appends a JSONL record under `<workspace>/conversations/YYYY-MM-DD/<session-id>.jsonl`

#### Scenario: Conversation records stay out of Wiki
- **WHEN** an interactive conversation record is written
- **THEN** the system does not create or update any `llm-wiki/raw`, `llm-wiki/wiki`, or Wiki source manifest entry for that conversation record
