## 1. Wiki Structure And Models

- [x] 1.1 Extend LLM Wiki initialization with `raw/knowledge/*`, `wiki/knowledge/*`, and dashboard output conventions.
- [x] 1.2 Add dataclasses or typed structures for knowledge source input, knowledge ingest result, knowledge gap, and dashboard build result.
- [x] 1.3 Extend source manifest writing so knowledge entries include source type, original URL/location, captured date, sensitivity, hash, and optional publisher/author metadata.

## 2. External Knowledge Ingestion

- [x] 2.1 Implement note ingestion that accepts direct text or stdin, writes an immutable raw note, and records a manifest entry.
- [x] 2.2 Implement local file ingestion that snapshots supported text or Markdown files without modifying the original file.
- [x] 2.3 Implement copied article/web ingestion that stores article text with origin URL and source metadata without hidden network access.
- [x] 2.4 Add explicit URL fetch handling only when requested, including fetch status, final URL, digest, and privacy audit metadata.
- [x] 2.5 Generate baseline WikiUpdateProposal drafts from ingested knowledge with target path suggestions, source references, tags, and unresolved questions.

## 3. Privacy And Lint

- [x] 3.1 Extend sensitivity checks so external knowledge can be marked safe, redacted, or local_only before Wiki proposals or dashboard exports.
- [x] 3.2 Extend privacy audit output with knowledge ingestion records, explicit fetch records, dashboard export decisions, redaction counts, and omitted local-only items.
- [x] 3.3 Extend Wiki lint to report external knowledge pages with missing provenance, invalid frontmatter, unsupported claims, or unsafe dashboard visibility.

## 4. Static Dashboard Generation

- [x] 4.1 Implement a dashboard data builder that indexes latest reports, growth tasks, maturity snapshots, diagnoses, Wiki pages, proposals, source manifest entries, knowledge gaps, privacy audit summaries, and lint findings.
- [x] 4.2 Ensure dashboard data is sanitized and excludes raw messages, raw code, secrets, and local-only source bodies by default.
- [x] 4.3 Implement static asset generation for `index.html`, CSS, JavaScript, and dashboard data under the resolved workspace dashboard directory.
- [x] 4.4 Add dashboard views for overview, Wiki knowledge, growth reports, growth tasks, maturity, proposals, sources, privacy, and knowledge gaps.
- [x] 4.5 Support direct file opening behavior and provide a fallback path print when automatic browser opening is unavailable.

## 5. CLI Integration

- [x] 5.1 Add `pga ingest note`, `pga ingest file`, and `pga ingest web` or equivalent subcommands using existing workspace and Wiki path resolution.
- [x] 5.2 Add `pga dashboard build` to generate the static dashboard and print the entry file path.
- [x] 5.3 Add `pga dashboard open` to open or print the generated dashboard entry file without starting a server.
- [x] 5.4 Keep `pga sources scan` limited to AI conversation source adapters and verify it does not ingest external knowledge sources.

## 6. Growth Memory Integration

- [x] 6.1 Load reviewed or eligible knowledge summaries and knowledge gaps into future growth cycle context.
- [x] 6.2 Generate growth task candidates from relevant knowledge gaps while linking them to source knowledge pages.
- [x] 6.3 Preserve the distinction between external knowledge context and observed personal capability evidence in maturity estimates and diagnoses.

## 7. Tests And Verification

- [x] 7.1 Add tests for Wiki directory initialization and source manifest records for external knowledge.
- [x] 7.2 Add tests for note, file, and copied article ingestion, including immutable raw output and proposal generation.
- [x] 7.3 Add tests for privacy behavior covering local_only imports, redaction, and dashboard-safe export data.
- [x] 7.4 Add tests for dashboard build output, deterministic data, and no-service file entry generation.
- [x] 7.5 Add CLI tests for ingest commands, dashboard build/open behavior, and existing source scan separation.
- [x] 7.6 Run the project test suite and confirm all OpenSpec artifacts remain valid UTF-8 without BOM.
