## Purpose

Define how the system generates a no-server static dashboard for reviewing LLM Wiki knowledge, growth reports, growth plans, proposals, source lineage, and privacy state.

## Requirements

### Requirement: Generate a no-server static dashboard
The system SHALL generate a static dashboard that can be opened directly from disk without starting a local web server.

#### Scenario: Dashboard build runs
- **WHEN** the user runs the dashboard build command
- **THEN** the system writes standalone HTML, CSS, JavaScript, and data files under a dashboard output directory

#### Scenario: Dashboard is opened from disk
- **WHEN** the user opens the generated HTML entry file through a browser file path
- **THEN** the dashboard renders without requiring a running backend service

### Requirement: Provide Wiki and growth review views
The static dashboard SHALL include views for Wiki knowledge, growth reports, growth tasks, maturity estimates, Wiki update proposals, source lineage, and privacy status.

#### Scenario: Dashboard renders growth data
- **WHEN** growth reports and Wiki growth memory exist
- **THEN** the dashboard shows report summaries, active tasks, maturity snapshots, diagnoses, and review states

#### Scenario: Dashboard renders Wiki data
- **WHEN** Wiki pages and update proposals exist
- **THEN** the dashboard shows page lists, proposal status, source counts, related pages, and review needs

### Requirement: Export dashboard-safe data
The system MUST build dashboard data from sanitized, dashboard-safe summaries rather than raw source content by default.

#### Scenario: Raw knowledge exists
- **WHEN** dashboard data is generated
- **THEN** the output excludes raw conversation messages, raw code, secrets, and local-only source bodies unless explicitly allowed by safe export rules

### Requirement: Support static proposal review
The dashboard SHALL make Wiki update proposals inspectable without applying them.

#### Scenario: Proposal exists
- **WHEN** a WikiUpdateProposal is included in dashboard data
- **THEN** the dashboard displays target path, reason, risk, source references, status, and diff file path

### Requirement: Support dashboard open command
The CLI SHALL provide a command that resolves the current workspace dashboard entry file and opens or prints it.

#### Scenario: Dashboard exists
- **WHEN** the user runs the dashboard open command
- **THEN** the system opens the static dashboard entry file or prints the file path if opening is unavailable

### Requirement: Rebuild dashboard deterministically
The dashboard build process SHALL be deterministic for the same workspace inputs.

#### Scenario: Inputs do not change
- **WHEN** the dashboard build command runs repeatedly with unchanged Wiki, runs, and audit files
- **THEN** the generated dashboard data has stable content except for build metadata timestamps
