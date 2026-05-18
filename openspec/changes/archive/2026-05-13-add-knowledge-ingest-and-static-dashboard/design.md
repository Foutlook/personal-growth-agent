## Context

The current system is a local-first Python CLI with a persistent `llm-wiki/` workspace, immutable raw inputs, diff-first Wiki updates, growth memory integration, privacy audit output, and analyzer provider plumbing. It already treats growth runs, reports, diagnoses, tasks, action assets, conversations, and repository snapshots as long-lived Wiki memory.

The next gap is broader knowledge management and inspection. The user wants to ingest knowledge from websites, public account articles, personal notes, copied summaries, and local documents, then manage it together with reports and growth plans. They also prefer a no-service front end: a static page that can be opened directly from disk, not a long-running `pga serve`.

The Karpathy LLM Wiki reference suggests a three-layer model:

- `raw/`: immutable source material.
- `wiki/`: structured, linked Markdown pages maintained through proposals/diffs.
- `AGENTS.md` / `SCHEMA.md`: operating rules for LLM and human review.

This change keeps that model, with Obsidian as an optional Markdown Wiki IDE and PGA Static Dashboard as the productized visual review surface.

## Goals / Non-Goals

**Goals:**

- Add explicit external knowledge ingestion for notes, files, copied article text, and optionally approved URL fetches.
- Store imported knowledge as immutable raw Wiki inputs with source metadata and privacy state.
- Generate reviewable Wiki proposals from imported knowledge, never silent direct overwrites.
- Add a static dashboard build that can be opened with `file://` or a normal browser file path.
- Visualize Wiki knowledge, growth reports, growth tasks, maturity snapshots, proposals, source lineage, and privacy status.
- Keep the feature installable and open-source friendly through CLI commands, deterministic file outputs, and no mandatory service process.
- Preserve local-first behavior while allowing future LLM-assisted enrichment through the existing provider interface and approval/audit flow.

**Non-Goals:**

- No hosted web application or authenticated server.
- No replacement for Obsidian's Markdown editing, backlinks, or graph plugins.
- No automatic ingestion of all files on disk.
- No hidden network crawling.
- No claim that imported external knowledge proves user capability or maturity.
- No direct application of Wiki proposals without human review.

## Decisions

### Decision: External knowledge uses an explicit ingest module

Add a dedicated knowledge ingestion layer instead of expanding conversation source adapters.

Rationale:

- Conversation adapters answer "what AI tool conversations exist?"
- Knowledge ingestion answers "what external knowledge did the user intentionally add?"
- Keeping them separate prevents `pga sources scan` from accidentally scanning arbitrary notes, articles, or downloaded files.

Expected module shape:

- `personal_growth_agent/knowledge.py`
- `KnowledgeSourceInput` / `KnowledgeIngestResult` models or dataclasses.
- Functions for note, file, article text, and optional URL fetch ingestion.
- Reuse `init_llm_wiki`, source manifest append behavior, sensitivity checks, hashes, and stable IDs.

Alternatives considered:

- Reuse `sources.py` adapters for all knowledge. Rejected because it blurs conversation inventory with curated personal knowledge and makes accidental broad scans more likely.

### Decision: Raw knowledge lives under `llm-wiki/raw/knowledge/`

Add:

```text
llm-wiki/
  raw/
    knowledge/
      web/
      notes/
      files/
      excerpts/
  wiki/
    knowledge/
      concepts/
      sources/
      gaps/
```

Rationale:

- Keeps external knowledge visibly separate from conversations, repositories, growth runs, and action assets.
- Matches the LLM Wiki raw/read-only pattern.
- Leaves room for article-specific metadata and user-authored notes without overloading `raw/conversations`.

### Decision: Knowledge pages are proposal-first

Ingestion should create raw source records first. Wiki page creation should happen as `WikiUpdateProposal` drafts, optionally assisted by local rules and later LLM enrichment.

Rationale:

- This protects the Wiki from noisy or low-confidence imports.
- It keeps source references and review state visible.
- It matches existing growth memory and diff-first Wiki behavior.

Local rules should produce a useful baseline:

- infer title from metadata or first heading;
- classify source type;
- extract short summary and candidate tags;
- create a target path suggestion;
- mark unresolved questions when uncertain.

LLM enrichment can improve:

- concept extraction;
- relation discovery;
- duplicate page matching;
- knowledge gaps;
- structured rewrite proposals.

All non-local LLM enrichment must go through provider approval, outbound preview, output validation, and privacy audit.

### Decision: Static dashboard is generated, not served

Add `pga dashboard build` and `pga dashboard open`.

`build` writes a directory such as:

```text
<workspace>/
  dashboard/
    index.html
    assets/
      dashboard.css
      dashboard.js
    data/
      dashboard-data.json
```

`open` opens or prints the `index.html` path. It must not start a server.

Rationale:

- The user's stated preference is "无需启动服务的静态页面".
- Static files are easy to inspect, share locally, commit selectively, or regenerate.
- The project remains simple and open-source friendly.

Alternatives considered:

- `pga serve`: richer interactions but adds lifecycle, ports, browser/server security, and packaging friction.
- Embedding all data into one HTML file: simplest to open, but harder to inspect and test. The implementation can still offer single-file mode later if browser file restrictions become a problem.

### Decision: Dashboard data is a sanitized index, not raw source rendering

The dashboard should read generated `dashboard-data.json` summaries rather than directly rendering arbitrary raw Markdown or JSON.

Data categories:

- latest run/report summary;
- active growth tasks and reviews;
- diagnoses and maturity snapshots;
- Wiki page index;
- Wiki proposal index;
- source manifest summary;
- knowledge gaps;
- privacy audit summary;
- lint findings.

Rationale:

- Browsers opening local files should not expose raw content unexpectedly.
- A compact JSON index is easier to validate in tests.
- Privacy redaction can happen once during build.

### Decision: Obsidian remains optional

Obsidian can open `llm-wiki/` as a Vault for Markdown reading, backlink exploration, and diff review. PGA Dashboard should not depend on Obsidian plugins.

Rationale:

- Obsidian is strong as a Wiki IDE.
- PGA Dashboard is stronger for guided views across reports, tasks, privacy, proposals, and source lineage.
- Keeping them separate prevents product scope from depending on a proprietary desktop app.

### Decision: Growth uses knowledge as learning context, not behavioral evidence

Imported knowledge can inform recommended learning tasks and knowledge gaps, but it cannot prove the user's maturity.

Rationale:

- Reading or importing an expert article is not evidence that the user can apply the skill.
- Maturity estimates must stay tied to observed behavior, repository signals, user reviews, or human confirmation.

## Risks / Trade-offs

- [Risk] Static pages opened from disk may face browser restrictions when loading adjacent JSON files → Mitigation: support a bundled data script or inline JSON fallback if needed.
- [Risk] Knowledge ingestion could become a web crawler by accident → Mitigation: fetch only with explicit approval and record fetch metadata.
- [Risk] LLM enrichment may over-summarize copyrighted or private source material → Mitigation: store raw locally, generate short summaries/proposals, enforce privacy audit, and avoid exposing raw bodies in dashboard data.
- [Risk] Knowledge imports may pollute growth diagnosis → Mitigation: separate external knowledge from personal behavior evidence and lint unsupported maturity claims.
- [Risk] Dashboard becomes a second Wiki editor → Mitigation: make it review/inspect focused; proposal application remains a separate explicit workflow.
- [Risk] CLI surface grows too wide → Mitigation: group commands under `pga ingest ...` and `pga dashboard ...`.

## Migration Plan

1. Extend Wiki initialization to create knowledge and dashboard-related directories.
2. Add knowledge ingestion models/functions and tests for notes, files, copied article text, and explicit fetch metadata.
3. Add CLI ingest commands wired through existing workspace resolution.
4. Add dashboard data builder and static asset writer.
5. Add CLI dashboard build/open commands.
6. Extend privacy audit and Wiki lint for external knowledge and dashboard exports.
7. Extend growth memory loading to include eligible knowledge summaries and knowledge gaps without treating them as personal evidence.

Rollback is file-based: remove or ignore generated dashboard output and raw knowledge entries. Existing conversations, growth runs, and Wiki behavior should continue to work because the new directories are additive.

## Open Questions

- Should the first implementation support real URL fetching, or only copied article content plus URL metadata?
- Should dashboard output default to `<workspace>/dashboard/` or `<wiki>/dashboard/`?
- Should dashboard build include a single-file mode for stricter `file://` browser behavior?
- Should proposal review include a future `pga wiki proposals apply` command, or remain manual for now?
