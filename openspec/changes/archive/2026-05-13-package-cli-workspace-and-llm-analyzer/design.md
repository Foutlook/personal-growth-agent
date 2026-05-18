## Context

The current MVP can be run with `python -m personal_growth_agent.cli`, but it requires explicit source mappings or uses hardcoded defaults. It writes outputs under a passed output root and only uses local keyword rules for analysis. This is enough for development fixtures but not enough for open-source usage.

The next step is to make the system installable and usable as a local CLI while preserving the privacy-first design. LLM analysis should enhance the local-rules baseline, not replace the evidence chain or bypass redaction.

## Goals / Non-Goals

**Goals:**

- Provide an installable `pga` CLI.
- Add workspace initialization and path resolution for `runs/`, `llm-wiki/`, config, source manifests, and audit outputs.
- Add `pga init`, `pga run`, `pga sources scan`, `pga report latest`, and `pga wiki path`.
- Replace generic source scanning with Codex, Claude Code, and opencode adapters.
- Add incremental source inventory using file hash and parse status.
- Add analyzer provider interface with `local`, `openai-compatible`, and `ollama`.
- Add LLM assist/hybrid modes with strict payload preview, approval, validation, and reconciliation.
- Keep `local` as default and preserve full functionality without credentials or network.

**Non-Goals:**

- Do not implement static dashboard or external web/公众号/user-note ingestion in this change.
- Do not introduce a database, background daemon, or hosted service.
- Do not send raw conversation text or raw code to external providers by default.
- Do not make LLM output authoritative without source evidence and validation.

## Decisions

### Decision 1: CLI-first packaging

Add a console script:

```toml
[project.scripts]
pga = "personal_growth_agent.cli:main"
```

The CLI should support subcommands instead of a single flat command. This makes the product shape explicit:

```text
pga init
pga run
pga sources scan
pga report latest
pga wiki path
```

Alternatives considered:

- Keep `python -m`: fine for development, poor for open-source users.
- Build a web app first: too early and conflicts with local-first CLI workflows.

### Decision 2: Deterministic workspace resolution

Path resolution order:

1. Explicit CLI flags: `--workspace`, `--wiki`, `--config`.
2. Environment variables: `PGA_WORKSPACE`, `PGA_WIKI`, `PGA_CONFIG`.
3. Config file values.
4. User default: `~/.personal-growth-agent`.

Default layout:

```text
~/.personal-growth-agent/
├─ config.toml
├─ runs/
├─ llm-wiki/
├─ source-manifests/
└─ cache/
```

Alternatives considered:

- Default to current working directory: easy but scatters personal memory across projects.
- Require every path as a flag: explicit but not convenient.

### Decision 3: Source adapters own discovery and parsing

Introduce a common adapter contract:

```text
SourceAdapter
├─ name
├─ default_paths()
├─ discover(config)
├─ fingerprint(path)
├─ parse(path)
└─ summarize_failure(path, error)
```

Each adapter returns source candidates and normalized `ConversationSession` records. Incremental scan manifests record path, mtime, size, hash, adapter name, parse status, parse error, and last processed run.

Alternatives considered:

- Continue recursive JSON scanning: simple but brittle as real tool formats diverge.
- Hardcode every parser in one module: fast initially, harder to extend.

### Decision 4: Provider interface separates transport from analysis contract

Provider objects only handle request/response transport. Analyzer orchestration owns prompts, allowed payload shape, validation, and reconciliation.

Provider modes:

- `local`: current local-rules behavior.
- `openai-compatible`: base URL, model, API key env var, timeout.
- `ollama`: local endpoint and model.

Analysis modes:

- `local`: no LLM enrichment.
- `assist`: LLM proposes candidate evidence, profile, risks, tasks, and Wiki suggestions.
- `hybrid`: validated LLM output can influence task generation and confidence within limits.

Alternatives considered:

- Provider-specific business logic: leads to inconsistent behavior.
- LLM-first analysis: too risky for privacy and evidence quality.

### Decision 5: External analyzer calls require preview and approval

For non-local providers:

1. Build redacted payload from safe evidence summaries and allowed Wiki memory.
2. Generate `OutboundPayloadPreview`.
3. If `--dry-run`, stop before calling provider.
4. If approval flag or config is missing, skip call and use local fallback.
5. If approved, call provider and record audit metadata.

This keeps external LLM usage opt-in and inspectable.

### Decision 6: LLM output is candidate data until validated

LLM output must be strict JSON and include evidence references for every claim. Validation checks:

- JSON parse and schema compliance.
- Known evidence IDs or safe source summary IDs.
- No sensitive content.
- Required fields for role inference, candidate signals, growth tasks, and Wiki suggestions.
- No conversion of missing evidence into confirmed weakness.

Reconciliation rules:

- local + LLM agreement → confidence may increase within a cap.
- LLM-only with evidence → candidate or medium-confidence signal.
- local + LLM conflict → preserve local evidence and mark conflict.
- LLM claim without evidence → reject or caution only.

## Risks / Trade-offs

- External provider privacy leak → Mitigation: default local provider, redaction, payload preview, explicit approval, audit digests.
- LLM hallucination → Mitigation: schema validation, evidence reference checks, reconciliation rules, local fallback.
- CLI scope grows too large → Mitigation: keep dashboard and external knowledge ingestion out of this change.
- Real source formats are unstable → Mitigation: adapter contract and parse failure reporting.
- OpenAI-compatible APIs vary → Mitigation: support a minimal chat-completions-compatible request first and keep provider errors non-fatal.

## Migration Plan

1. Add CLI subcommand structure and console script.
2. Add workspace/config resolution and `pga init`.
3. Introduce source adapter interface and implement current fixture-compatible adapters.
4. Add source scan manifest and incremental scan behavior.
5. Add analyzer provider interface with local provider first.
6. Add dry-run outbound payload construction and audit recording.
7. Add openai-compatible and ollama provider stubs or minimal implementations.
8. Add LLM output schema validation and reconciliation.
9. Wire validated analyzer output into evidence and growth cycle generation.
10. Extend tests and CLI smoke checks.

Rollback is straightforward because `local` remains the default. If provider logic fails, users can run `pga run --provider local`.

## Open Questions

- Should `openai-compatible` use API key env var only, or allow config-file key storage? The safer initial choice is env var only.
- Should `pga run --provider openai-compatible` require both `--dry-run` and a second command to approve, or allow `--approve-outbound` in one command?
- Should `assist` mode be the default when a non-local provider is configured, or should the user choose it explicitly?
