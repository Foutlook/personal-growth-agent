## ADDED Requirements

### Requirement: Route interactive chat through configured providers
The system SHALL use the configured LLM provider registry for interactive chat requests.

#### Scenario: Interactive chat starts
- **WHEN** the REPL prepares a free-form chat request
- **THEN** the system resolves provider, model, base URL, timeout, model presets, and credentials from the same local LLM provider configuration used by other LLM workflows

#### Scenario: Chat credential is missing
- **WHEN** the resolved chat provider requires a credential and no file or environment credential is available
- **THEN** the system skips the remote call and returns a user-facing configuration message without exposing any secret value

### Requirement: Support streaming interactive responses
The system SHALL support streaming assistant output for interactive chat when the selected provider supports streaming.

#### Scenario: Provider streams chat output
- **WHEN** the provider returns incremental chat response chunks
- **THEN** the system forwards assistant text chunks to the REPL as they arrive

#### Scenario: Provider does not stream chat output
- **WHEN** the selected provider or transport cannot stream
- **THEN** the system returns the final assistant response through the same REPL interface

### Requirement: Preserve tool-call metadata for interactive chat
The system SHALL preserve local tool-call requests and results as structured metadata for interactive chat.

#### Scenario: Provider requests a local tool
- **WHEN** an interactive chat response includes a tool call
- **THEN** the system exposes the tool name, sanitized arguments, and tool call identifier to the interactive tool dispatcher

#### Scenario: Tool result is sent back to chat
- **WHEN** a local tool finishes
- **THEN** the system returns a compact tool result to the chat loop without exposing raw secrets, raw code, or local-only content
