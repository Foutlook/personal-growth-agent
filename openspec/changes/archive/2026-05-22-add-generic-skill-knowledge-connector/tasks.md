## 1. Connector Contract

- [x] 1.1 Add external skill knowledge connector models for collections, items, summaries, fetched content, credentials, and connector errors.
- [x] 1.2 Implement a connector registry that exposes only list, search, read, and fetch operations for enabled providers.
- [x] 1.3 Add policy checks that reject unsupported mutation operations and arbitrary skill or shell execution.
- [x] 1.4 Add unit tests for registry routing, missing connector handling, and mutation rejection.

## 2. IMA Connector

- [x] 2.1 Implement IMA collection listing through the generic connector contract without exposing IMA-specific IDs to user-facing output.
- [x] 2.2 Implement IMA item search with optional knowledge base or collection scope.
- [x] 2.3 Implement IMA item read for metadata and summary-level previews without fetching or persisting full bodies by default.
- [x] 2.4 Implement IMA fetch for on-demand full content retrieval with credential redaction and safe error reporting.
- [x] 2.5 Add tests for configured credentials, missing credentials, empty results, search results, and fetch failures.

## 3. Summary-Only Local Knowledge Import

- [x] 3.1 Add an ingestion path for selected external skill items that writes user-readable local Wiki summary notes.
- [x] 3.2 Enforce the six-bullet maximum summary policy when generating or accepting external skill summaries.
- [x] 3.3 Record provider, collection, source title, source locator, summary policy, fetch-on-demand policy, retention policy, captured date, and sensitivity metadata in Wiki frontmatter.
- [x] 3.4 Ensure fetched full content is not persisted as a raw full-content mirror by default.
- [x] 3.5 Add tests for summary note creation, summary bullet limits, long-lived retention behavior, and no implicit full-body persistence.

## 4. Interactive Agent Tools

- [x] 4.1 Add approved interactive tools for listing external collections, searching external knowledge, reading external item previews, fetching full content on demand, and importing selected summaries.
- [x] 4.2 Update interactive tool specs and system prompt guidance so the agent searches summaries first and fetches full content only when required.
- [x] 4.3 Require explicit user request or confirmation before importing external summaries into the local Wiki.
- [x] 4.4 Sanitize and summarize connector tool arguments and results in conversation logs.
- [x] 4.5 Add REPL tests for approved connector tools, rejected arbitrary skill calls, explicit import confirmation, and fetch-on-demand behavior.

## 5. Wiki Maintenance, Dashboard, and Audit

- [x] 5.1 Extend Wiki initialization or lint support for external skill summary metadata and summary policy validation.
- [x] 5.2 Add lint checks for missing external connector provenance and summaries exceeding six bullets.
- [x] 5.3 Extend dashboard-safe exports to show external skill summary notes and connector provenance without exposing credentials or full fetched bodies.
- [x] 5.4 Extend privacy audit records for connector list, search, read, fetch, credential resolution, redaction, and skipped calls.
- [x] 5.5 Add tests covering lint findings, dashboard-safe export redaction, and privacy audit metadata.

## 6. Growth Memory Integration

- [x] 6.1 Load external skill summary notes as learning context for growth cycle planning.
- [x] 6.2 Prevent external skill summaries or fetched third-party content from directly raising or lowering maturity estimates.
- [x] 6.3 Link growth task candidates inspired by external skill summaries to the local summary Wiki page.
- [x] 6.4 Add tests proving external skill summaries can inform tasks while remaining separate from behavioral capability evidence.

## 7. Documentation and Verification

- [x] 7.1 Update README or user documentation with the summary-first, fetch-on-demand external skill knowledge workflow.
- [x] 7.2 Document IMA connector configuration and credential expectations without including secret values.
- [x] 7.3 Run strict OpenSpec validation for the change.
- [x] 7.4 Run the focused automated test suite covering connector, ingestion, REPL, Wiki lint, audit, and growth integration behavior.
