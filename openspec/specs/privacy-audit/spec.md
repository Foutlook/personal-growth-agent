## Purpose

Define local-first privacy controls and audit outputs for conversation, repository, action asset, and LLM Wiki processing.

## Requirements

### Requirement: Default to local-first processing
The system MUST process raw conversations, source files, repository data, and raw Wiki sources locally by default.

#### Scenario: Analysis starts
- **WHEN** the system begins a run
- **THEN** it reads local data into local processing stages before any outbound LLM payload is prepared

### Requirement: Redact sensitive content before outbound use
The system MUST redact secrets, credentials, private identifiers, internal endpoints, company names, customer names, project codes, raw code, and personal privacy content before any outbound payload is generated.

#### Scenario: Secret is detected
- **WHEN** source content contains an API key, token, secret, cookie, private key, or connection string
- **THEN** the system replaces it with a redaction marker and records the redaction in the privacy audit

### Requirement: Audit outbound payloads
The system SHALL create an OutboundPayloadPreview for any content sent to an external LLM.

#### Scenario: External LLM call is prepared
- **WHEN** the system prepares a payload for an external LLM
- **THEN** it records target, purpose, included evidence count, redacted item count, raw code presence, original message presence, and payload digest

### Requirement: Protect LLM Wiki outputs
The system MUST run privacy checks on ActionAsset, WikiPage, and WikiUpdateProposal content before export or review.

#### Scenario: WikiPage contains sensitive content
- **WHEN** a generated WikiPage draft contains unredacted sensitive information
- **THEN** the system marks the output unsafe, records a privacy issue, and prevents the page from being marked ready

### Requirement: Record privacy audit artifacts
The system SHALL write privacy audit output for each run.

#### Scenario: Run completes
- **WHEN** a run completes or fails after reading any source
- **THEN** the system writes a privacy audit recording sources used, files skipped, redaction counts, local_only items, outbound payload summaries, generated ActionAssets, generated WikiUpdateProposals, and lint privacy findings

### Requirement: Degrade safely when privacy is uncertain
The system MUST mark uncertain sensitive content as local_only.

#### Scenario: Sensitivity cannot be determined
- **WHEN** the system cannot confidently classify content safety
- **THEN** it marks the content local_only and excludes it from outbound payloads and public Wiki outputs

### Requirement: Require approval before external analyzer calls
The system MUST require explicit approval before sending payloads to non-local analyzer providers.

#### Scenario: Approval is missing
- **WHEN** provider is not local and outbound approval has not been provided
- **THEN** the system writes outbound payload previews and does not call the external provider

### Requirement: Audit analyzer payloads and responses
The system SHALL record analyzer provider, model, purpose, payload digest, redaction counts, approval state, response digest, and validation status.

#### Scenario: External analyzer call completes
- **WHEN** a non-local analyzer provider returns a response
- **THEN** the privacy audit records the outbound payload preview, provider metadata, approval state, and response validation result

### Requirement: Exclude local-only evidence from external payloads
The system MUST exclude local_only EvidenceItem records and raw source content from non-local analyzer payloads.

#### Scenario: Payload contains local-only evidence
- **WHEN** an outbound analyzer payload is prepared
- **THEN** local_only evidence is omitted and the omission is recorded in the privacy audit

### Requirement: Audit external knowledge ingestion
The system SHALL include external knowledge sources in privacy audit outputs.

#### Scenario: Knowledge source is ingested
- **WHEN** a web article, public account article, local file, excerpt, or user note is ingested
- **THEN** the privacy audit records source type, original location or URL, redaction count, sensitivity state, hash, and whether raw content is local-only

### Requirement: Protect dashboard exports
The system MUST run privacy checks before writing dashboard-visible data.

#### Scenario: Dashboard data contains unsafe content
- **WHEN** dashboard export would include secrets, private identifiers, raw code, raw messages, or local-only content
- **THEN** the system redacts or omits the unsafe content and records the decision in the privacy audit

### Requirement: Mark imported sensitive knowledge as local-only
The system MUST degrade uncertain or sensitive external knowledge to local-only.

#### Scenario: Imported knowledge sensitivity is uncertain
- **WHEN** the system cannot confidently classify external knowledge as safe for generated Wiki pages or dashboard summaries
- **THEN** it marks the raw source local_only and prevents it from appearing in dashboard-safe exports by default

### Requirement: Audit explicit web fetches
The system SHALL record audit metadata for any explicit network fetch used during knowledge ingestion.

#### Scenario: URL fetch is performed
- **WHEN** the system fetches external content after explicit user approval
- **THEN** the privacy audit records fetch approval, target URL, final URL, fetch status, content digest, and redaction result

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

### Requirement: Audit credential resolution without exposing secrets
The system MUST audit remote provider credential resolution without storing plaintext credentials.

#### Scenario: File credential is used
- **WHEN** a remote provider uses a credential from `api_key`
- **THEN** the privacy audit records credential source `file` and omits the credential value

#### Scenario: Environment credential is used
- **WHEN** a remote provider uses a credential from `api_key_env`
- **THEN** the privacy audit records credential source `env` and omits the environment variable value

#### Scenario: Credential is missing
- **WHEN** a remote provider call is skipped because no credential can be resolved
- **THEN** the privacy audit records credential source `missing`, provider, model, scenario, and skip reason without storing any secret material

### Requirement: Keep interactive conversation logs local
The system MUST store interactive conversation logs outside the LLM Wiki and exclude them from Wiki source manifests by default.

#### Scenario: Conversation log is created
- **WHEN** the interactive REPL writes a conversation JSONL file
- **THEN** the file is stored under the resolved workspace `conversations` directory, not under `llm-wiki`

#### Scenario: Wiki manifest is updated by other workflows
- **WHEN** Wiki source manifests are read or written
- **THEN** interactive conversation log files are not added as raw sources unless a future explicit ingestion command requests it

### Requirement: Audit interactive external chat safely
The system SHALL record safe metadata for interactive external chat calls without storing credentials or unsafe raw context.

#### Scenario: External chat call is prepared
- **WHEN** the REPL prepares an outbound chat payload for a non-local provider
- **THEN** the system records provider, model, purpose, payload digest, credential source, and redaction summary without storing plaintext credentials

#### Scenario: Interactive context includes unsafe content
- **WHEN** chat context assembly encounters local-only content, raw source bodies, raw conversation messages, raw code, secrets, or private identifiers
- **THEN** the system omits or redacts that content before preparing the outbound chat payload

### Requirement: Record local tool activity without leaking unsafe data
The system SHALL record interactive local tool calls with sanitized arguments and summarized results.

#### Scenario: Local tool call is logged
- **WHEN** the chat loop executes a local tool
- **THEN** the conversation log records the tool name, sanitized arguments, status, and compact result summary

#### Scenario: Tool result contains unsafe content
- **WHEN** a tool result contains local-only content, secrets, raw code, or private identifiers
- **THEN** the logged result and outbound tool response omit or redact the unsafe content
