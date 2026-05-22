## Why

The current product direction is drifting toward a standalone agent CLI with its own chat loop, provider routing, tool calling, and skill runtime. Codex, Claude Code, and OpenCode already do that well; this system's distinctive value is the long-lived growth knowledge layer: capturing conversations, external material, reviews, and later project experience into a local LLM Wiki that can be recalled by those host CLIs.

This change redesigns the product as an installable AI CLI skill with bundled lightweight scripts for local knowledge persistence, rather than as another interactive agent application.

## What Changes

- **BREAKING**: Reframe the primary product from `Personal Growth Agent` as a standalone interactive CLI to `Growth Knowledge Hub` as a skill that host CLIs can load.
- Add a skill package that exposes growth knowledge workflows through `SKILL.md`, progressive reference files, and bundled local scripts.
- Move first-version intelligence boundaries to the host CLI: Codex, Claude Code, or OpenCode summarizes current context and materials; the bundled scripts validate, redact, index, and write deterministic local artifacts.
- Support first-version capture flows for current conversation capture, external material ingestion, growth review, and local memory recall.
- Preserve the local `llm-wiki/` as the durable data model and make both write and read flows available through the skill.
- Keep the bundled scripts lightweight and dependency-minimal; users should not need to install the current `pga` package just to use the skill.
- De-emphasize or remove the standalone interactive agent loop, LLM provider orchestration, arbitrary skill runtime, and automatic host conversation-log analysis from the first-version product surface.
- Reserve local repository analysis as a future workflow that uses the same host-CLI-analysis plus local-persistence pattern.

## Capabilities

### New Capabilities
- `growth-knowledge-hub-skill`: Defines the installable skill package, trigger behavior, progressive references, bundled scripts, and host-CLI interaction contract.
- `growth-knowledge-recall`: Defines how Codex, Claude Code, OpenCode, and similar host CLIs can search, read, and retrieve compact context from the local growth knowledge base.

### Modified Capabilities
- `cli-workspace-management`: Replace standalone app installation as the primary path with skill-local scripts and simple data-home resolution.
- `external-knowledge-ingestion`: Reframe external material ingestion as host-generated structured input that the skill persists locally.
- `growth-memory-wiki-integration`: Reframe growth memory updates around explicit skill capture/review inputs instead of autonomous agent cycle inference.
- `interactive-agent-repl`: Deprecate the standalone interactive REPL as a primary product surface for this redesign.
- `llm-provider-and-prompt-registry`: Remove first-version dependence on project-owned model provider routing for skill workflows.
- `repository-signal-analysis`: Move local repository analysis to a future skill workflow rather than first-version automatic analysis.
- `static-dashboard-generation`: Keep dashboard generation as an optional local script output for the skill-managed Wiki.
- `wiki-direct-merge`: Preserve direct write behavior while applying it to skill-managed deterministic writes.

## Impact

- Affected code: current CLI, interactive chat loop, provider routing, knowledge ingestion, Wiki write utilities, dashboard generation, repository analysis, and tests.
- Affected docs: README and OpenSpec documentation must describe skill installation and usage instead of presenting `pga` as the central agent experience.
- Affected data model: `llm-wiki/` remains the durable local store, with explicit capture, ingest, review, recall, manifest, and write-log records.
- Dependencies: first-version skill scripts should use Python standard library only where feasible and avoid requiring users to install the Python package.
- Compatibility: existing `llm-wiki/` content should remain readable; migration should avoid deleting prior growth pages or source manifests.
