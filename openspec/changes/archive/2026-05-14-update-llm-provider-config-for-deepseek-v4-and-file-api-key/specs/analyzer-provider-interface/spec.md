## MODIFIED Requirements

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
