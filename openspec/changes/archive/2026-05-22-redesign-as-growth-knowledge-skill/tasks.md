## 1. Skill Package Foundation

- [x] 1.1 Create the `growth-knowledge-hub` skill directory structure with `SKILL.md`, workflow references, and lightweight bundled scripts
- [x] 1.2 Define the first-version skill trigger language for capture, ingest, review, search, read, context, and dashboard workflows
- [x] 1.3 Add a minimal skill metadata file or manifest if needed by the target host CLI loaders

## 2. Lightweight Local Engine

- [x] 2.1 Implement a standard-library `gkh.py` entrypoint that supports `init`, `capture`, `ingest`, `review`, `search`, `read`, `context`, `index`, and `dashboard`
- [x] 2.2 Implement data-home resolution for `GKH_HOME`, project-local `.growth-knowledge/`, and user-level fallback storage
- [x] 2.3 Reuse or port deterministic utilities for redaction, source manifests, direct writes, write logs, and summary caps
- [x] 2.4 Ensure unsupported commands and invalid structured inputs fail safely without partial writes

## 3. Knowledge Capture and Recall

- [x] 3.1 Add capture input handling for current conversation summaries, decisions, insights, open questions, next actions, and tags
- [x] 3.2 Add material ingestion input handling for external articles, documents, copied notes, and external knowledge summaries
- [x] 3.3 Add growth review input handling for observations, progress, bottlenecks, knowledge gaps, and next tasks
- [x] 3.4 Add search/read/context commands that return compact, sanitized recall results with provenance
- [x] 3.5 Add an index rebuild flow for the skill-managed local Wiki pages

## 4. Documentation, Migration, and Verification

- [x] 4.1 Update README and user-facing docs to explain the skill-first workflow and de-emphasize the standalone agent path
- [x] 4.2 Add or update tests that verify the skill scripts run without installing the Python package and that writes/recall respect the local Wiki model
- [x] 4.3 Preserve compatibility with existing `llm-wiki/` data and verify that legacy pages, manifests, and write logs remain readable
- [x] 4.4 Review whether any legacy standalone-agent modules should be archived, retained as compatibility shims, or removed in a follow-up change
