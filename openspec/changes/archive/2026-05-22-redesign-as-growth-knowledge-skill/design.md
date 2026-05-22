## Context

The current repository implements a local-first Personal Growth Agent: installable `pga` CLI, interactive REPL, remote LLM provider routing, evidence extraction from Codex/Claude/OpenCode logs, growth task generation, knowledge ingestion, direct Wiki writes, and a static dashboard. During exploration, the product direction shifted: mature host CLIs already provide strong chat, tool calling, file reading, and skill/plugin orchestration. This project should focus on its unique value: a durable local growth knowledge hub that those host CLIs can use.

The redesigned product is an installable skill package with bundled lightweight scripts. Host CLIs handle language understanding and contextual analysis. The skill tells them when and how to capture, ingest, review, and recall growth knowledge. The scripts perform deterministic local persistence into `llm-wiki/`.

## Goals / Non-Goals

**Goals:**

- Package the system as a skill usable from Codex, Claude Code, OpenCode, and similar CLIs.
- Keep configuration simple: install/load the skill; do not require the user to install the current Python package for first-version workflows.
- Preserve `llm-wiki/` as the long-lived data store for raw inputs, human-readable Wiki pages, machine-readable indexes, manifests, and write logs.
- Support first-version workflows for conversation capture, external material ingestion, growth review, memory search/read/context recall, and static dashboard generation.
- Let the host CLI generate structured capture/review/ingest input from the current conversation or material.
- Keep local scripts deterministic, lightweight, and dependency-minimal.
- Keep privacy boundaries: redact or reject secrets, avoid raw third-party full-content persistence by default, and return compact recall context.

**Non-Goals:**

- Do not rebuild a standalone chat agent, tool loop, or multi-skill runtime inside this project.
- Do not require project-owned LLM provider configuration for the skill's first-version workflows.
- Do not automatically parse Codex, Claude Code, or OpenCode conversation databases in the first version.
- Do not migrate all current `pga` features into the skill; only preserve the knowledge-hub core.
- Do not perform deep local repository analysis in the first version; keep it as a future workflow using the same structured-input pattern.

## Decisions

### Decision 1: Ship a skill-first package with bundled scripts

The deliverable should be a skill directory such as `growth-knowledge-hub/` containing `SKILL.md`, progressive reference files, and `scripts/gkh.py`. The skill body teaches host CLIs when to trigger the workflow and which reference to load. The script handles deterministic filesystem writes and reads.

Alternative considered: keep `pga` as an installable CLI and ask host CLIs to call it. This preserves existing code but keeps the product framed as a separate application. It also forces installation before use. The skill-first package better matches the desired "drop into Codex/Claude/OpenCode" experience.

### Decision 2: Host CLI performs semantic analysis; scripts persist structured input

Host CLIs should turn the current conversation, external material, or review into structured JSON according to the skill references. The bundled script validates fields, caps summaries, redacts or rejects unsafe content, writes Markdown pages, updates indexes, and emits machine-readable results.

Alternative considered: embed model calls and prompt routing in the bundled script. This would duplicate Codex/Claude/OpenCode capabilities, require credentials, and bring back the standalone-agent shape we are trying to avoid.

### Decision 3: Keep one durable Wiki model with both write and recall workflows

The skill should support a closed loop:

1. `capture`, `ingest`, and `review` write durable local knowledge.
2. `search`, `read`, and `context` let host CLIs retrieve that knowledge later.

Recall commands should return compact, sanitized context by default. Full page reads are allowed only for selected pages and must respect `local_only`/sensitivity metadata.

Alternative considered: only write notes and rely on the host CLI to search the filesystem manually. That loses the product's value as a personal memory layer and makes later personalized assistance brittle.

### Decision 4: Use a data home independent from the skill install directory

Skill code may be upgraded, replaced, or installed in multiple host CLI locations. User data must live outside the skill package. Resolution should be simple and predictable:

- Explicit `GKH_HOME` wins.
- A project-local `.growth-knowledge/` directory may provide project-scoped memory.
- Otherwise default to a user data home such as `~/.growth-knowledge-hub/`.

The Wiki should live under `<data-home>/llm-wiki/`.

Alternative considered: store data inside the skill directory. This risks losing knowledge on skill reinstall/update and complicates sharing across host CLIs.

### Decision 5: Keep repository analysis as a V2 structured-input workflow

Repository analysis remains valuable, but first-version scope should not scan large repositories automatically. Later, the host CLI can inspect a project and produce `project-analysis.json`, which the skill persists under `wiki/projects/<project>/`.

Alternative considered: port the current shallow repository analyzer into V1. This is feasible, but it distracts from the essential capture/ingest/recall loop.

### Decision 6: Preserve useful existing code concepts, not the full app

The redesign should reuse ideas and selected code patterns from `audit.py`, `utils.py`, `wiki.py`, `knowledge.py`, and `dashboard.py`: UTF-8 writes, direct Wiki writes, source manifests, write logs, redaction, summary caps, and static dashboard output. It should not carry over `interactive.py`, `chat_provider.py`, remote analyzer provider routing, external connector runtime, or automatic conversation-log parsing as first-version paths.

Alternative considered: move the whole package into `scripts/`. That would make the skill heavy, keep unnecessary dependencies, and blur the boundary between host intelligence and local persistence.

## Risks / Trade-offs

- Host CLIs differ in how they load skills and execute scripts → keep the skill instructions generic, use ordinary shell/Python commands, and avoid host-specific APIs in first-version scripts.
- Structured JSON quality depends on the host model → provide strict references, examples, validation errors, and small schemas for each workflow.
- Removing first-version autonomous analysis may feel like a regression → frame it as a deliberate shift: the host CLI is the agent; this project is the memory layer.
- Lightweight scripts may duplicate some existing package code → accept a small copy of stable local logic to avoid requiring package installation.
- Recall may leak sensitive notes if too broad → search/context return summaries by default, respect sensitivity metadata, redact content, and require explicit page reads for details.
- Existing users may still rely on `pga` CLI → keep migration docs and avoid deleting readable `llm-wiki/` data; legacy CLI may remain temporarily but is no longer the primary product surface.

## Migration Plan

1. Create the `growth-knowledge-hub` skill package structure with `SKILL.md`, references, scripts, and tests.
2. Implement a minimal standard-library `gkh.py` script with `init`, `capture`, `ingest`, `review`, `search`, `read`, `context`, and `dashboard`.
3. Reuse or port deterministic local functions for data-home resolution, redaction, direct writes, manifests, indexes, and static dashboard generation.
4. Update README to describe skill installation and usage from Codex, Claude Code, and OpenCode; mark the standalone REPL/provider path as legacy or non-primary.
5. Add tests that run the skill scripts without installing the package and verify writes/recall/dashboard behavior.
6. Keep existing `llm-wiki/` content compatible. Do not delete previous growth memory, source manifests, or write logs.
7. After the skill path is stable, consider pruning or archiving standalone-agent modules in a separate change.

Rollback is straightforward because the skill package writes to the same local Wiki model. If the skill path is disabled, existing Wiki pages remain readable and previous CLI workflows can continue until explicitly removed.

## Open Questions

- What exact install locations should be documented for Codex, Claude Code, and OpenCode?
- Should the default data home be `~/.growth-knowledge-hub/` or `~/.gkh/`?
- Should project-local memory use `.growth-knowledge/` by default, or only when explicitly requested?
- Should V1 include a machine-readable schema file for each JSON input, or keep schemas in Markdown references with runtime validation?
