## 1. Tests and Fixtures

- [x] 1.1 Add representative Codex, Claude Code, and OpenCode history fixture files under the test suite.
- [x] 1.2 Add tests for `analyze-history --source codex`, `--source claude`, and `--source opencode` using explicit source directories.
- [x] 1.3 Add tests for `analyze-history --source all` with repeated `--source-map` entries.
- [x] 1.4 Add tests for rejecting `--source all --source-dir <path>` and unknown `--source-map` keys.
- [x] 1.5 Add tests for `--since`, `--until`, `--limit`, `--dry-run`, and `--output stdout|json|wiki`.
- [x] 1.6 Add tests that historical secrets are redacted and private-key-like sessions are excluded or rejected before output.
- [x] 1.7 Add tests that Wiki output is searchable through existing `search` and `context` commands.

## 2. CLI and Source Selection

- [x] 2.1 Add the `analyze-history` subcommand to `growth-knowledge-hub/scripts/gkh.py`.
- [x] 2.2 Add arguments for `--source codex|claude|opencode|all`, `--source-dir`, repeatable `--source-map`, `--since`, `--until`, `--limit`, `--dry-run`, and `--output stdout|json|wiki`.
- [x] 2.3 Implement validation for incompatible or invalid source arguments before any scan begins.
- [x] 2.4 Implement default source discovery helpers for Codex, Claude Code, and OpenCode with clear warnings when no directory is found.

## 3. History Parsing and Normalization

- [x] 3.1 Define an internal normalized historical session shape using standard-library data structures.
- [x] 3.2 Implement the Codex history adapter for fixture-backed session discovery and parsing.
- [x] 3.3 Implement the Claude Code history adapter for fixture-backed session discovery and parsing.
- [x] 3.4 Implement the OpenCode history adapter for fixture-backed session discovery and parsing.
- [x] 3.5 Implement tolerant skip-and-warn behavior for unsupported or malformed history files.
- [x] 3.6 Implement stable session identity, content hashing, and duplicate skipping.
- [x] 3.7 Implement date filtering and per-run session limiting.

## 4. Analysis Output and Wiki Persistence

- [x] 4.1 Implement deterministic compact analysis fields: title, source, timestamps, message counts, first meaningful user prompt, short excerpts, and lightweight keywords.
- [x] 4.2 Reuse existing redaction helpers for historical message content before stdout, JSON, or Wiki output.
- [x] 4.3 Implement `stdout` output without Wiki writes.
- [x] 4.4 Implement `json` output without Wiki writes.
- [x] 4.5 Implement `wiki` output that writes sanitized raw conversation records and source-specific pages under `wiki/history/`.
- [x] 4.6 Ensure `--dry-run` suppresses all file writes even when `--output wiki` is selected.
- [x] 4.7 Rebuild the local index after Wiki history writes so recall commands can find generated pages.

## 5. Skill Documentation and References

- [x] 5.1 Add a `growth-knowledge-hub/references/history-analysis.md` workflow reference.
- [x] 5.2 Update `growth-knowledge-hub/SKILL.md` to route historical session analysis requests to the new reference.
- [x] 5.3 Update `growth-knowledge-hub/skill.json` metadata if trigger phrases or command lists are present.
- [x] 5.4 Update `README.md` with examples for single-source scans, all-source scans, source maps, dry runs, and privacy boundaries.

## 6. Verification

- [x] 6.1 Run the focused history analysis tests.
- [x] 6.2 Run the full Python test suite.
- [x] 6.3 Run `openspec validate add-host-cli-history-analysis --strict`.
- [x] 6.4 Verify generated and modified text files are UTF-8 without BOM.
