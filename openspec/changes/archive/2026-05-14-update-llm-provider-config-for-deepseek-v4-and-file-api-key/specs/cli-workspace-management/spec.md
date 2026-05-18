## MODIFIED Requirements

### Requirement: Configure default LLM analysis
The CLI SHALL support configuration for default LLM provider, model, analysis mode, prompt directory, scenario routing, model presets, and credential sources.

#### Scenario: Config file exists
- **WHEN** the CLI starts a run
- **THEN** it loads default LLM and prompt settings from the config before applying command-line overrides

#### Scenario: Default config is initialized
- **WHEN** the user runs `pga init`
- **THEN** the generated config includes DeepSeek default model `deepseek-v4-flash`, model presets for `flash` and `pro`, an editable `api_key = ""` placeholder, and the configured `api_key_env`

#### Scenario: User edits file API key
- **WHEN** the user writes a DeepSeek API key into the generated `api_key` field
- **THEN** subsequent CLI runs can use that key without requiring a source code change or environment variable update

#### Scenario: Missing API key is reported
- **WHEN** a remote LLM provider is selected and no API key can be resolved
- **THEN** the CLI tells the user which config file field or environment variable to configure before retrying remote analysis
