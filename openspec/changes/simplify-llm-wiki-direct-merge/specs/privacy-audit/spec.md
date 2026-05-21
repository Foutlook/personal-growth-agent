## MODIFIED Requirements

### Requirement: Protect LLM Wiki outputs
The system MUST run privacy checks on ActionAsset, WikiPage, and direct Wiki write content before export or persistence.

#### Scenario: WikiPage contains sensitive content
- **WHEN** generated Wiki content contains unredacted sensitive information
- **THEN** the system marks the output unsafe, records a privacy issue, and prevents the page from being written as a direct merge result

### Requirement: Record privacy audit artifacts
The system SHALL write privacy audit output for each run.

#### Scenario: Run completes
- **WHEN** a run completes or fails after reading any source
- **THEN** the system writes a privacy audit recording sources used, files skipped, redaction counts, local_only items, outbound payload summaries, generated ActionAssets, direct Wiki writes, and lint privacy findings

### Requirement: Audit prompt and provider routing
The system SHALL include prompt and provider routing metadata in privacy audit outputs.

#### Scenario: Remote LLM request is prepared
- **WHEN** the system prepares an outbound LLM request for analysis or Wiki compilation
- **THEN** the privacy audit records scenario, prompt ID, prompt version, prompt digest, provider, model, payload digest, approval state, and dry-run state

### Requirement: Exclude unsafe prompt context
The system MUST exclude unsafe prompt context from remote LLM payloads.

#### Scenario: Prompt context includes local-only evidence
- **WHEN** prompt context is assembled for a remote provider
- **THEN** local-only evidence, raw messages, raw code, private identifiers, and local-only raw source bodies are omitted or redacted before the payload preview is generated
