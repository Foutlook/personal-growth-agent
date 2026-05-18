## Why

Personal Growth Agent already persists growth reports, diagnoses, tasks, and LLM Wiki memory, but it does not yet provide a first-class way to ingest external knowledge such as web articles, public account articles, files, or user notes. The system also lacks a zero-service visual surface for reviewing Wiki knowledge, reports, growth plans, proposals, source lineage, and privacy status.

This change turns the Wiki into a broader personal knowledge and growth memory system while keeping the local-first, reviewable, static-file workflow suitable for open-source use.

## What Changes

- Add external knowledge ingestion for web snapshots, copied article text, local files, and user-authored notes.
- Preserve external knowledge under `llm-wiki/raw/knowledge/` as immutable raw inputs with source metadata, hashes, sensitivity state, and provenance.
- Generate or propose structured Wiki pages from external knowledge using the same diff-first, source-linked Wiki workflow.
- Add static dashboard generation that produces standalone HTML/CSS/JS files which can be opened directly from disk without starting a server.
- Add dashboard views for Wiki overview, growth reports, growth tasks, maturity trends, update proposals, source inventory, privacy audit, and knowledge graph-style relationships.
- Extend CLI behavior with knowledge ingest and dashboard commands while preserving existing workspace path resolution.
- Extend privacy handling so imported external knowledge and generated static dashboard assets cannot expose unsafe raw content by default.

## Capabilities

### New Capabilities

- `external-knowledge-ingestion`: Ingest web/article/note/file knowledge sources into the LLM Wiki raw layer and generate reviewable Wiki proposals from them.
- `static-dashboard-generation`: Build and open a no-server static dashboard for reviewing reports, growth memory, Wiki pages, proposals, source lineage, and privacy status.

### Modified Capabilities

- `llm-wiki-maintenance`: Add knowledge-specific raw directories, page types, source manifest fields, and lint rules for externally ingested knowledge.
- `growth-memory-wiki-integration`: Allow growth cycles to read curated Wiki knowledge as context and produce growth tasks from knowledge gaps, while preventing unsupported self-reinforcement.
- `privacy-audit`: Extend privacy checks and audit outputs to external knowledge ingestion and static dashboard exports.
- `cli-workspace-management`: Add user-facing CLI commands for knowledge ingestion and static dashboard generation/opening.
- `source-adapter-discovery`: Clarify that conversation source adapters remain separate from explicit external knowledge ingestion while sharing scan metadata and manifest conventions where useful.

## Impact

- Affected CLI surface: new commands such as `pga ingest note`, `pga ingest file`, `pga ingest web`, `pga dashboard build`, and `pga dashboard open`.
- Affected workspace layout: new LLM Wiki raw and dashboard output directories under the resolved workspace or Wiki path.
- Affected data model: new raw knowledge source metadata, knowledge page types, dashboard index data, and dashboard-safe export records.
- Affected privacy flow: imported knowledge and dashboard exports must pass local redaction/sensitivity checks before being exposed to generated pages.
- Affected analysis flow: future growth cycles may use curated Wiki knowledge and knowledge gaps as inputs, but must retain evidence links and confidence boundaries.
