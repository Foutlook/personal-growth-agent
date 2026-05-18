## 1. Configuration And Prompt Registry

- [x] 1.1 Add LLM provider config models for default provider, default model, analysis mode, approval policy, prompt directory, and provider-specific settings.
- [x] 1.2 Update default workspace config generation to include DeepSeek and OpenAI-compatible provider examples without hard-coded secrets.
- [x] 1.3 Add prompt registry resolution with package defaults, workspace overrides, and explicit prompt path overrides.
- [x] 1.4 Add default scenario prompt files for role profile, maturity scoring, growth planning, evidence enrichment, knowledge ingestion, Wiki maintenance, and report generation.
- [x] 1.5 Record prompt ID, version, digest, scenario, provider, and model in prompt request metadata.

## 2. Provider Interface And Remote Routing

- [x] 2.1 Extend analyzer request/response models with scenario, prompt metadata, output schema name, provider route, and skip/fallback reason.
- [x] 2.2 Implement DeepSeek provider request construction using configured official API endpoint, model, API key env var, timeout, and approval gates.
- [x] 2.3 Extend OpenAI-compatible provider handling to support GPT-5.4 model metadata and provider audit records.
- [x] 2.4 Preserve dry-run behavior so remote providers generate payload previews without network calls.
- [x] 2.5 Implement deterministic provider resolution from CLI flags, scenario config, workspace config, environment variables, and defaults.

## 3. Scenario Prompt Routing

- [x] 3.1 Implement scenario routing for role profile, maturity scoring, growth planning, evidence enrichment, knowledge ingestion, Wiki maintenance, and report generation.
- [x] 3.2 Build redacted structured prompt context from local-rule evidence, local signals, allowed Wiki memory, knowledge gaps, and repository summaries.
- [x] 3.3 Ensure remote prompt context excludes raw messages, raw code, private identifiers, and local-only evidence by default.
- [x] 3.4 Add prompt inspection CLI behavior so users can locate prompt directories and scenario prompt files.

## 4. Validation And Reconciliation

- [x] 4.1 Add scenario-specific schema validation for role profile outputs.
- [x] 4.2 Add scenario-specific schema validation for maturity scoring outputs.
- [x] 4.3 Add scenario-specific schema validation for growth planning outputs.
- [x] 4.4 Add scenario-specific schema validation for knowledge and Wiki proposal outputs.
- [x] 4.5 Reconcile LLM-first outputs with local-rule signals, preserving local evidence on conflict and preventing confidence amplification from unsupported claims.
- [x] 4.6 Record validation failures, prompt provenance, provider metadata, reconciliation status, and fallback decisions in audit output.

## 5. Growth Cycle Integration

- [x] 5.1 Route GrowthCycle generation through validated LLM-first outputs when available.
- [x] 5.2 Preserve local-rule fallback for missing approval, provider failure, timeout, invalid JSON, invalid schema, or unsafe content.
- [x] 5.3 Ensure role inference, maturity estimates, diagnoses, growth tasks, and Wiki suggestions keep evidence IDs and analyzer provenance.
- [x] 5.4 Prevent LLM-only role level or maturity claims from becoming observed evidence without direct evidence or human-confirmed memory.

## 6. CLI And Reporting

- [x] 6.1 Add or extend CLI flags for provider, model, analysis mode, prompt scenario, prompt directory, dry-run, and outbound approval.
- [x] 6.2 Update reports to show default provider, scenario prompts, prompt versions, LLM validation status, and fallback mode.
- [x] 6.3 Update privacy audit output with prompt routing metadata, skip reasons, payload digest, response digest, and redaction counts.
- [x] 6.4 Update README usage notes for remote provider setup, prompt editing, dry-run, and approval workflow.

## 7. Tests And Verification

- [x] 7.1 Add tests for LLM config loading, provider override order, and default remote provider behavior.
- [x] 7.2 Add tests for prompt registry resolution, workspace override, prompt digest, and scenario routing.
- [x] 7.3 Add tests for DeepSeek and OpenAI-compatible payload construction without making real network calls.
- [x] 7.4 Add tests for dry-run, missing approval, missing credentials, and local fallback.
- [x] 7.5 Add tests for scenario output validation and evidence reference enforcement.
- [x] 7.6 Add tests that LLM-first growth outputs influence GrowthCycle only after validation.
- [x] 7.7 Run the full test suite and verify new/modified text files remain UTF-8 without BOM.
