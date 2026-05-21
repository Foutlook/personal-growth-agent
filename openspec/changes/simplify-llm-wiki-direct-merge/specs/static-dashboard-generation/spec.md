## MODIFIED Requirements

### Requirement: Provide Wiki and growth review views
The static dashboard SHALL include views for Wiki knowledge, growth reports, growth tasks, maturity estimates, direct Wiki writes, source lineage, and privacy status.

#### Scenario: Dashboard renders growth data
- **WHEN** growth reports and growth memory state exist
- **THEN** the dashboard shows report summaries, active tasks, maturity snapshots, diagnoses, and review states from machine-readable growth memory and compiled Wiki summaries

#### Scenario: Dashboard renders Wiki data
- **WHEN** Wiki pages and direct write logs exist
- **THEN** the dashboard shows page lists, write provenance, source counts, related pages, and lint status

## REMOVED Requirements

### Requirement: Support static proposal review
**Reason**: The system no longer creates a proposal queue or requires human approval before applying Wiki updates.

**Migration**: Replace proposal review dashboard data with direct write log data including target path, operation, source references, prompt metadata, write timestamp, and content hash.
