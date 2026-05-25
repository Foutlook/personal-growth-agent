## Context

Growth Knowledge Hub is currently a host-CLI-loaded skill and deterministic local script. The host CLI summarizes the active conversation, materials, reviews, or project lessons, then `gkh.py` validates and persists those structured inputs into a local `llm-wiki/`.

This design adds explicit historical AI CLI session analysis for Codex, Claude Code, and OpenCode. The important boundary change is permission-based: the script still must not implicitly scan host CLI databases during ordinary capture, recall, review, or dashboard commands, but it may scan historical sessions when the user explicitly invokes `analyze-history`.

The project should keep its current standard-library-only script posture. Historical analysis must therefore be deterministic and local: parse files, normalize sessions, redact sensitive content, deduplicate, build lightweight summaries, write Wiki pages, and rebuild indexes. Deeper semantic interpretation remains the host CLI's responsibility after recalling the generated history context.

## Goals / Non-Goals

**Goals:**

- Add `analyze-history` for `codex`, `claude`, `opencode`, and `all`.
- Support default source discovery, single-source `--source-dir`, and multi-source `--source-map <source>=<path>`.
- Provide bounded scanning through `--since`, `--until`, `--limit`, `--dry-run`, and `--output stdout|wiki|json`.
- Normalize host sessions into a common internal session shape before writing.
- Persist sanitized history results into the local Wiki so existing `search`, `context`, and `read` workflows can recall them.
- Preserve the existing `capture` meaning: current conversation only.
- Preserve no remote model calls and no arbitrary tool execution.

**Non-Goals:**

- Do not implement a standalone chat loop or model provider.
- Do not infer deep growth maturity, personality traits, or capability levels directly inside `gkh.py`.
- Do not save complete long conversation bodies by default.
- Do not support every possible historical storage format variant in the first implementation; unsupported files should be skipped with warnings.
- Do not automatically scan host histories during unrelated commands.

## Decisions

### Decision: Add a separate `analyze-history` command

`capture` remains scoped to host-generated current-conversation input. Historical analysis uses a new command because it has different privacy, performance, and error-handling semantics.

Alternative considered: make `capture` search all historical conversations automatically. This was rejected because it would make a small memory write unexpectedly read broad private history and would blur the user's consent boundary.

### Decision: Use source adapters behind one normalized session shape

Each host source gets a small adapter responsible for discovery, enumeration, and parsing:

- `codex`
- `claude`
- `opencode`

Adapters return a normalized structure with `source`, `session_id`, `started_at`, `title`, `messages`, `path`, and parse warnings. Downstream redaction, deduplication, output formatting, and Wiki writes operate on this normalized shape.

```text
Codex files      Claude files      OpenCode files
     │                │                 │
     ▼                ▼                 ▼
 CodexAdapter    ClaudeAdapter     OpenCodeAdapter
     │                │                 │
     └───────────────┬─────────────────┘
                     ▼
          NormalizedConversationSession
                     │
          redact / dedupe / summarize
                     │
          stdout/json/wiki output
```

Alternative considered: write one parser that recursively guesses all formats. This was rejected because source-specific assumptions would become hard to audit and test.

### Decision: Prefer explicit directory overrides over aggressive discovery

Default discovery should cover known conventional locations where practical. When discovery fails or the user's installation differs, the command should ask for `--source-dir` for a single source or repeated `--source-map <source>=<path>` for `all`.

`--source-dir` is invalid with `--source all` because one unlabeled path cannot safely represent three distinct host histories. `--source-map` is accepted for any source and is the preferred override for multi-source runs.

### Decision: Write compact history pages, not full transcripts by default

The first implementation should write:

- raw source records containing sanitized compact snippets and provenance,
- source-specific history index pages under `wiki/history/`,
- index metadata that existing recall commands can search.

The default summary should be deterministic: title, time, source, first meaningful user prompt, message counts, lightweight keyword/topic extraction, and short redacted excerpts. Full transcript persistence can be a future explicit option.

### Decision: `--output` controls side effects

- `--output stdout` prints a compact result and does not write Wiki pages.
- `--output json` prints machine-readable normalized results and does not write Wiki pages.
- `--output wiki` writes local Wiki artifacts and rebuilds the index.
- `--dry-run` suppresses writes regardless of output mode and reports what would be scanned or written.

This keeps preview behavior testable and avoids accidental writes during discovery.

## Risks / Trade-offs

- Host history formats may vary or change → keep adapters tolerant, skip unsupported files with warnings, and cover sample fixtures in tests.
- Default discovery may be incomplete → document `--source-dir` and `--source-map`, and surface clear warnings for missing sources.
- Historical conversations may contain secrets or sensitive private content → apply the same redaction/rejection layer before any output that could be persisted or indexed.
- Large histories may be slow to parse → apply date filters before expensive parsing when timestamps are available, enforce `--limit`, and stream/iterate files instead of loading a whole tree into memory.
- Deterministic summaries may feel shallow → make this explicit; host CLI can perform deeper analysis later using `context` or selected `read` results.
- Duplicate sessions may appear across backups or exports → derive stable IDs from source, source path, timestamps, and content hashes, and make repeated writes idempotent where practical.

## Migration Plan

Existing users keep current behavior. `capture`, `ingest`, `review`, `project`, `search`, `context`, `read`, `index`, and `dashboard` remain compatible.

The privacy spec changes from an absolute "no host CLI database scanning" rule to an explicit-consent rule. No migration of existing Wiki pages is required.

Implementation can ship behind the new command with sample-driven parser coverage. If problems appear, rollback is simple: remove the `analyze-history` command exposure and leave existing Wiki data intact.

## Open Questions

- Exact default directories for Codex, Claude Code, and OpenCode may need fixture-backed confirmation for Windows, macOS, and Linux.
- Whether a future `--include-full-content` option is acceptable should be decided separately because it changes the privacy profile.
- Whether generated history pages should live under `wiki/history/` permanently or later be promoted into `wiki/growth/` by a host-generated review workflow remains a future design choice.
