# Material Ingest

Use this workflow when the user wants to save an article, note, document, third-party knowledge result, or external knowledge-base summary into the local growth knowledge base.

The host CLI should read or retrieve the material, generate a summary-first JSON file, and call:

```bash
python scripts/gkh.py ingest --input material.json
```

## Input Shape

```json
{
  "title": "Agent Harness Engineering",
  "source_type": "external_material",
  "source_locator": "ima:media:opaque-id-or-url",
  "summary_points": [
    "Harness connects model decisions to safe, typed tool execution.",
    "Tool results should be compact and provenance-aware."
  ],
  "key_concepts": ["tool boundary", "provenance", "recall context"],
  "why_it_matters": "This helps turn agent experience into reusable system design knowledge.",
  "application_ideas": ["Use compact context packs for local memory recall."],
  "open_questions": ["How should project-level memories differ from user-level memories?"],
  "tags": ["agent_engineering", "knowledge_management"]
}
```

## Guidance

- `summary_points` must contain at most six durable points.
- Do not persist full third-party bodies by default. Use `source_locator` and summary-first notes.
- Include how the material might change future practice, not only what it says.
- Mark unresolved questions clearly so they can become growth tasks later.

