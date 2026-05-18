## Context

The current system already has a provider abstraction, privacy gates, analyzer payload previews, and local-rules analysis. However, the implementation still treats local rules as the main analyzer path and does not yet use remote LLM output as the primary input for role inference, maturity scoring, growth planning, and Wiki suggestion generation.

The user wants the default analysis path to be remote LLMs such as DeepSeek official API or GPT-5.4, while keeping local rules as a supporting layer for evidence extraction, redaction, and fallback. They also want LLM configuration and prompts separated so they can be changed without editing code.

This is a cross-cutting change that touches provider selection, prompt routing, validation, audit metadata, CLI config, and growth-cycle generation.

## Goals / Non-Goals

**Goals:**

- Make remote LLM analysis the default path for supported analysis scenarios.
- Keep local rules as the evidence, privacy, and fallback layer.
- Externalize provider configuration and prompt content.
- Route different analysis scenarios to different prompts.
- Preserve evidence traceability, validation, and reconciliation.
- Keep local fallback if remote analysis is unavailable, unapproved, or invalid.

**Non-Goals:**

- No automatic trust in remote LLM output.
- No new hosted service.
- No prompt editor UI.
- No multi-agent orchestration beyond scenario routing.
- No removal of local-rules baseline extraction.

## Decisions

### Decision: Introduce a prompt registry separate from code

Store scenario prompts as files instead of embedding them in Python source.

Suggested layout:

```text
prompts/
  role_profile.zh.md
  maturity_scoring.zh.md
  growth_planning.zh.md
  evidence_enrichment.zh.md
  knowledge_ingest.zh.md
  wiki_maintenance.zh.md
  report_generation.zh.md
```

Workspace override layout:

```text
<workspace>/prompts/
<workspace>/llm-wiki/machine-usable/prompts/
```

Rationale:

- Users can tweak prompts without code changes.
- Scenario prompts become versionable content.
- Prompt changes can be reviewed and diffed.

Alternatives considered:

- Keep prompts inside Python constants. Rejected because they are harder to iterate and version.
- Store prompts only in `llm-wiki`. Rejected because prompt files are executable strategy, not just knowledge.

### Decision: Introduce an LLM configuration section distinct from analyzer config

Separate provider/model/prompt routing from the current general analyzer config so that remote LLM behavior can be edited independently.

Suggested config shape:

```toml
[llm]
default_provider = "deepseek"
default_model = "deepseek-chat"
default_analysis_mode = "llm_first"
prompt_dir = "prompts"
approve_outbound = true

[llm.providers.deepseek]
base_url = "https://api.deepseek.com"
api_key_env = "PGA_DEEPSEEK_API_KEY"
timeout_seconds = 60

[llm.providers.openai]
base_url = "https://api.openai.com/v1"
api_key_env = "PGA_OPENAI_API_KEY"
timeout_seconds = 60
```

Rationale:

- The user wants DeepSeek and GPT-5.4 as first-class remote options.
- Provider details should not be duplicated across CLI flags and code branches.
- Analysis mode should be explicit instead of inferred ad hoc.

### Decision: Treat local rules as structured context and fallback

Keep local-rules extraction, redaction, and signal reconciliation in place, but do not use it as the top-level analysis strategy when remote LLM analysis is available.

Rationale:

- Local rules are reliable for deterministic extraction and privacy filtering.
- Remote LLMs are better for higher-order synthesis, role inference, and growth planning.
- Local rules still matter when the remote provider is unavailable or the output fails validation.

### Decision: Route analysis by scenario

Each scenario gets its own prompt and output schema.

Examples:

- role profile → current role, level, strengths, risks, cautions
- maturity scoring → track-level maturity and missing signals
- growth planning → tasks, steps, done definition, review questions
- evidence enrichment → candidate signals and rationale
- knowledge ingest → knowledge gaps, tags, Wiki proposal content
- wiki maintenance → diff-ready update proposals

Rationale:

- One generic prompt causes prompt sprawl and muddled outputs.
- Scenario routing makes outputs testable and easier to validate.

### Decision: Validation must happen after every remote call

All remote LLM results should go through:

1. schema validation,
2. evidence reference validation,
3. privacy/redaction validation,
4. reconciliation with local rules,
5. audit recording.

Rationale:

- Remote LLMs can be wrong, verbose, or inconsistent.
- The system should never treat LLM output as direct evidence without proof.

### Decision: Default behavior is LLM-first, not LLM-only

Remote provider should be the default analysis path, but the system must still preserve a complete local fallback package.

Rationale:

- Remote LLM gives better synthesis for the user’s goals.
- Local rules are still necessary for traceability and safety.

## Risks / Trade-offs

- [Risk] Remote providers add latency and cost → Mitigation: make scenario prompts compact, cache prompt digests, and support dry-run / local fallback.
- [Risk] Prompt drift can make analysis inconsistent → Mitigation: version prompt files and record prompt digest/version in audit.
- [Risk] Remote output may overstate confidence → Mitigation: strict evidence validation and no confidence amplification from unsupported claims.
- [Risk] Provider-specific APIs diverge → Mitigation: keep a provider interface and normalize scenario input/output across providers.
- [Risk] Prompt files become stale knowledge artifacts → Mitigation: separate executable prompts from Wiki knowledge and review them explicitly.

## Migration Plan

1. Add prompt registry and provider config handling.
2. Introduce scenario-based prompt selection.
3. Update analyzer payload construction to include prompt identity/version and scenario metadata.
4. Add remote-provider-first execution path with local fallback.
5. Extend validation and audit outputs.
6. Route growth cycle generation through validated LLM outputs.
7. Add tests for provider selection, prompt override, validation, and fallback.

Rollback strategy:

- Disable remote default provider in config.
- Revert to local provider and existing local-rules generation.
- Keep prompt files inert if the routing layer is disabled.

## Open Questions

- Should DeepSeek and OpenAI be treated as separate provider IDs or a common `openai-compatible` superclass with named presets?
- Should prompt files live only in workspace, or also be generated into `llm-wiki/machine-usable/prompts/`?
- Should LLM analysis run by default in every command, or only in `run` and knowledge/Wiki generation flows?
- Should prompt versioning be semantic (`v1`, `v2`) or digest-based only?
