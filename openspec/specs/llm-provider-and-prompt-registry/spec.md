## Purpose

Define how the system manages configurable remote LLM providers, scenario prompt files, prompt routing, and prompt provenance outside of application code.

## Requirements

### Requirement: Maintain configurable LLM provider registry
The system SHALL maintain provider settings outside of application code.

#### Scenario: Provider config is loaded
- **WHEN** the CLI starts a run
- **THEN** it loads remote provider settings including provider name, base URL, model, model presets, direct API key value, API key environment variable, timeout, default analysis mode, and approval policy from local configuration

#### Scenario: DeepSeek provider is configured
- **WHEN** the user configures a DeepSeek-compatible provider
- **THEN** the system can route analyzer requests to the configured DeepSeek official API endpoint with DeepSeek v4 model IDs and without hard-coding credentials

#### Scenario: OpenAI provider is configured
- **WHEN** the user configures an OpenAI-compatible provider with model `gpt-5.4`
- **THEN** the system can route analyzer requests to the configured OpenAI API endpoint while recording model metadata

### Requirement: Maintain provider model presets
The system SHALL maintain provider-specific model presets outside of application code.

#### Scenario: DeepSeek model presets are loaded
- **WHEN** the CLI loads LLM provider configuration
- **THEN** the DeepSeek provider exposes `flash` as `deepseek-v4-flash` and `pro` as `deepseek-v4-pro`

#### Scenario: DeepSeek preset is selected
- **WHEN** the user configures DeepSeek model `flash` or `pro`
- **THEN** the system resolves the preset to the corresponding DeepSeek v4 model ID before preparing the analyzer request

### Requirement: Resolve provider credentials deterministically
The system MUST resolve remote provider credentials without hard-coding secrets.

#### Scenario: File API key is configured
- **WHEN** `api_key` is present and non-empty in provider configuration
- **THEN** the system uses that value as the credential source for the provider request

#### Scenario: Environment API key is configured
- **WHEN** `api_key` is empty and `api_key_env` points to a populated environment variable
- **THEN** the system uses the environment variable value as the credential source for the provider request

#### Scenario: Provider credential is missing
- **WHEN** neither `api_key` nor the configured `api_key_env` resolves to a value
- **THEN** the system marks the provider credential as missing and returns a user-facing configuration message naming the config file field and environment variable option

### Requirement: Maintain scenario prompt registry
The system SHALL maintain named prompt files outside of application code.

#### Scenario: Prompt registry is initialized
- **WHEN** the workspace is initialized
- **THEN** the system creates or references prompt files for role profile, maturity scoring, growth planning, evidence enrichment, knowledge ingestion, Wiki maintenance, and report generation

#### Scenario: Workspace prompt overrides package prompt
- **WHEN** a scenario prompt exists in the workspace prompt directory
- **THEN** the system uses that prompt instead of the package default prompt for the same scenario

### Requirement: Route analysis scenarios to prompts
The system SHALL select prompts by scenario instead of using one generic analyzer prompt.

#### Scenario: Role analysis runs
- **WHEN** the system performs role inference
- **THEN** it uses the configured role profile prompt and expected output schema

#### Scenario: Growth planning runs
- **WHEN** the system generates growth tasks
- **THEN** it uses the configured growth planning prompt and expected output schema

### Requirement: Track prompt identity and version
The system MUST record prompt identity and version for every LLM analyzer request.

#### Scenario: LLM request is prepared
- **WHEN** the system prepares a prompt for a scenario
- **THEN** the outbound preview and analyzer audit include prompt ID, prompt version, scenario, provider, and model

### Requirement: Support prompt editing without code changes
The system MUST allow users to modify scenario prompts without editing Python source files.

#### Scenario: User edits workspace prompt
- **WHEN** the user changes a workspace prompt file
- **THEN** subsequent runs use the updated prompt content and record the new prompt digest

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
