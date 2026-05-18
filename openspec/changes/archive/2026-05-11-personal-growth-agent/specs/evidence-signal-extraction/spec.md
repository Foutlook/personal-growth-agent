## ADDED Requirements

### Requirement: Extract traceable evidence items
The system SHALL extract EvidenceItem records from parsed conversations, tool call summaries, repository summaries, and growth artifacts.

#### Scenario: Evidence item is created
- **WHEN** the system identifies a relevant behavior, knowledge, risk, growth, project, or engineering signal in parsed input
- **THEN** it creates an EvidenceItem with source reference, category, summary, sensitivity, confidence, tags, and local citation

### Requirement: Classify evidence sensitivity
The system MUST classify EvidenceItem sensitivity before any downstream LLM payload is generated.

#### Scenario: Sensitive evidence is detected
- **WHEN** an EvidenceItem includes secrets, private identifiers, internal endpoints, company names, customer names, project codes, raw code, or personal privacy content
- **THEN** the system marks the EvidenceItem as redacted or local_only and prevents unsafe raw content from being included in outbound payloads

### Requirement: Aggregate evidence into standard signals
The system SHALL aggregate EvidenceItem records into standard EvidenceSignal records using the MVP signal taxonomy.

#### Scenario: Repeated behavior supports a signal
- **WHEN** multiple EvidenceItem records indicate the same standard behavior such as requires_verification or asks_business_goal
- **THEN** the system creates or updates an EvidenceSignal with observed evidence IDs, frequency, contexts, confidence, and supported maturity tracks

### Requirement: Support MVP signal taxonomy
The system MUST support MVP signals for AI collaboration, Agent engineering, business depth, AI system management, and knowledge curation.

#### Scenario: MVP signal is detected
- **WHEN** input evidence matches one of the MVP signal definitions
- **THEN** the system records the matching signal name and category rather than creating an unstructured free-text label

### Requirement: Distinguish missing evidence from negative evidence
The system MUST distinguish evidence absence from evidence of a weakness or risk.

#### Scenario: Business signal is absent
- **WHEN** no source contains business metric discussion
- **THEN** the system marks the relevant business-depth signal as missing or unknown rather than concluding that the user lacks business depth
