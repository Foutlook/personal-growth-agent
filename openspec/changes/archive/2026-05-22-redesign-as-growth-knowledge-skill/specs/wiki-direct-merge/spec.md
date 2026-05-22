## ADDED Requirements

### Requirement: Directly write skill-managed Wiki pages
The system SHALL directly write skill-managed capture, ingest, review, and future project-analysis pages into `llm-wiki/wiki/`.

#### Scenario: Skill capture writes pages
- **WHEN** the skill script accepts valid structured capture input
- **THEN** it writes the corresponding Wiki pages directly and records create/update operations in the write log

#### Scenario: Skill recall indexes pages
- **WHEN** a directly written page is eligible for recall
- **THEN** the system includes it in the local index with path, type, tags, summary, source IDs, and content hash

### Requirement: Keep direct writes deterministic and script-local
The skill-managed direct write path MUST produce deterministic files from the same structured input.

#### Scenario: Same input is written twice
- **WHEN** the same valid input is processed repeatedly
- **THEN** the resulting target paths, content hashes, source IDs, and write operations are stable except for expected timestamps
