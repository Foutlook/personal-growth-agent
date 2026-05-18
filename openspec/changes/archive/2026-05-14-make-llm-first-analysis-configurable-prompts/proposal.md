## Why

The current system treats local rules as the primary analysis engine and only uses LLMs as an optional enrichment path. This limits analysis quality and makes prompt behavior hard to evolve per scenario, while the user wants remote providers such as DeepSeek official API and GPT-5.4 to be the default analysis path.

This change makes LLM analysis the primary analysis mode while keeping local rules as a structured evidence, privacy, and fallback layer. It also externalizes provider settings and scenario-specific prompts so they can be changed without modifying code.

## What Changes

- Make remote LLM analysis the default analysis path for supported workflows.
- Keep local rules as evidence extraction, redaction, reconciliation, and fallback infrastructure rather than the primary analyzer.
- Externalize analyzer provider configuration into a dedicated LLM config section with per-provider settings.
- Externalize prompts into named scenario prompt files that can be overridden per workspace.
- Route different analysis scenarios to different prompts, such as role inference, maturity scoring, growth planning, knowledge ingestion, and Wiki maintenance.
- Require every LLM-derived result to preserve evidence references, prompt version metadata, provider metadata, and validation status.
- Preserve safe local fallback when a remote provider is unavailable, unapproved, or invalid.

## Capabilities

### New Capabilities

- `llm-provider-and-prompt-registry`: Manage remote provider settings, prompt bundles, and scenario routing outside of code.

### Modified Capabilities

- `analyzer-provider-interface`: Change default analysis behavior so the system can use remote LLM providers as the primary analysis path.
- `llm-evidence-enrichment`: Extend LLM enrichment to cover role inference, maturity scoring, growth planning, and knowledge/Wiki scenarios through scenario-specific prompts.
- `analyzer-output-validation`: Require prompt versioning, provider provenance, and stricter evidence-aware validation for LLM outputs.
- `growth-cycle-execution`: Consume validated LLM analysis as the primary input for diagnoses, tasks, and maturity estimates while preserving local fallback.
- `cli-workspace-management`: Add CLI/config behavior for selecting providers, prompt packs, and default analysis modes.
- `privacy-audit`: Extend audit metadata to capture prompt identity/version, provider routing, and remote LLM invocation decisions.

## Impact

- Affected code paths: analyzer provider selection, payload construction, output validation, reconciliation, growth cycle generation, and CLI config loading.
- Affected config surface: provider selection, model selection, prompt registry, and scenario routing.
- Affected prompt assets: scenario prompt files for role inference, maturity scoring, growth planning, knowledge ingestion, and Wiki maintenance.
- Affected audit records: provider, model, prompt version, analysis mode, validation status, and reconciliation status.
- Affected runtime behavior: remote LLMs become the default analysis path, with local rules preserved as a fallback and guardrail layer.
