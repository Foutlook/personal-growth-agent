## ADDED Requirements

### Requirement: Audit external skill connector calls
The system SHALL audit safe metadata for external skill connector calls without storing credentials or full third-party bodies.

#### Scenario: Connector list or search runs
- **WHEN** the system calls an external skill connector list or search operation
- **THEN** the privacy audit or conversation log records connector name, operation, query or collection metadata after redaction, result count, and status without storing plaintext credentials

#### Scenario: Connector fetch runs
- **WHEN** the system fetches third-party full content on demand
- **THEN** the privacy audit records connector name, operation, source locator digest, purpose, approval or trigger reason, content digest, redaction summary, and status without storing the full fetched body by default

### Requirement: Protect external skill credentials
The system MUST NOT write external skill credentials to Wiki pages, raw sources, dashboard exports, privacy audits, or conversation logs.

#### Scenario: Connector credentials are resolved
- **WHEN** a connector uses credentials from environment variables, config files, or provider-specific storage
- **THEN** the system records only the credential source type and missing/present status, never the credential value

### Requirement: Redact connector results before chat and logs
The system MUST redact or summarize connector results before sending them to external chat providers or writing conversation logs.

#### Scenario: Connector result contains sensitive content
- **WHEN** connector list, search, read, or fetch results include secrets, private identifiers, raw code, or local-only content
- **THEN** the system redacts or omits unsafe content before returning the result to the chat loop or log
