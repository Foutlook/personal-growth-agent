## ADDED Requirements

### Requirement: Maintain configurable LLM provider registry
The system SHALL maintain provider settings outside of application code.

#### Scenario: Provider config is loaded
- **WHEN** the CLI starts a run
- **THEN** it loads remote provider settings including provider name, base URL, model, API key environment variable, timeout, default analysis mode, and approval policy from local configuration

#### Scenario: DeepSeek provider is configured
- **WHEN** the user configures a DeepSeek-compatible provider
- **THEN** the system can route analyzer requests to the configured DeepSeek official API endpoint without hard-coding credentials

#### Scenario: OpenAI provider is configured
- **WHEN** the user configures an OpenAI-compatible provider with model `gpt-5.4`
- **THEN** the system can route analyzer requests to the configured OpenAI API endpoint while recording model metadata

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
