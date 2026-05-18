## ADDED Requirements

### Requirement: Include validated LLM-enriched evidence
The system SHALL allow validated LLM-enriched evidence to supplement local EvidenceItem extraction.

#### Scenario: LLM candidate evidence is valid
- **WHEN** LLM output includes a candidate evidence item with valid source references, sensitivity classification, and confidence
- **THEN** the system can include it as LLM-derived evidence with analyzer provenance

### Requirement: Preserve local-rules baseline
The system MUST keep local-rules evidence extraction available when LLM analysis is disabled or fails.

#### Scenario: LLM provider fails
- **WHEN** a configured LLM provider errors, times out, or returns invalid output
- **THEN** the system records the analyzer failure and continues with local-rules evidence and signals
