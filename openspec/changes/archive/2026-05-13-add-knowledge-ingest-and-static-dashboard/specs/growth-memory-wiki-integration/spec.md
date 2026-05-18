## ADDED Requirements

### Requirement: Use curated Wiki knowledge in future growth cycles
The system SHALL use reviewed or eligible Wiki knowledge as context for future growth cycles.

#### Scenario: Growth cycle starts with curated knowledge
- **WHEN** a GrowthCycle starts and reviewed or eligible knowledge pages exist
- **THEN** the system loads relevant knowledge summaries, related tracks, and unresolved knowledge gaps before generating diagnoses and tasks

### Requirement: Generate growth tasks from knowledge gaps
The system SHALL generate growth task candidates from unresolved knowledge gaps when they align with the user's growth goals.

#### Scenario: Knowledge gap matches a growth track
- **WHEN** an unresolved knowledge gap is related to AI Agent engineering, business depth, or AI system management
- **THEN** the system may create a GrowthTask candidate linked to the source knowledge page and gap reference

### Requirement: Separate knowledge evidence from personal evidence
The system MUST distinguish external knowledge from evidence about the user's behavior or capability.

#### Scenario: External article supports a growth task
- **WHEN** an external knowledge page informs a recommended task
- **THEN** the system links the knowledge as learning context rather than treating it as observed evidence of the user's current skill level

### Requirement: Prevent knowledge-only maturity conclusions
The system MUST NOT raise or lower a maturity estimate using only external knowledge ingestion.

#### Scenario: User imports expert material
- **WHEN** the user ingests expert articles or notes without behavioral evidence or human review
- **THEN** the system does not treat the imported material as proof that the user has mastered the content
