# privacy-audit Specification

## Purpose

Define the local privacy boundary for Growth Knowledge Hub writes, recall, and dashboard export.

## Requirements

### Requirement: Default to local deterministic processing
The system MUST process Growth Knowledge Hub script operations locally by default.

#### Scenario: Ordinary script command runs
- **WHEN** `gkh.py` performs init, capture, ingest, review, search, read, context, index, or dashboard
- **THEN** it does not call remote models, does not scan host CLI databases, and does not execute arbitrary tools

#### Scenario: Explicit history analysis command runs
- **WHEN** `gkh.py analyze-history` runs for Codex, Claude Code, OpenCode, or all supported sources
- **THEN** it scans only the requested local history sources, does not call remote models, and does not execute arbitrary tools

### Requirement: Redact unsafe structured input before persistence
The system MUST redact common secrets and private identifiers before writing local Wiki content.

#### Scenario: Redactable sensitive content is detected
- **WHEN** input contains API-key-like strings, tokens, email addresses, URLs, or phone numbers
- **THEN** the script replaces them with redaction markers before writing raw sources, Wiki pages, indexes, or dashboard-visible summaries

### Requirement: Require explicit consent for host CLI history scans
The system MUST scan host CLI history data only after the user explicitly invokes the history analysis workflow.

#### Scenario: Recall command runs
- **WHEN** the user runs `search`, `context`, or `read`
- **THEN** the system reads only the local Wiki data and does not scan host CLI history directories

#### Scenario: Capture command runs
- **WHEN** the user runs `capture`
- **THEN** the system persists the provided structured input and does not scan host CLI history directories

#### Scenario: History command runs
- **WHEN** the user runs `analyze-history`
- **THEN** the system may read requested local host CLI history files subject to configured source and filter parameters

### Requirement: Redact historical session content before output
The system MUST apply redaction checks to historical session content before printing or persisting analysis results.

#### Scenario: Redactable content appears in history
- **WHEN** historical session content contains API-key-like strings, tokens, email addresses, URLs, or phone numbers
- **THEN** the system replaces them with redaction markers before stdout, JSON, Wiki, index, or dashboard-visible output

#### Scenario: Private key content appears in history
- **WHEN** historical session content contains private-key-like content
- **THEN** the system excludes or rejects that session before any output or persistence includes the private key body

### Requirement: Reject local-only private key content
The system MUST reject private-key-like content instead of persisting it.

#### Scenario: Private key content is detected
- **WHEN** structured input contains a private key marker
- **THEN** the script returns an error and avoids partial Wiki writes

### Requirement: Protect selected reads
The system MUST prevent unsafe local-only page bodies from being exposed through recall reads.

#### Scenario: Read target is local-only
- **WHEN** a requested page is marked `local_only` or contains private-key-like content
- **THEN** the read command returns a local-only placeholder rather than the body

### Requirement: Protect path boundaries
The system MUST prevent recall reads from escaping the resolved local Wiki.

#### Scenario: Path traversal is attempted
- **WHEN** a read path resolves outside `llm-wiki/`
- **THEN** the command rejects the request

### Requirement: Preserve provenance without secrets
The system SHALL record source and write provenance without storing credentials.

#### Scenario: Source manifest is written
- **WHEN** a source manifest entry is appended
- **THEN** it includes safe source metadata, hash, source type, path, tags, and redaction status without credential values

#### Scenario: Write log is written
- **WHEN** a Wiki page is written
- **THEN** the write log records target path, operation, source raw IDs, compiler, provider label, content hash, and timestamp without plaintext secrets

### Requirement: Keep dashboard exports sanitized
The system MUST build dashboard output from indexed page metadata and summaries rather than unsafe raw source bodies.

#### Scenario: Dashboard is generated
- **WHEN** `gkh.py dashboard` builds the no-server page
- **THEN** it renders escaped titles, summaries, and paths from the local index and excludes local-only raw bodies
