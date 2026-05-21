# simplify-llm-wiki-direct-merge Implementation Plan

## Goal

Implement OpenSpec change `simplify-llm-wiki-direct-merge`: replace proposal/review-style Wiki updates with direct Wiki writes, append write provenance, move automatic growth machine state into `data/growth-memory/`, and add raw+prompt compile CLI.

## Success Criteria

- Direct Wiki writes create/update pages and append `llm-wiki/data/wiki-write-log.json`.
- Knowledge ingest writes raw sources, compiles directly into Wiki, and records write provenance.
- Growth run stores machine state under `data/growth-memory/` and writes human-readable growth summaries, not machine pages under `wiki/growth/diagnoses` or `wiki/growth/maturity-snapshots`.
- `pga wiki compile --raw <path> --prompt <path>` works with resolved workspace/wiki paths.
- Dashboard and privacy audit expose direct write information instead of proposal review state.
- Tests are updated first for new behavior and pass.

## Phases

| Phase | Status | Notes |
|---|---|---|
| 1. Context and baseline | complete | Read OpenSpec apply context and current code/tests. |
| 2. Core direct write model | complete | Added tests, model, writer, write log, init paths. |
| 3. Knowledge ingest and compile CLI | complete | Added tests, updated ingest, added compile service and CLI. |
| 4. Growth memory restructure | complete | Added tests, wrote data/growth-memory, generated summaries, legacy read compatibility. |
| 5. Dashboard/privacy/docs | complete | Updated dashboard data, audit outputs, README. |
| 6. Verification | complete | Full test suite passed: 77 passed. |

## Constraints

- Always read/write project files as UTF-8.
- Preserve comments unrelated to the change.
- Use minimal, scoped changes.
- Do not introduce review/approval workflow.
- Keep privacy checks as hard write gates.

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
