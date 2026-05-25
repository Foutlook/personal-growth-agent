## Why

Growth Knowledge Hub currently captures only the active host conversation or host-summarized inputs, so it cannot answer questions that require patterns across prior Codex, Claude Code, and OpenCode sessions unless those sessions were manually saved first. Users need an explicit, local, privacy-aware way to analyze historical AI CLI conversations and turn them into searchable growth memory.

## What Changes

- Add an explicit `analyze-history` workflow for scanning historical host CLI sessions from Codex, Claude Code, OpenCode, or all supported sources.
- Support default source discovery plus user-supplied source directories through single-source `--source-dir` and multi-source `--source-map <source>=<path>` arguments.
- Persist deterministic, local history analysis output into `llm-wiki/` as sanitized raw conversation records, source-specific history index pages, and updated recall indexes.
- Add filtering and preview controls: `--since`, `--until`, `--limit`, `--dry-run`, and `--output stdout|wiki|json`.
- Keep `capture` scoped to the current conversation; historical analysis is opt-in through the new command.
- Preserve the no-remote-model boundary: the script performs local parsing, redaction, deduplication, lightweight summaries, and indexing, while deeper semantic growth interpretation remains the host CLI's job.
- Modify the privacy boundary from "never scan host CLI databases" to "never scan them implicitly; scan only when the user explicitly invokes history analysis."

## Capabilities

### New Capabilities

- `host-cli-history-analysis`: Defines explicit historical session scanning, supported sources, source directory handling, local analysis output, and recall integration.

### Modified Capabilities

- `growth-knowledge-hub-skill`: Adds the `analyze-history` command and workflow reference while preserving current `capture`, `review`, `project`, and recall behavior.
- `privacy-audit`: Updates privacy requirements to allow explicit user-triggered host CLI history scans while forbidding implicit scans and remote model calls.

## Impact

- Affected skill files: `growth-knowledge-hub/SKILL.md`, `growth-knowledge-hub/skill.json`, and a new history-analysis reference document.
- Affected script: `growth-knowledge-hub/scripts/gkh.py` command parsing, history source adapters, deterministic session parsing, wiki writes, and indexing.
- Affected tests: new coverage for Codex, Claude Code, OpenCode sample histories; `--source all`; custom source maps; date and limit filters; dry-run behavior; privacy redaction; and recall of generated history pages.
- No new runtime package dependency is required; the bundled script should remain Python standard-library-only.
