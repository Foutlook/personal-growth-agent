## MODIFIED Requirements

### Requirement: Default to local deterministic processing
The system MUST process Growth Knowledge Hub script operations locally by default.

#### Scenario: Ordinary script command runs
- **WHEN** `gkh.py` performs init, capture, ingest, review, search, read, context, index, or dashboard
- **THEN** it does not call remote models, does not scan host CLI databases, and does not execute arbitrary tools

#### Scenario: Explicit history analysis command runs
- **WHEN** `gkh.py analyze-history` runs for Codex, Claude Code, OpenCode, or all supported sources
- **THEN** it scans only the requested local history sources, does not call remote models, and does not execute arbitrary tools

## ADDED Requirements

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
