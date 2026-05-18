## ADDED Requirements

### Requirement: Use validated analyzer output in growth cycle generation
The system SHALL use validated LLM analyzer output as candidate input for maturity estimates, diagnoses, growth tasks, and Wiki update suggestions.

#### Scenario: Validated LLM task exists
- **WHEN** validated analyzer output includes a growth task with evidence references and done definition
- **THEN** GrowthCycle generation can include or merge that task while preserving evidence basis and analyzer provenance

### Requirement: Keep local fallback for growth cycle generation
The system MUST generate a GrowthCycle using local-rules output when LLM analysis is unavailable or rejected.

#### Scenario: External analyzer is not approved
- **WHEN** outbound approval is missing for a non-local provider
- **THEN** the system skips external analysis and generates the GrowthCycle from local evidence and historical Wiki memory
