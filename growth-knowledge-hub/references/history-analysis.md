# Host CLI History Analysis

Use this workflow when the user explicitly asks to analyze prior Codex, Claude Code, OpenCode, or all supported host CLI conversations.

This workflow is different from `conversation-capture.md`: `capture` preserves the current discussion that the host has already summarized, while `analyze-history` scans local host CLI history files only after the user asks for historical analysis.

## Commands

Single source:

```bash
python scripts/gkh.py analyze-history --source codex --output wiki
python scripts/gkh.py analyze-history --source claude --output wiki
python scripts/gkh.py analyze-history --source opencode --output wiki
```

All supported sources:

```bash
python scripts/gkh.py analyze-history --source all --output wiki
```

When default discovery is not enough, pass explicit locations:

```bash
python scripts/gkh.py analyze-history --source codex --source-dir /path/to/codex/sessions --output wiki
python scripts/gkh.py analyze-history --source all --source-map codex=/path/to/codex --source-map claude=/path/to/claude --source-map opencode=/path/to/opencode --output wiki
```

Useful filters:

```bash
python scripts/gkh.py analyze-history --source all --since 2026-01-01 --until 2026-05-25 --limit 200 --dry-run --output stdout
```

## Guidance

- Use `--dry-run` first when scanning broad histories or unfamiliar directories.
- Use `--source-dir` only for a single source. For `--source all`, use repeated `--source-map source=path` entries.
- The bundled script performs local deterministic parsing, redaction, deduplication, compact summaries, Wiki writes, and indexing.
- The bundled script does not call remote models and does not infer deep growth conclusions from history by itself.
- For deeper interpretation, run `search` or `context` after history pages are written, then let the host CLI generate a `capture` or `review` input from selected recalled context.

## Output

With `--output wiki`, the script writes source-specific pages under:

```text
wiki/history/
```

It also writes compact sanitized raw records under the local Wiki raw source area and rebuilds `data/index.json` so `search` and `context` can recall the historical analysis.

## Safety

- Do not run history analysis unless the user explicitly requested historical scanning.
- Do not pass a broad directory unless it is intended to contain host CLI session history.
- Private-key-like sessions are excluded or rejected before output.
- Common secrets, emails, URLs, and phone numbers are redacted before stdout, JSON, Wiki, index, or dashboard-visible output.
