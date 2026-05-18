## Purpose

Define how the system turns growth tasks into reusable, machine-usable action assets for future AI collaboration workflows.

## Requirements

### Requirement: Generate reusable action assets
The system SHALL generate ActionAsset records that help the user apply growth tasks in future Codex, Claude Code, opencode, or generic AI collaboration workflows.

#### Scenario: Action asset is generated
- **WHEN** a GrowthTask requires future workflow support
- **THEN** the system generates an ActionAsset with type, title, trigger, target tool, content, usage instruction, source references, review metric, and export target

### Requirement: Support core action asset types
The system MUST support prompt_snippet, checklist, template, agent_rule, and playbook action asset types.

#### Scenario: Verification gap is detected
- **WHEN** EvidenceSignals indicate missing or weak verification behavior
- **THEN** the system can generate a checklist or prompt_snippet for AI output verification

### Requirement: Link action assets to tasks and evidence
The system MUST link each ActionAsset to at least one source GrowthTask or Diagnosis and to supporting EvidenceItem records when available.

#### Scenario: Action asset is exported
- **WHEN** an ActionAsset is included in report or LLM Wiki output
- **THEN** it contains sourceTaskIds or sourceDiagnosisIds and sourceEvidenceIds or sourceRawIds

### Requirement: Protect action asset privacy
The system MUST prevent ActionAsset content from containing unredacted secrets, customer names, company names, project codes, raw code, private URLs, or personal privacy content.

#### Scenario: Sensitive content appears in generated asset
- **WHEN** generated ActionAsset content contains unredacted sensitive information
- **THEN** the system blocks export, records a privacy issue, and requires redaction or regeneration

### Requirement: Export machine-usable assets
The system SHALL export accepted ActionAssets into the machine-usable section of the LLM Wiki layout.

#### Scenario: Prompt asset is accepted
- **WHEN** a prompt_snippet ActionAsset is valid
- **THEN** the system writes or proposes it under llm-wiki/machine-usable/prompts/
