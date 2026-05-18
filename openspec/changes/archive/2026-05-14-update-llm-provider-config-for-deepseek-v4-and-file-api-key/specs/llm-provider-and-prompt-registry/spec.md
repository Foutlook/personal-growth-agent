## ADDED Requirements

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

## MODIFIED Requirements

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
