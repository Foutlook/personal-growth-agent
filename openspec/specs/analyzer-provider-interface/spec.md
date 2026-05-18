## Purpose

Define the analyzer provider abstraction for local and optional LLM-backed analysis.

## Requirements

### Requirement: Provide analyzer provider abstraction
The system SHALL analyze evidence through a provider interface that supports LLM-first remote providers and local fallback providers.

#### Scenario: Default provider is used
- **WHEN** no provider override is passed on the command line
- **THEN** the system uses the configured default LLM provider and configured default analysis mode

#### Scenario: Default provider lacks approval
- **WHEN** the configured default provider is remote and outbound approval is missing
- **THEN** the system writes outbound previews and falls back to local rules instead of calling the remote provider

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

#### Scenario: GPT-5.4 model is configured
- **WHEN** the user configures model `gpt-5.4`
- **THEN** the provider records that model ID in request metadata, outbound preview, validation records, and audit output

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

### Requirement: Support DeepSeek provider
The system SHALL support a DeepSeek remote provider configured with official API endpoint, v4 model ID or preset, direct API key value, API key environment variable, and timeout.

#### Scenario: DeepSeek provider is configured
- **WHEN** the user selects `deepseek`
- **THEN** the provider prepares an analyzer request using configured DeepSeek settings without hard-coding credentials

#### Scenario: DeepSeek default model is used
- **WHEN** the user selects `deepseek` without a model override
- **THEN** the provider uses `deepseek-v4-flash` as the default model

#### Scenario: DeepSeek pro model is configured
- **WHEN** the user configures DeepSeek model `pro` or `deepseek-v4-pro`
- **THEN** the provider prepares the analyzer request with model `deepseek-v4-pro`

#### Scenario: DeepSeek credential is missing
- **WHEN** the user selects `deepseek` and no credential is available from `api_key` or `api_key_env`
- **THEN** the provider skips the remote call, emits a clear configuration message, and returns control to the configured fallback path

### Requirement: Preserve provider override order
The system MUST resolve analyzer provider settings deterministically from command flags, scenario config, workspace config, environment variables, and package defaults.

#### Scenario: Command provider is supplied
- **WHEN** the user passes a provider or model flag on the command line
- **THEN** that value overrides scenario and workspace defaults for the current run
