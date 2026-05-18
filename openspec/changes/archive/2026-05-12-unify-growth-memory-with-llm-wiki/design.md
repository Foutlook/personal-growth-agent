## Context

The MVP currently separates per-run outputs from long-lived LLM Wiki memory. `runs/<timestamp>/` stores reports, evidence, diagnoses, maturity estimates, tasks, and privacy audit outputs, while `llm-wiki/` stores raw conversation summaries, generated task artifacts, ActionAssets, and WikiUpdateProposals.

This split makes the current system useful for one-off analysis, but weak for continuous growth. Past diagnoses, unfinished tasks, user reviews, and maturity trends are not consistently available as structured inputs for future cycles. The next iteration should treat LLM Wiki as the long-term memory layer for both knowledge and growth operations.

## Goals / Non-Goals

**Goals:**

- Persist each growth run as an immutable, sanitized raw source under the LLM Wiki.
- Represent GrowthCycle, Diagnosis, GrowthTask, MaturityEstimate, report summaries, and future user reviews as typed Wiki growth memory.
- Feed prior active growth memory into new GrowthCycle generation.
- Preserve evidence traceability and avoid confidence inflation from prior inferred model output.
- Extend Wiki lint to detect stale or unsupported growth memory.
- Keep the MVP local-first and Python standard-library-only.

**Non-Goals:**

- Do not implement a UI for reviewing WikiUpdateProposals.
- Do not introduce a database, vector store, external LLM dependency, or background service.
- Do not deeply analyze raw source code beyond existing repository-signal scope.
- Do not automatically apply proposed Wiki updates without human review.

## Decisions

### Decision 1: Treat growth memory as typed Wiki pages plus immutable raw snapshots

Each run should create a raw snapshot under `llm-wiki/raw/growth-runs/` and propose typed pages under `llm-wiki/wiki/growth/` or `llm-wiki/wiki/profile/`.

The raw snapshot preserves the run result as source material. The typed pages provide long-lived operational memory that future cycles can query.

Alternatives considered:

- Store only reports in `runs/<timestamp>/`: simple, but future cycles cannot reliably reuse history.
- Directly overwrite Wiki pages: convenient, but violates diff-first behavior and risks stale claims becoming permanent.

### Decision 2: Add lifecycle and provenance metadata to growth memory

Growth memory pages should carry enough metadata to separate facts, inferred claims, human-confirmed claims, and stale assumptions.

Required metadata:

- `type`: `growth_cycle`, `diagnosis`, `growth_task`, `growth_review`, `maturity_snapshot`, `profile_snapshot`, or `report_summary`
- `lifecycle_status`: `proposed`, `active`, `completed`, `carried_forward`, `stale`, `superseded`, or `rejected`
- `source_run_id`
- `source_evidence_ids`
- `source_raw_ids`
- `evidence_status`: `Observed`, `Inferred`, `Unknown`, or `HumanConfirmed`
- `confidence`
- `human_confirmed`
- `valid_until`
- `review_state`
- `tracks`
- `related`

Alternatives considered:

- Reuse current `WikiPage.type` only: insufficient to prevent prior model output from being mistaken as direct evidence.
- Add a separate database model: unnecessary for this local-first MVP.

### Decision 3: Future GrowthCycle generation reads Wiki memory as planning context, not as raw truth

The next cycle should load:

- Active or carried-forward GrowthTasks.
- Recent GrowthReviews.
- Active Diagnoses with valid evidence or human confirmation.
- Recent MaturitySnapshots.
- North Star goals.
- ActionAsset usage references when available.

Prior inferred memory must not increase confidence by itself. It can suggest a hypothesis or task continuation, but strong conclusions still require direct evidence or human confirmation.

Alternatives considered:

- Ignore history and analyze only new conversations: avoids self-reinforcement, but loses continuity.
- Treat all Wiki memory as evidence: maximizes continuity, but amplifies stale model claims.

### Decision 4: Keep diff-first update behavior

Growth memory pages should be created through WikiUpdateProposal by default. Raw snapshots may be written directly because they are immutable source material. Existing Wiki pages should not be overwritten automatically.

Alternatives considered:

- Directly update `wiki/growth/` pages after every run: easier to inspect, but conflicts with review-first knowledge management.

### Decision 5: Extend lint rather than adding a separate validation subsystem

Growth memory quality checks should live in Wiki Lint because the risks are Wiki-level risks: missing provenance, stale pages, unsupported profile claims, and unreviewed growth tasks.

Initial lint issue types:

- `growth_missing_source`
- `growth_stale_diagnosis`
- `growth_expired_maturity`
- `growth_unreviewed_task`
- `growth_unsupported_profile_claim`
- `growth_invalid_lifecycle`

## Risks / Trade-offs

- Self-reinforcing conclusions → Mitigation: require source evidence or human confirmation for confidence increase; lint unsupported claims.
- Wiki clutter from every run → Mitigation: store full runs under `raw/growth-runs/` and only propose typed pages for useful memory objects.
- Increased implementation complexity → Mitigation: keep all storage file-based Markdown/JSON and reuse existing WikiUpdateProposal flow.
- Review burden on the user → Mitigation: group proposals by run and expose concise report summaries.
- Stale unfinished tasks biasing future planning → Mitigation: lifecycle status, review deadline, and carried-forward handling.

## Migration Plan

1. Add growth memory models and serialization helpers.
2. Extend `init_llm_wiki` with growth memory directories.
3. Persist new run snapshots under `raw/growth-runs/`.
4. Generate WikiUpdateProposals for cycle, task, diagnosis, maturity, and report summary pages.
5. Load prior Wiki growth memory into `generate_growth_cycle`.
6. Extend Wiki Lint checks for growth memory.
7. Update reports and tests to verify the closed loop.

Rollback is straightforward because the change adds new files and metadata paths. If needed, disable historical growth memory loading while continuing to produce run outputs.

## Open Questions

- What user-facing workflow should approve or reject growth memory proposals?
- Should user GrowthReviews be accepted from Markdown files, CLI arguments, or both?
- How long should default `valid_until` windows be for diagnoses and maturity snapshots?
- Should carried-forward tasks count against the default three-task weekly package or be shown separately?
