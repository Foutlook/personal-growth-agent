## ADDED Requirements

### Requirement: Generate dashboard from skill-managed knowledge
The system SHALL allow the growth knowledge skill scripts to generate a static dashboard from the local `llm-wiki/`.

#### Scenario: Skill dashboard command runs
- **WHEN** the host CLI or user runs the skill dashboard command
- **THEN** the system writes a no-server dashboard under the resolved data home using sanitized Wiki indexes, write logs, source manifests, growth reviews, tasks, and knowledge pages

#### Scenario: Dashboard is generated without installed package
- **WHEN** the bundled skill script runs dashboard generation without `pip install personal-growth-agent`
- **THEN** the dashboard still builds from the skill-managed local Wiki using bundled or standard-library code

### Requirement: Keep dashboard output recall-friendly
The dashboard SHALL expose enough page metadata to support human review and memory recall.

#### Scenario: Dashboard data is built
- **WHEN** dashboard data is generated
- **THEN** it includes page titles, types, paths, tags, summaries, source counts, write provenance, and privacy state without embedding raw local-only content
