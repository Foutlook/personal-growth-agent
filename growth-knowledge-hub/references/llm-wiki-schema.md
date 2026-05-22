# LLM Wiki Schema

The local Wiki lives under `<data-home>/llm-wiki/`.

```text
llm-wiki/
  AGENTS.md
  SCHEMA.md
  raw/
    conversations/
    materials/
    reviews/
  wiki/
    growth/
      reviews/
      decisions/
      tasks/
    knowledge/
      concepts/
      external-summaries/
      gaps/
  data/
    source-manifest.json
    wiki-write-log.json
    index.json
  dashboard/
    index.html
```

Every write must preserve:

- Source manifest entry with source ID, raw source ID, source type, locator, timestamp, sensitivity, and hash.
- Wiki write-log entry with target path, operation, source raw IDs, content hash, and timestamp.
- Human-readable Markdown with frontmatter.

External material summaries are long-lived and summary-first. Full third-party content is fetched or stored only by explicit future workflows.

