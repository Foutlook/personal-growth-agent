## Why

DeepSeek official API has introduced `deepseek-v4-flash` and `deepseek-v4-pro`, while legacy `deepseek-chat` and `deepseek-reasoner` model names are scheduled for deprecation on 2026-07-24. The current default config still points at `deepseek-chat`, and users also need a lower-friction way to configure API keys directly in `config.toml` after installing the CLI.

## What Changes

- Update DeepSeek defaults from `deepseek-chat` to `deepseek-v4-flash`.
- Support `deepseek-v4-pro` as the higher-capability DeepSeek model option.
- Add model presets or aliases so users can choose `flash` or `pro` without memorizing full provider model names.
- Extend provider configuration to support a direct file-based `api_key = ""` field while preserving `api_key_env`.
- Resolve credentials deterministically from direct config value first, then configured environment variable.
- Emit a clear configuration prompt when a remote provider requires credentials and neither direct `api_key` nor `api_key_env` resolution provides a key.
- Update default config and README examples to show DeepSeek v4 model names, the empty API key placeholder, and the legacy model deprecation note.
- Ensure privacy and audit outputs never store plaintext API keys, only credential source metadata such as `file`, `env`, or `missing`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llm-provider-and-prompt-registry`: DeepSeek provider config gains v4 defaults, model presets, direct file API key support, and deterministic credential resolution.
- `analyzer-provider-interface`: DeepSeek analyzer requests use v4 models by default and fail or fall back clearly when required credentials are missing.
- `cli-workspace-management`: Default workspace config writes editable DeepSeek v4 model and API key placeholders that users can modify directly.
- `privacy-audit`: Audit records credential source and missing-credential skip reasons without exposing secret values.

## Impact

- Affected config code: `personal_growth_agent/config.py`
- Affected provider code: remote analyzer provider resolution and request preparation
- Affected CLI/user docs: `README.md` and default `pga init` config output
- Affected tests: config loading, default config generation, DeepSeek model selection, credential resolution, missing credential messaging, and privacy audit metadata
