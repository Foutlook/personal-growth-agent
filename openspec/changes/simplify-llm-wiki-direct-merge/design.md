## Context

The current workspace already has the rough LLM Wiki layers: immutable raw sources, Markdown wiki pages, source manifests, prompts, reports, and dashboard exports. However, its requirements still describe diff-first proposals and human review states, while the current implementation often writes target Wiki pages directly and marks the result accepted. That mismatch makes the architecture hard to reason about and also pollutes `wiki/growth/` with machine-oriented pages such as cycles, diagnoses, and maturity snapshots.

The desired workflow is a direct-merge variant of the LLM Wiki model:

```text
raw source or growth snapshot
  -> prompt-driven compiler
  -> direct write to wiki/
  -> source manifest + wiki write log + lint/report
```

This keeps the useful LLM Wiki separation while removing the review queue:

- `raw/` is immutable source material.
- `data/` is machine state, indexes, manifests, and write logs.
- `wiki/` is human-readable compiled knowledge.
- `prompts/` controls how raw inputs are transformed into Wiki content.
- `report/` contains lint and operational reports.

## Goals / Non-Goals

**Goals:**

- Replace Wiki proposal/review semantics with explicit direct Wiki writes.
- Record write provenance for every Wiki write in `data/wiki-write-log.json`.
- Support prompt-driven compilation from explicit raw paths into Wiki pages.
- Move automatic growth machine state out of `wiki/growth/` and into `data/growth-memory/`.
- Keep only human-readable growth summaries, current focus pages, reviews, and cases in `wiki/growth/` or `wiki/cases/`.
- Preserve privacy checks, source manifests, prompt provenance, and lint reports.

**Non-Goals:**

- Introduce a human approval workflow, PR workflow, or dashboard approval buttons.
- Delete historical Wiki files automatically during migration.
- Build a full RAG or graph retrieval system.
- Require remote LLM use for every compile; local-rule compilation remains valid when configured or when outbound use is unavailable.

## Decisions

### Direct write result replaces proposal as the primary contract

The system will introduce a direct write result model for successful Wiki writes. It will record target path, operation, source raw IDs, source evidence IDs, prompt metadata, compiler, provider/model when applicable, content hash, and write time.

Alternative considered: keep `WikiUpdateProposal` and always set `status=accepted`. That preserves compatibility but keeps a misleading review concept in the domain model. A short compatibility adapter is acceptable during implementation, but new code should use direct write semantics.

### `data/wiki-write-log.json` is append-only provenance

Every direct Wiki write will append an entry to `llm-wiki/data/wiki-write-log.json`. The log is not an approval queue and does not block writes. It exists for traceability, dashboard display, audit output, and rollback investigation through Git or filesystem history.

Alternative considered: rely only on Git diff. Git is useful, but the application still needs structured provenance linking Wiki output to raw source IDs, prompt digests, and provider metadata.

### Growth memory machine state belongs in `data/growth-memory/`

Automatic `GrowthCycle`, `Diagnosis`, `MaturityEstimate`, and task state will be serialized as machine-readable state under `data/growth-memory/`. Wiki pages generated from that state should be concise compiled summaries such as `wiki/growth/overview.md`, `wiki/growth/current-focus.md`, and optional case/review pages.

Alternative considered: keep typed Markdown pages under `wiki/growth/cycles/`, `wiki/growth/diagnoses/`, and `wiki/growth/maturity-snapshots/`. That makes Obsidian and the dashboard noisy and treats model-generated state as long-lived human knowledge before it has been compiled into a readable form.

### Prompt-driven compile is explicit

The CLI will expose an explicit raw-plus-prompt compile path. Ingest commands may still save raw sources and immediately compile them, but the lower-level operation should support `pga wiki compile --raw <path> --prompt <path>`.

Alternative considered: hide compilation inside ingest only. That is simpler for common use, but it does not support the Karpathy-style workflow of pointing the system at a raw directory and a chosen prompt.

### Privacy remains a hard write gate

Removing human review does not remove privacy protection. Generated Wiki content must still pass sensitive-content checks before being written. Unsafe source content may still be stored as local-only raw input, but compiled Wiki output and dashboard-safe exports must omit or redact unsafe material.

Alternative considered: write everything and rely on lint. That would make direct merge dangerous because there is no review step to catch leaked secrets.

## Risks / Trade-offs

- Direct merge can write low-quality summaries faster than a review workflow -> lint reports, write logs, prompt provenance, and Git history provide correction and rollback paths.
- Moving growth state from Wiki pages to data files may break existing dashboard or memory-context readers -> implement a compatibility reader for old pages during migration while writing new state to `data/growth-memory/`.
- Removing proposal status may break tests and dashboard data assumptions -> update contracts and tests to use direct write logs instead of proposal status.
- Prompt-driven compilation can become nondeterministic when remote LLMs are used -> record prompt digest, provider, model, source IDs, and content hash for every write.
- Existing user workspaces may already contain `wiki/growth/diagnoses/` or `wiki/growth/maturity-snapshots/` -> do not delete those files automatically; ignore them as primary state unless a compatibility reader needs them.

## Migration Plan

1. Add direct write result and write-log support while keeping compatibility shims for existing callers.
2. Update knowledge ingest to write raw sources, compile Wiki pages directly, and append write-log entries.
3. Update growth run output to write machine state under `data/growth-memory/` and compile human-readable growth summary pages into `wiki/growth/`.
4. Update dashboard and privacy audit exports to read direct write logs and growth memory data.
5. Add `pga wiki compile --raw --prompt`.
6. Update tests and README to document direct merge, raw/wiki/data responsibilities, and removal of the review queue.

Rollback is straightforward because the change writes normal files. Reverting the code and restoring previous workspace files from Git or backups restores the previous proposal-style behavior. Existing raw sources and source manifest entries remain valid.

## Open Questions

- Should direct compile overwrite existing Wiki pages by default, or should it merge sections when a page already exists?
- Should `wiki/growth/current-focus.md` be regenerated every run, while `wiki/growth/overview.md` accumulates history?
- Should legacy `WikiUpdateProposal` remain in public JSON outputs for one release as a compatibility alias?
