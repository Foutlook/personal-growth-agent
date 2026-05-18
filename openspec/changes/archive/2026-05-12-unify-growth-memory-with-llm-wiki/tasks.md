## 1. Data Model and Serialization

- [x] 1.1 Add data models for GrowthMemoryContext, GrowthRunSnapshot, GrowthReview, and growth memory metadata.
- [x] 1.2 Extend WikiPage or supporting structures to carry lifecycle status, source run ID, evidence status, human confirmation, valid_until, and review state.
- [x] 1.3 Add serialization helpers for growth memory objects using existing JSON and Markdown conventions.
- [x] 1.4 Add validators that reject growth memory pages missing source run, source references, confidence, evidence status, or lifecycle state.

## 2. LLM Wiki Layout and Raw Snapshot Storage

- [x] 2.1 Extend LLM Wiki initialization with raw growth run, raw review, profile, growth cycle, task, diagnosis, review, maturity snapshot, and case directories.
- [x] 2.2 Implement immutable growth run snapshot creation under `llm-wiki/raw/growth-runs/`.
- [x] 2.3 Link growth run snapshots into `data/source-manifest.json` with run ID, source type, redaction status, hash, and source object references.
- [x] 2.4 Add tests that existing growth run snapshots are not overwritten.

## 3. Growth Memory Proposal Generation

- [x] 3.1 Generate WikiUpdateProposals for GrowthCycle summary pages.
- [x] 3.2 Generate WikiUpdateProposals for Diagnosis pages with evidence status, confidence, valid_until, and human confirmation fields.
- [x] 3.3 Generate WikiUpdateProposals for GrowthTask pages with lifecycle state, review state, expected artifacts, and carried-forward metadata.
- [x] 3.4 Generate WikiUpdateProposals for MaturityEstimate snapshot pages.
- [x] 3.5 Generate WikiUpdateProposals for report summary pages that link back to raw growth run snapshots.
- [x] 3.6 Add tests for proposal paths, metadata, evidence links, and diff-first behavior.

## 4. Historical Growth Memory Loading

- [x] 4.1 Implement a reader that loads active diagnoses, active or carried-forward tasks, recent reviews, maturity snapshots, and North Star pages from `llm-wiki/`.
- [x] 4.2 Exclude stale, rejected, superseded, unsupported, or expired growth memory from high-confidence planning input.
- [x] 4.3 Represent prior inferred memory separately from direct evidence and human-confirmed memory.
- [x] 4.4 Add tests for empty Wiki, valid memory, stale memory, unsupported memory, and human-confirmed memory cases.

## 5. Growth Cycle Integration

- [x] 5.1 Extend GrowthCycle generation to accept optional GrowthMemoryContext.
- [x] 5.2 Use active unfinished tasks to carry forward or revise tasks instead of creating duplicates.
- [x] 5.3 Use GrowthReview blockers and usefulness feedback to adjust task scope, track, or done definition.
- [x] 5.4 Prevent maturity confidence increases from prior inferred Wiki memory alone.
- [x] 5.5 Add tests proving historical memory can influence task selection without becoming unsupported direct evidence.

## 6. Pipeline and Reporting Integration

- [x] 6.1 Update the pipeline to create a growth run snapshot after evidence, diagnoses, maturity estimates, tasks, assets, and reports are available.
- [x] 6.2 Update the pipeline to load historical GrowthMemoryContext before generating a new GrowthCycle.
- [x] 6.3 Write growth memory proposal summaries into per-run `wiki-update-proposals/`.
- [x] 6.4 Update `report.md` to show carried-forward tasks, new tasks, growth memory updates, and raw growth run snapshot reference.
- [x] 6.5 Ensure privacy audit includes growth run snapshots and growth memory proposals.

## 7. Growth Memory Lint

- [x] 7.1 Add lint checks for growth memory pages missing source evidence, source raw IDs, or source run metadata.
- [x] 7.2 Add lint checks for stale diagnoses and expired maturity snapshots.
- [x] 7.3 Add lint checks for completed tasks without review and active tasks without review deadlines.
- [x] 7.4 Add lint checks for unsupported profile claims and invalid lifecycle states.
- [x] 7.5 Add tests for each growth memory lint issue type.

## 8. End-to-End Verification

- [x] 8.1 Add fixtures for one prior growth memory state and one new conversation batch.
- [x] 8.2 Run an end-to-end pipeline where prior active task memory affects the next growth cycle.
- [x] 8.3 Verify raw growth run snapshots, WikiUpdateProposals, report output, source manifest, and privacy audit are all generated.
- [x] 8.4 Verify repeated runs preserve immutable raw snapshots and avoid overwriting existing Wiki pages.
- [x] 8.5 Verify OpenSpec requirements are covered by automated tests or documented verification.
