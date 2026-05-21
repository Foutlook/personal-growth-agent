## 1. Data Contracts and Workspace Layout

- [x] 1.1 Add a direct Wiki write result model with target path, operation, source IDs, prompt metadata, compiler metadata, content hash, and written timestamp.
- [x] 1.2 Implement append-only `llm-wiki/data/wiki-write-log.json` helpers that preserve existing entries and write UTF-8 without BOM.
- [x] 1.3 Update LLM Wiki initialization to create `data/growth-memory/` and direct-merge workspace paths while keeping existing raw and wiki directories compatible.
- [x] 1.4 Add compatibility wrappers or migration-safe aliases for existing `WikiUpdateProposal` callers until all call sites use direct write semantics.

## 2. Direct Wiki Write Pipeline

- [x] 2.1 Replace `create_wiki_update_proposal` primary usage with a direct write function that privacy-checks content before writing.
- [x] 2.2 Ensure every direct Wiki write records source raw IDs or source evidence IDs in page content/frontmatter and in the write log.
- [x] 2.3 Record prompt ID, prompt version, prompt path, prompt digest, compiler, provider, and model in write-log entries when available.
- [x] 2.4 Update lint logic to evaluate directly written Wiki pages and write-log provenance instead of proposal review state.

## 3. Knowledge Ingestion and Raw-Prompt Compile

- [x] 3.1 Update note, file, web, and URL ingest flows to save immutable raw sources, update source manifest entries, compile directly into Wiki pages, and append write-log entries.
- [x] 3.2 Add a raw-to-Wiki compile service that accepts a raw file or directory plus an explicit prompt path.
- [x] 3.3 Support local-rule compilation fallback when remote LLM compilation is unavailable, unapproved, or invalid.
- [x] 3.4 Validate remote compiler payloads and responses before direct Wiki writes, preserving existing outbound approval and privacy gates.

## 4. Growth Memory Restructure

- [x] 4.1 Write growth cycles, diagnoses, maturity snapshots, task state, and report summary state under `llm-wiki/data/growth-memory/`.
- [x] 4.2 Stop writing automatic cycle, diagnosis, and maturity snapshot machine pages under `wiki/growth/cycles/`, `wiki/growth/diagnoses/`, and `wiki/growth/maturity-snapshots/`.
- [x] 4.3 Generate direct human-readable growth Wiki summaries such as `wiki/growth/overview.md` and `wiki/growth/current-focus.md` from growth memory state.
- [x] 4.4 Update `load_growth_memory_context` to prefer `data/growth-memory/` while tolerating legacy growth Wiki pages during migration.
- [x] 4.5 Ensure growth memory maturity logic still distinguishes behavioral evidence, external knowledge context, inferred memory, and human-confirmed memory.

## 5. CLI, Dashboard, and Audit

- [x] 5.1 Add `pga wiki compile --raw <path> --prompt <path>` using existing workspace and Wiki path resolution.
- [x] 5.2 Update CLI ingest output to report raw source IDs and written Wiki target paths instead of proposal status.
- [x] 5.3 Update dashboard data generation to show direct writes, write provenance, growth memory state, and lint status instead of proposal approval views.
- [x] 5.4 Update privacy audit outputs to include direct Wiki writes and prompt/source provenance instead of generated WikiUpdateProposal records.
- [x] 5.5 Keep dashboard-safe exports free of raw messages, raw code, local-only raw bodies, secrets, and private identifiers.

## 6. Tests and Documentation

- [x] 6.1 Update unit tests for knowledge ingest, growth runs, Wiki initialization, lint, dashboard, and privacy audit to assert direct merge and write-log behavior.
- [x] 6.2 Add CLI tests for `pga wiki compile --raw --prompt`, including explicit `--wiki` path resolution.
- [x] 6.3 Add migration/compatibility tests proving legacy growth Wiki pages do not break future growth context loading.
- [x] 6.4 Update README to document `raw/`, `wiki/`, `data/`, `prompts/`, `report/`, direct merge, write logs, and the removed review queue.
- [x] 6.5 Run the full test suite and targeted OpenSpec validation before marking implementation complete.
