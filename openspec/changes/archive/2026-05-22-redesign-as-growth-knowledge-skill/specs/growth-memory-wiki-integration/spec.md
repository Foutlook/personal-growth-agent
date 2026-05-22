## ADDED Requirements

### Requirement: Capture host-generated growth memory
The system SHALL persist growth memory supplied by the host CLI as structured local Wiki memory.

#### Scenario: Conversation capture includes growth signals
- **WHEN** the host CLI provides capture input with decisions, insights, open questions, next actions, and growth tracks
- **THEN** the system writes human-readable growth pages and machine-readable records linked to the capture source

#### Scenario: Review input includes next tasks
- **WHEN** the host CLI provides growth review input with next tasks
- **THEN** the system writes or updates local task records without requiring an autonomous growth-cycle run

### Requirement: Treat host-generated conclusions as inferred memory
The system MUST distinguish host-generated summaries, decisions, and growth suggestions from directly observed user capability evidence.

#### Scenario: Host CLI proposes maturity or growth interpretation
- **WHEN** structured input includes an interpretation of the user's growth, maturity, bottleneck, or next action
- **THEN** the system records it as inferred or reviewable memory unless the input explicitly includes human confirmation and supporting source references

#### Scenario: Imported material suggests a skill level
- **WHEN** external material or a host-generated summary implies expertise
- **THEN** the system records the material as learning context rather than proof of user mastery

### Requirement: Support skill-based growth reviews without autonomous runs
The system SHALL allow growth reviews to be created directly from skill inputs.

#### Scenario: User asks for a weekly review
- **WHEN** the host CLI summarizes the user's recent work and provides review input
- **THEN** the system writes a review page, next-action records, and updated indexes without scanning host CLI logs

#### Scenario: User reviews a prior task
- **WHEN** review input references a previous task or Wiki page
- **THEN** the system links the new review to that local memory item
