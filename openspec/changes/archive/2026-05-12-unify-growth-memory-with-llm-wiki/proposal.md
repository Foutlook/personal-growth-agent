## Why

The current system produces growth reports, diagnoses, maturity estimates, and tasks as per-run outputs, while the LLM Wiki is mostly used for long-lived knowledge pages and action assets. This creates a gap: growth conclusions are not consistently preserved as typed, evidence-backed memory, and future growth cycles cannot reliably learn from past tasks, reviews, and maturity trends.

## What Changes

- Introduce a Growth Memory layer inside the LLM Wiki that treats GrowthCycle, Diagnosis, GrowthTask, MaturityEstimate, report snapshots, and user reviews as first-class long-term memory objects.
- Persist each run's analysis report and machine-readable growth outputs into `llm-wiki/raw/growth-runs/` as immutable source material.
- Generate WikiUpdateProposals for growth memory pages instead of keeping growth outputs only under `runs/<timestamp>/`.
- Read historical growth memory from the LLM Wiki when generating the next GrowthCycle, including prior tasks, completion status, reviews, maturity snapshots, and still-active diagnoses.
- Add lifecycle fields to growth memory pages to prevent self-reinforcing stale conclusions: evidence status, confidence, human confirmation, validity window, source run, and review status.
- Extend Wiki lint to detect stale diagnoses, unreviewed tasks, unsupported profile claims, expired maturity snapshots, and growth memory pages without source evidence.

## Capabilities

### New Capabilities
- `growth-memory-wiki-integration`: Defines how growth reports, diagnoses, maturity snapshots, tasks, reviews, and artifacts become typed LLM Wiki memory and how that memory feeds future growth cycles.

### Modified Capabilities
- `llm-wiki-maintenance`: Extend the LLM Wiki schema, directory layout, update proposal behavior, and lint checks to support growth memory objects.
- `growth-cycle-execution`: Use prior growth memory from the LLM Wiki as input when generating new diagnoses, maturity estimates, and growth tasks.

## Impact

- Affected modules: `personal_growth_agent/models.py`, `wiki.py`, `growth.py`, `pipeline.py`, `reporting.py`, and tests.
- Output changes: `llm-wiki/` gains typed growth memory locations and raw growth run snapshots; reports link back to Wiki growth memory proposals.
- Data model changes: growth memory pages require source references, confidence, evidence status, lifecycle status, source run, review state, and validity metadata.
- No external service dependency is introduced; the change remains local-first and privacy-audited.
