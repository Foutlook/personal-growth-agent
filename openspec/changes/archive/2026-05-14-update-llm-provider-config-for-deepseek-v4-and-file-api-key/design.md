## Context

The current LLM configuration already separates provider and prompt settings from code, but the DeepSeek defaults still use `deepseek-chat`. The user wants the installed CLI to be usable by editing `config.toml` directly: model choice, API key, and provider options should be visible in one place. DeepSeek official API now exposes v4 model IDs (`deepseek-v4-flash`, `deepseek-v4-pro`) and marks legacy `deepseek-chat` / `deepseek-reasoner` for deprecation on 2026-07-24, so the default config needs to move before users build new workflows on deprecated names.

## Goals / Non-Goals

**Goals:**

- Make `deepseek-v4-flash` the default DeepSeek model.
- Support `deepseek-v4-pro` through either the full model ID or a `pro` preset.
- Let users configure API keys directly in `config.toml` with `api_key = ""`.
- Preserve environment-variable based credential configuration with `api_key_env`.
- Provide clear missing-credential messaging for remote provider runs.
- Keep plaintext API keys out of logs, reports, outbound previews, and privacy audits.
- Update README/default config examples so a newly installed user can configure DeepSeek without reading source code.

**Non-Goals:**

- No hosted secret manager.
- No encryption-at-rest implementation for local config files.
- No removal of `api_key_env`.
- No broad provider SDK replacement.
- No implementation of OpenAI-specific credential changes beyond preserving existing behavior.

## Decisions

### Decision: Prefer explicit file API key over environment fallback

Credential resolution order:

1. Non-empty provider `api_key` from `config.toml`.
2. Value from the configured `api_key_env` environment variable.
3. Missing credential state with a user-facing message and audit skip reason.

Rationale:

- The user explicitly wants post-install setup by editing a file.
- Environment variables remain safer for shared machines and automation.
- The order is deterministic and easy to explain.

Alternative considered:

- Prefer environment variables over file values. Rejected because it makes the visible `config.toml` value less predictable for local users who intentionally edited it.

### Decision: Store model presets in provider config

Suggested config shape:

```toml
[llm]
default_provider = "deepseek"
default_model = "deepseek-v4-flash"

[llm.providers.deepseek]
provider = "deepseek"
base_url = "https://api.deepseek.com"
api_key = ""
api_key_env = "PGA_DEEPSEEK_API_KEY"
default_model = "deepseek-v4-flash"
timeout_seconds = 60

[llm.providers.deepseek.models]
flash = "deepseek-v4-flash"
pro = "deepseek-v4-pro"
```

Rationale:

- Provider-scoped presets avoid global alias collisions.
- Users can still write full model IDs when provider docs change.
- Future providers can define their own `flash` or `pro` names without changing code paths.

Alternative considered:

- Hard-code DeepSeek aliases in provider code. Rejected because it makes provider updates require code edits and hides the available choices from the user.

### Decision: Treat legacy model names as deprecated but not a breaking config error

If a user already configured `deepseek-chat` or `deepseek-reasoner`, the system should not fail only because the name is legacy. It should surface a warning that those model names are deprecated as of 2026-07-24 and recommend `deepseek-v4-flash` or `deepseek-v4-pro`.

Rationale:

- Existing configs should not break before the provider actually removes the models.
- The README and generated config should steer new users to v4 immediately.

Alternative considered:

- Reject legacy names. Rejected because it creates avoidable migration friction and may block users during a transition period.

### Decision: Missing credentials are a provider readiness failure, not a validation failure

When credentials are missing, provider request preparation should stop before building a remote call. The analyzer should record a skipped remote invocation and use the configured fallback path rather than treating the provider response as invalid.

Rationale:

- There is no remote response to validate.
- The user action is configuration, not data correction.
- Privacy audit can clearly distinguish `missing_credentials` from malformed output.

Alternative considered:

- Let the HTTP client fail with authentication errors. Rejected because it produces weaker user guidance and can create unnecessary outbound attempts.

## Risks / Trade-offs

- [Risk] File-based API keys can be committed accidentally → Mitigation: generated docs warn that local config can contain secrets and must not be committed.
- [Risk] Provider model names may change again → Mitigation: full model IDs remain configurable and presets live in config.
- [Risk] Credential source metadata may accidentally expose values → Mitigation: audit stores only `file`, `env`, or `missing`, never raw key text or environment variable values.
- [Risk] Existing tests may assume `deepseek-chat` defaults → Mitigation: update default config and provider-resolution tests together.

## Migration Plan

1. Extend provider config data structures to include `api_key` and provider model preset mapping.
2. Update default LLM config and `pga init` generated TOML to use `deepseek-v4-flash`.
3. Add DeepSeek `flash` and `pro` preset resolution.
4. Implement credential resolution with file-first, env-second ordering.
5. Add missing-credential messages before outbound provider calls.
6. Update privacy audit metadata to record credential source and missing-credential skip reasons.
7. Update README with DeepSeek v4 examples and the 2026-07-24 legacy model deprecation note.

Rollback strategy:

- Users can set `default_model` back to an explicit model ID in `config.toml`.
- If file credentials cause operational concern, users can leave `api_key = ""` and rely only on `api_key_env`.

## Open Questions

- Should the environment variable name shown in generated config be `PGA_DEEPSEEK_API_KEY` or the shorter `DEEPSEEK_API_KEY`?
- Should legacy DeepSeek model warnings be printed on every run or only when config inspection/report commands are invoked?
