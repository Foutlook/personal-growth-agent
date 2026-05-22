# growth-memory-wiki-integration Specification

## Purpose

Define how Growth Knowledge Hub records host-generated growth memory as user-readable local Wiki pages and task notes without running an autonomous growth analyzer.

## Requirements

### Requirement: Capture host-generated growth memory
The system SHALL persist growth memory supplied by the host CLI as local Wiki memory.

#### Scenario: Conversation capture includes growth signals
- **WHEN** capture input includes decisions, insights, open questions, next actions, and growth tracks
- **THEN** the script writes a growth capture page linked to the raw capture source and write log

### Requirement: Support skill-based growth reviews
The system SHALL create growth reviews directly from structured review input.

#### Scenario: User asks for a review
- **WHEN** the host CLI summarizes recent work and calls `gkh.py review`
- **THEN** the script writes a growth review page, records observations, progress, bottlenecks, knowledge gaps, and next tasks, and updates recall indexes

### Requirement: Persist next actions as task pages
The system SHALL make next tasks visible as local task records.

#### Scenario: Review input includes next tasks
- **WHEN** review input contains one or more next tasks
- **THEN** the script writes task pages under `wiki/growth/tasks/` linked to the review raw source

### Requirement: Treat host-generated conclusions as inferred memory
The system MUST distinguish host-generated summaries, decisions, and growth suggestions from directly observed user capability evidence.

#### Scenario: Host CLI proposes an interpretation
- **WHEN** structured input includes growth interpretation, bottlenecks, or next actions
- **THEN** the system records them as inferred or reviewable memory rather than confirmed capability evidence

### Requirement: Keep external knowledge separate from personal evidence
The system MUST distinguish learning material from evidence about the user's behavior or capability.

#### Scenario: External material informs a task
- **WHEN** imported material suggests a learning task or knowledge gap
- **THEN** the system links it as learning context and does not use it as proof of mastery
