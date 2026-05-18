## ADDED Requirements

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
