## ADDED Requirements

### Requirement: Represent external skill summaries as Wiki knowledge notes
The system SHALL represent imported external skill knowledge items as user-readable Wiki knowledge notes with connector provenance.

#### Scenario: External skill summary page is written
- **WHEN** the system writes a local Wiki page for an external skill item
- **THEN** the page includes provider, collection, source title, source locator, summary policy, full-content fetch policy, retention policy, captured date, and sensitivity metadata

### Requirement: Mark external skill summaries as fetch-on-demand
The system MUST make clear in Wiki metadata that full third-party content is fetched on demand rather than stored locally.

#### Scenario: Summary page is inspected
- **WHEN** a user or downstream tool reads an external skill summary page
- **THEN** the page metadata indicates `full_content_policy` is fetch-on-demand or an equivalent explicit value

### Requirement: Preserve external skill summary notes
The system MUST NOT delete imported external skill summary notes automatically during maintenance.

#### Scenario: External source is stale
- **WHEN** Wiki maintenance detects that an external skill item may be stale, missing, or changed remotely
- **THEN** the system preserves the summary note and records a freshness warning or lint finding instead of deleting it

### Requirement: Lint external skill summary pages
The system SHALL include checks for external skill summary page provenance and summary shape.

#### Scenario: External skill summary lacks provenance
- **WHEN** an external skill summary page lacks provider, collection, source locator, or captured date metadata
- **THEN** Wiki Lint reports a provenance issue

#### Scenario: External skill summary exceeds summary policy
- **WHEN** an external skill summary page contains more than six summary bullet points
- **THEN** Wiki Lint reports a summary policy issue
