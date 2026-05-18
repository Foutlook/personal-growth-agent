## ADDED Requirements

### Requirement: Provide analyzer provider abstraction
The system SHALL analyze evidence through a provider interface that supports local and optional LLM-backed providers.

#### Scenario: Default provider is used
- **WHEN** no provider is configured
- **THEN** the system uses the local provider and makes no external network call

### Requirement: Support local provider
The system MUST support a local provider backed by existing local-rules behavior.

#### Scenario: Local provider runs
- **WHEN** the analyzer provider is `local`
- **THEN** the system extracts local evidence and signals without requiring credentials or outbound payload approval

### Requirement: Support openai-compatible provider
The system SHALL support an openai-compatible provider configured with base URL, model, and API key environment variable name.

#### Scenario: OpenAI-compatible provider is configured
- **WHEN** the user selects `openai-compatible`
- **THEN** the provider reads configured model settings and prepares requests using the provider interface without bypassing privacy gates

### Requirement: Support ollama provider
The system SHALL support an ollama provider for local model analysis.

#### Scenario: Ollama provider is configured
- **WHEN** the user selects `ollama`
- **THEN** the provider uses the configured local Ollama endpoint and model while recording provider metadata in the audit

### Requirement: Support dry-run analysis
The system MUST support a dry-run mode for non-local providers.

#### Scenario: Dry run is requested
- **WHEN** the user runs analysis with `--dry-run`
- **THEN** the system generates outbound payload previews and skips external provider invocation
