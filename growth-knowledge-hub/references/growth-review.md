# Growth Review

Use this workflow when the user asks for a growth review, weekly review, current bottleneck, next practice task, or learning plan.

The host CLI should inspect relevant recent context or recalled memories, generate a structured review JSON file, and call:

```bash
python scripts/gkh.py review --input review.json
```

## Input Shape

```json
{
  "title": "本周成长复盘",
  "period": "2026-W21",
  "observations": ["The user noticed the project was drifting into a generic agent runtime."],
  "progress": ["Reframed the product as a skill-based knowledge hub."],
  "bottlenecks": ["Scope control around agent/runtime features."],
  "knowledge_gaps": ["How to package one skill for several host CLIs."],
  "next_tasks": ["Ship a minimal standard-library local writer and recall command."],
  "related_pages": [],
  "tags": ["review", "growth"]
}
```

## Guidance

- Treat review conclusions as inferred memory unless the user explicitly confirms them.
- Keep tasks concrete and small enough to do next.
- Link related pages when recall results or previous tasks informed the review.
- Do not infer mastery from reading material alone; learning material is context, not capability evidence.
- Do not create a review when the user only asked for a factual answer or a one-off task.
- If recent context is insufficient, ask for the review period, focus area, or source memories before writing.
- After a successful write, tell the user the review page path and the task pages created.
- If the script returns an error, do not claim the review was saved. Explain what field or content needs correction.
