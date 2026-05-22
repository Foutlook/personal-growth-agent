## Context

The current interactive agent exposes a fixed whitelist of local tools for reports, tasks, local Wiki pages, knowledge gaps, growth runs, and dashboard generation. Installed Codex skills such as IMA can access third-party knowledge sources, but that access currently lives outside the Personal Growth Agent product. The local LLM Wiki already separates immutable raw sources, human-readable compiled Wiki pages, and machine-readable provenance data, which makes it a natural place to store durable summaries without mirroring third-party full content.

The desired product behavior is summary-first and source-on-demand: the local Wiki should keep long-lived, user-readable summary notes with at most six bullet points, while full third-party content remains in the source system and is fetched only when a user question requires it.

## Goals / Non-Goals

**Goals:**

- Introduce a generic read-only connector model for knowledge-oriented skills.
- Support four connector operations: list, search, read, and fetch.
- Add IMA as the first connector while keeping the product contract provider-neutral.
- Store local Wiki summary notes as durable, user-readable knowledge pages capped at six summary bullets.
- Preserve source provenance and make it explicit that full content is fetched on demand.
- Let the interactive agent discover, search, preview, and selectively import external skill summaries through approved tools.
- Keep external knowledge separate from personal capability evidence.

**Non-Goals:**

- Do not implement arbitrary skill execution inside the agent.
- Do not expose write, mutation, upload, note-editing, or third-party side-effect operations through the generic connector.
- Do not mirror full third-party knowledge bodies into the local Wiki by default.
- Do not automatically sync every third-party item into the local Wiki.
- Do not treat imported external summaries as proof of user mastery.

## Decisions

### Decision 1: Model connectors as read-only knowledge providers

The connector contract should expose only list, search, read, and fetch. `list` discovers collections, `search` finds candidate items, `read` returns metadata or existing summary-level information, and `fetch` retrieves full third-party content for a specific question or explicit import flow.

Alternative considered: expose installed skills directly as arbitrary tools. This was rejected because skill packages can contain write operations, shell scripts, credential flows, and network calls that are too broad for an interactive agent whitelist.

### Decision 2: Store local summaries as Wiki pages, not machine-only indexes

The durable local artifact should be a user-readable Wiki note under `wiki/knowledge/`, with frontmatter carrying provider, collection, source locator, summary policy, and full-content fetch policy. Machine-readable index data can reference those pages, but the primary local memory should be readable in Obsidian and the dashboard.

Alternative considered: store only a JSON index under `data/`. This would be efficient for search but would not satisfy the user's desire to preserve knowledge as readable local notes.

### Decision 3: Cap summaries at six bullet points and retain them long term

Each imported summary note should contain no more than six summary bullets. The note is long-lived and should not be deleted automatically just because the remote source changes or disappears. If freshness tracking is added, it should annotate the note rather than remove it.

Alternative considered: keep short snippets only. This was rejected because snippets are useful for search but too thin for human reading and later growth planning.

### Decision 4: Fetch full content only on demand

The system should first answer from local summaries when sufficient. It should call connector `fetch` only when the user asks for details, the local summary is insufficient, or the user explicitly requests original content. Fetched full content may be used transiently to answer, but it should not be persisted as a raw full-content mirror unless a future explicit import mode is added.

Alternative considered: background sync full sources into `raw/knowledge/`. This was rejected because large third-party collections such as IMA knowledge bases can contain thousands of items and would pollute the local Wiki.

### Decision 5: Treat IMA as the first provider behind a generic interface

IMA should implement the generic connector operations, mapping IMA knowledge bases and notebooks to collections and IMA media or notes to items. The interactive agent and ingestion flow should depend on the generic connector contract rather than IMA-specific details.

Alternative considered: add IMA-only tools directly to the REPL. This is simpler initially but makes future providers harder and couples product language to one third-party service.

### Decision 6: Keep connector credentials and logs redacted

Connector configuration should identify credential sources without writing secret values to conversation logs, source manifests, Wiki pages, dashboard exports, or privacy audits. Tool arguments and results should be summarized and redacted using existing interactive logging rules.

Alternative considered: rely only on provider skill scripts to avoid logging secrets. This was rejected because the product must enforce its own privacy boundary regardless of provider behavior.

## Risks / Trade-offs

- Connector abstraction may be too generic for provider-specific quirks → Start with IMA and keep provider-specific mapping inside adapter modules.
- Summary-only storage may be insufficient for detailed answers → Use on-demand `fetch` when the user asks for specifics.
- Remote source content can change after a summary is imported → Keep summary notes long-lived and record last-seen metadata or fetch timestamps without deleting summaries.
- Skill packages may expose unsafe operations → Only expose explicitly configured read-only connector adapters, not arbitrary skill operations.
- External knowledge may bias growth scoring → Preserve the existing rule that external knowledge is learning context, never direct behavioral evidence.
- Large third-party collections may overwhelm local search → Prefer selective import and search-first workflows instead of automatic full sync.

## Migration Plan

1. Add connector data models and a registry for read-only providers.
2. Add IMA provider support using the installed skill/API path and existing credential sources.
3. Add interactive tools that call the registry and return compact, redacted results.
4. Add summary import logic that writes user-readable Wiki notes and provenance metadata.
5. Extend dashboard and privacy audit exports to show connector activity without exposing secrets or full remote bodies.
6. Keep existing local Wiki and ingest behavior unchanged for users who do not configure external connectors.

Rollback is straightforward because the feature adds new tools, metadata, and Wiki pages. Disabling the connector registry should leave existing local Wiki pages readable and should stop future third-party calls.

## Open Questions

- Should connector configuration live in the main app config, a dedicated `connectors` config file, or both?
- Should imported summaries be grouped by provider/collection folders or placed in existing `wiki/knowledge/concepts/` with provider frontmatter?
- Should on-demand fetched full content ever be eligible for explicit raw ingestion, or should that remain a separate future change?
