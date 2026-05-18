## 1. Configuration Model

- [x] 1.1 Extend LLM provider config loading to include direct `api_key` and provider-scoped model presets.
- [x] 1.2 Update default DeepSeek config values from `deepseek-chat` to `deepseek-v4-flash`.
- [x] 1.3 Generate `api_key = ""`, `api_key_env`, and DeepSeek `flash` / `pro` presets in the default `pga init` config.

## 2. Provider Resolution

- [x] 2.1 Implement model preset resolution so `flash` maps to `deepseek-v4-flash` and `pro` maps to `deepseek-v4-pro`.
- [x] 2.2 Implement file-first then environment-variable credential resolution for remote providers.
- [x] 2.3 Add missing-credential handling that skips the remote call, prints the required config options, and uses the configured fallback path.
- [x] 2.4 Add a non-blocking warning for legacy DeepSeek model names `deepseek-chat` and `deepseek-reasoner`.

## 3. Audit and Safety

- [x] 3.1 Record credential source metadata as `file`, `env`, or `missing` without storing plaintext API keys.
- [x] 3.2 Record missing-credential skip reasons in analyzer and privacy audit outputs.
- [x] 3.3 Ensure outbound previews, reports, and debug output do not include direct file API key values.

## 4. Documentation

- [x] 4.1 Update README configuration examples to show DeepSeek v4 defaults, direct `api_key`, `api_key_env`, and model presets.
- [x] 4.2 Document the DeepSeek legacy model deprecation date of 2026-07-24 and recommend `deepseek-v4-flash` or `deepseek-v4-pro`.
- [x] 4.3 Document that `api_key = ""` can be left empty when using environment variables and that local config files containing keys must not be committed.

## 5. Verification

- [x] 5.1 Add or update tests for loading direct API keys, environment fallback, and missing credential behavior.
- [x] 5.2 Add or update tests for DeepSeek v4 defaults and `flash` / `pro` preset resolution.
- [x] 5.3 Add or update tests confirming privacy audit metadata omits plaintext credentials.
- [x] 5.4 Run the relevant test suite and confirm OpenSpec status is complete before archiving.
