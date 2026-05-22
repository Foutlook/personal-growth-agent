## ADDED Requirements

### Requirement: Treat external skill summaries as learning context
The system SHALL use imported external skill summary notes as learning context for growth planning without treating them as evidence of user capability.

#### Scenario: Growth cycle reads external skill summaries
- **WHEN** a GrowthCycle loads relevant Wiki knowledge and finds external skill summary notes
- **THEN** it may use their summaries, tags, and unresolved questions as learning context for diagnoses and task planning

### Requirement: Prevent external skill summaries from changing maturity by themselves
The system MUST NOT raise or lower maturity estimates based only on imported external skill summaries or fetched third-party content.

#### Scenario: External skill summary is the only supporting input
- **WHEN** a maturity estimate candidate is supported only by external skill summaries or fetched third-party content
- **THEN** the system excludes that input from direct maturity evidence and records it only as learning context

### Requirement: Link tasks from external skill summaries to source context
The system SHALL link GrowthTask candidates inspired by external skill summaries to the local summary note rather than to transient fetched full content.

#### Scenario: External summary suggests a learning task
- **WHEN** the system creates a GrowthTask candidate from an imported external skill summary
- **THEN** the task references the local summary Wiki page and records the relationship as learning context
