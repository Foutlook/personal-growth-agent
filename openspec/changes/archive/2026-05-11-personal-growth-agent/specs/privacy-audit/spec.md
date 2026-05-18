## ADDED Requirements

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
