## ADDED Requirements

### Requirement: Analyze explicit host CLI history sources
The system SHALL provide an explicit `analyze-history` command that scans historical AI CLI sessions only when the user invokes that command.

#### Scenario: Analyze Codex history
- **WHEN** the user runs `gkh.py analyze-history --source codex`
- **THEN** the system scans Codex history from a discovered or configured Codex source directory

#### Scenario: Analyze Claude Code history
- **WHEN** the user runs `gkh.py analyze-history --source claude`
- **THEN** the system scans Claude Code history from a discovered or configured Claude source directory

#### Scenario: Analyze OpenCode history
- **WHEN** the user runs `gkh.py analyze-history --source opencode`
- **THEN** the system scans OpenCode history from a discovered or configured OpenCode source directory

#### Scenario: Analyze all supported histories
- **WHEN** the user runs `gkh.py analyze-history --source all`
- **THEN** the system attempts to scan Codex, Claude Code, and OpenCode histories and reports warnings for sources that cannot be discovered or parsed

### Requirement: Support explicit source directory overrides
The system SHALL allow users to override host history locations without ambiguous multi-source directory interpretation.

#### Scenario: Single source directory override
- **WHEN** the user runs `gkh.py analyze-history --source codex --source-dir <path>`
- **THEN** the system scans the provided directory as the Codex history source

#### Scenario: Multi-source directory map
- **WHEN** the user runs `gkh.py analyze-history --source all --source-map codex=<path> --source-map claude=<path> --source-map opencode=<path>`
- **THEN** the system scans each mapped directory for its matching source

#### Scenario: Ambiguous all-source directory is rejected
- **WHEN** the user runs `gkh.py analyze-history --source all --source-dir <path>`
- **THEN** the system rejects the command with a clear error explaining that `--source-map` is required for multi-source directory overrides

#### Scenario: Unknown source map key is rejected
- **WHEN** the user provides a `--source-map` key other than `codex`, `claude`, or `opencode`
- **THEN** the system rejects the command without scanning or writing history data

### Requirement: Normalize historical sessions
The system SHALL parse supported host history files into a common conversation session shape before redaction, deduplication, output, or Wiki writes.

#### Scenario: Session is normalized
- **WHEN** a supported history file is parsed
- **THEN** the normalized session includes source, stable session ID, source path, optional start time, title or fallback title, and role-labeled messages

#### Scenario: Unsupported file is skipped
- **WHEN** a file in a source directory cannot be parsed as a supported session
- **THEN** the system skips that file, records a warning, and continues scanning other files

#### Scenario: Duplicate session is encountered
- **WHEN** multiple files produce the same stable session identity or content hash
- **THEN** the system records one analyzed session and reports the duplicate as skipped

### Requirement: Bound history scanning
The system SHALL provide filters that limit which historical sessions are analyzed.

#### Scenario: Since filter is applied
- **WHEN** the user runs `analyze-history --since YYYY-MM-DD`
- **THEN** the system excludes sessions known to be older than the given date

#### Scenario: Until filter is applied
- **WHEN** the user runs `analyze-history --until YYYY-MM-DD`
- **THEN** the system excludes sessions known to be newer than the given date

#### Scenario: Limit is applied
- **WHEN** the user runs `analyze-history --limit 50`
- **THEN** the system analyzes at most 50 sessions per command run after source discovery and filtering

### Requirement: Produce side-effect controlled output
The system SHALL support `stdout`, `json`, and `wiki` output modes plus a dry-run mode for historical analysis.

#### Scenario: Stdout output
- **WHEN** the user runs `analyze-history --output stdout`
- **THEN** the system prints a compact human-readable analysis summary and does not write Wiki pages

#### Scenario: JSON output
- **WHEN** the user runs `analyze-history --output json`
- **THEN** the system prints machine-readable normalized analysis results and does not write Wiki pages

#### Scenario: Wiki output
- **WHEN** the user runs `analyze-history --output wiki`
- **THEN** the system writes sanitized history artifacts into the local Wiki and rebuilds the recall index

#### Scenario: Dry run suppresses writes
- **WHEN** the user runs `analyze-history --dry-run --output wiki`
- **THEN** the system reports what would be scanned or written without creating or modifying Wiki files

### Requirement: Persist compact sanitized history knowledge
The system SHALL persist compact, sanitized historical session knowledge rather than full long transcripts by default.

#### Scenario: History page is written
- **WHEN** `analyze-history --output wiki` completes with parsed sessions
- **THEN** the system writes source-specific history pages under `wiki/history/` and source manifest entries for the analyzed sessions

#### Scenario: Raw historical source is written
- **WHEN** historical session snippets are persisted
- **THEN** the system stores only redacted compact snippets and provenance metadata by default

#### Scenario: Recall index includes history
- **WHEN** history pages are written
- **THEN** `search` and `context` can return matching historical analysis pages from the local Wiki index

### Requirement: Preserve local deterministic analysis boundary
The system MUST NOT call remote models or perform deep semantic growth interpretation inside `gkh.py analyze-history`.

#### Scenario: Historical sessions require deeper interpretation
- **WHEN** the user wants decisions, growth insights, or review conclusions from historical sessions
- **THEN** the host CLI uses recalled history context to generate structured `capture`, `review`, or other existing write inputs
