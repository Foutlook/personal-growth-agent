# With-Skill / Baseline Evaluation

Date: 2026-05-22
Mode: dry-run comparison
Skill: `growth-knowledge-hub`
Prompt set: `growth-knowledge-hub/test-prompts.json`

## Method

This evaluation compares two expected behaviors for each prompt:

- **baseline**: a capable host CLI answers without consulting `growth-knowledge-hub/SKILL.md`.
- **with-skill**: a host CLI follows `growth-knowledge-hub/SKILL.md` and the relevant reference file.

Because this repository does not contain an agent runner that can execute isolated model trials, this is a rubric-based dry run rather than a live multi-agent benchmark.

Each prompt is graded on six assertions:

1. Selects the correct workflow or asks for clarification when ambiguous.
2. Uses the relevant reference or recall strategy instead of improvising.
3. Produces the required structured JSON or recall plan.
4. Calls the correct `gkh.py` command or explicitly avoids a nonexistent command.
5. Preserves privacy, provenance, summary limits, and source boundaries.
6. Reports the outcome in human terms, including paths, redaction/error status, and recall guidance.

## Results

| Prompt | Baseline | With Skill | Notes |
| --- | ---: | ---: | --- |
| `capture-discussion` | 2/6 | 6/6 | Baseline likely summarizes the discussion but misses JSON shape, script call, write-log/provenance, and recall guidance. |
| `ingest-third-party-summary` | 2/6 | 6/6 | With-skill preserves summary-first and fetch-on-demand policy; baseline may store or summarize without the local persistence contract. |
| `growth-review` | 3/6 | 5/6 | Baseline can write a useful review, but misses local Wiki/task persistence. With-skill may still need enough recent context before writing. |
| `recall-prior-decision` | 2/6 | 6/6 | Baseline may answer from conversation memory. With-skill starts with `search`/`context`, reads selected pages, and cites paths. |
| `ambiguous-save` | 2/6 | 6/6 | With-skill pauses for clarification instead of turning a vague request into permanent memory. |
| `project-analysis-boundary` | 2/6 | 6/6 | With-skill keeps analysis host-led, then persists structured project memory through `gkh.py project`. |

## Aggregate

| Mode | Passed Assertions | Pass Rate |
| --- | ---: | ---: |
| Baseline | 13/36 | 36.1% |
| With Skill | 35/36 | 97.2% |

Delta: **+61.1 percentage points**

## Findings

### What the skill improves

- Converts vague memory requests into the correct persistence workflow.
- Prevents accidental full-Wiki context dumps during recall.
- Makes third-party knowledge summary-first and fetch-on-demand by default.
- Keeps local project analysis inside the host CLI boundary while providing a deterministic `project` persistence command.
- Forces outcome reporting: written paths, redaction/error status, and future recall commands.

### Remaining gaps

- `growth-review` depends on the host CLI having enough recent context or recalled memories; the skill correctly says to ask when context is insufficient, but a live runner would need to prove that behavior.
- This dry run should eventually be replaced by live with-skill/baseline model trials if a suitable isolated runner is available.

## Verdict

The skill provides a large behavioral lift over baseline for its core purpose. The biggest measured value is not better wording; it is workflow discipline: selecting one memory workflow, producing structured input, using local deterministic commands, and reporting safe provenance-aware results.
