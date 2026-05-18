## ADDED Requirements

### Requirement: Audit prompt and provider routing
The system SHALL include prompt and provider routing metadata in privacy audit outputs.

#### Scenario: Remote LLM request is prepared
- **WHEN** the system prepares an outbound LLM request
- **THEN** the privacy audit records scenario, prompt ID, prompt version, prompt digest, provider, model, payload digest, approval state, and dry-run state

### Requirement: Audit remote provider decisions
The system SHALL record why a remote provider was called or skipped.

#### Scenario: Remote provider is skipped
- **WHEN** remote provider invocation is skipped due to missing approval, dry-run, privacy risk, validation failure, or missing credentials
- **THEN** the audit records the skip reason and fallback mode

### Requirement: Exclude unsafe prompt context
The system MUST exclude unsafe prompt context from remote LLM payloads.

#### Scenario: Prompt context includes local-only evidence
- **WHEN** prompt context is assembled for a remote provider
- **THEN** local-only evidence, raw messages, raw code, and private identifiers are omitted or redacted before the payload preview is generated
