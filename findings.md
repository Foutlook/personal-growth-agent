# Findings

## OpenSpec Context

- Change: `simplify-llm-wiki-direct-merge`.
- Apply progress at start: 0/27 tasks complete.
- Required behavior: direct Wiki writes with write-log provenance; raw sources immutable; machine growth state in `data/growth-memory/`; human-readable Wiki summaries only in `wiki/growth/`.

## Current Known Code Shape

- `create_wiki_update_proposal` currently writes directly to the target Wiki page but returns `WikiUpdateProposal` with `status="accepted"` and `requires_human_review=False`.
- `knowledge.py` ingest saves raw sources, creates a knowledge page through `create_wiki_update_proposal`, and writes gap pages directly.
- `pipeline.py` writes per-run JSON outputs, creates a growth run snapshot, then calls `create_growth_memory_proposals`.
- `load_growth_memory_context` currently scans Markdown pages under `wiki/` and categorizes typed growth memory pages.

## Implementation Assumptions

- Keep backward-compatible `WikiUpdateProposal` wrappers where needed while introducing direct write result as the primary model.
- Use local-rule compilation first for raw+prompt compile; remote LLM compile can be represented through prompt provenance and existing approval/audit hooks if available.
- Do not delete legacy workspace pages automatically.
