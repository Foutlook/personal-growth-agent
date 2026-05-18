## ADDED Requirements

### Requirement: Keep interactive conversation logs local
The system MUST store interactive conversation logs outside the LLM Wiki and exclude them from Wiki source manifests by default.

#### Scenario: Conversation log is created
- **WHEN** the interactive REPL writes a conversation JSONL file
- **THEN** the file is stored under the resolved workspace `conversations` directory, not under `llm-wiki`

#### Scenario: Wiki manifest is updated by other workflows
- **WHEN** Wiki source manifests are read or written
- **THEN** interactive conversation log files are not added as raw sources unless a future explicit ingestion command requests it

### Requirement: Audit interactive external chat safely
The system SHALL record safe metadata for interactive external chat calls without storing credentials or unsafe raw context.

#### Scenario: External chat call is prepared
- **WHEN** the REPL prepares an outbound chat payload for a non-local provider
- **THEN** the system records provider, model, purpose, payload digest, credential source, and redaction summary without storing plaintext credentials

#### Scenario: Interactive context includes unsafe content
- **WHEN** chat context assembly encounters local-only content, raw source bodies, raw conversation messages, raw code, secrets, or private identifiers
- **THEN** the system omits or redacts that content before preparing the outbound chat payload

### Requirement: Record local tool activity without leaking unsafe data
The system SHALL record interactive local tool calls with sanitized arguments and summarized results.

#### Scenario: Local tool call is logged
- **WHEN** the chat loop executes a local tool
- **THEN** the conversation log records the tool name, sanitized arguments, status, and compact result summary

#### Scenario: Tool result contains unsafe content
- **WHEN** a tool result contains local-only content, secrets, raw code, or private identifiers
- **THEN** the logged result and outbound tool response omit or redact the unsafe content
