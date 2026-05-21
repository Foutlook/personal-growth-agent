## Why

The current LLM Wiki design mixes human-readable Wiki pages with machine state and still describes a diff-first human review flow that the product no longer wants. This change aligns the workspace with a direct-merge LLM Wiki model: raw sources remain immutable, prompts compile raw inputs into Wiki pages, and every direct write is traceable through machine-readable logs.

## What Changes

- **BREAKING** Replace diff-first Wiki update proposals with direct Wiki writes backed by a write log.
- Remove the human approval gate from Wiki ingestion and growth memory compilation.
- Keep `raw/` as the immutable source layer and `wiki/` as the human-readable compiled knowledge layer.
- Move automatic growth cycle, diagnosis, and maturity snapshot state out of `wiki/growth/` and into `data/growth-memory/`.
- Compile growth memory into small human-readable Wiki pages such as `wiki/growth/overview.md` and `wiki/growth/current-focus.md`.
- Add write provenance for every direct Wiki write, including source IDs, prompt identity, prompt digest, compiler, timestamps, operation type, and content hash.
- Add a prompt-driven raw-to-Wiki compile workflow that can ingest a specific raw directory with a specific prompt path.
- Update dashboard and audit behavior to show direct writes and write-log provenance instead of proposal approval states.

## Capabilities

### New Capabilities
- `wiki-direct-merge`: Directly write compiled Wiki pages while recording write provenance and preserving raw/source traceability.
- `raw-prompt-wiki-compile`: Compile selected raw sources into Wiki pages using an explicit prompt path without introducing a review queue.

### Modified Capabilities
- `llm-wiki-maintenance`: Replace diff-first proposal and human review requirements with direct merge, write logging, and clearer raw/wiki/data responsibilities.
- `external-knowledge-ingestion`: Ingested knowledge should compile directly into Wiki pages with raw source references and write-log entries.
- `growth-memory-wiki-integration`: Growth cycles, diagnoses, maturity snapshots, and task state should be stored as machine state under `data/growth-memory/`, with only compiled human-readable summaries written to `wiki/`.
- `cli-workspace-management`: Add CLI support for prompt-driven raw-to-Wiki compilation and remove user-facing reliance on proposal review states.
- `static-dashboard-generation`: Show direct Wiki writes, growth memory state, and write provenance instead of static proposal approval workflows.
- `privacy-audit`: Audit direct Wiki writes and prompt/source provenance rather than WikiUpdateProposal review records.

## Impact

- Affected modules: `personal_growth_agent/wiki.py`, `knowledge.py`, `pipeline.py`, `dashboard.py`, `cli.py`, `models.py`, `prompts.py`, and related tests.
- Affected workspace layout: `llm-wiki/wiki/growth/cycles/`, `llm-wiki/wiki/growth/diagnoses/`, and `llm-wiki/wiki/growth/maturity-snapshots/` are no longer primary output locations for automatic machine state.
- Affected data contracts: `WikiUpdateProposal` usage is replaced or compatibility-wrapped by a direct write result and `data/wiki-write-log.json`.
- Affected CLI: `pga wiki compile --raw <path> --prompt <path>` becomes the explicit raw-plus-prompt compilation path.
