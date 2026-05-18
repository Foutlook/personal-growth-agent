## ADDED Requirements

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
