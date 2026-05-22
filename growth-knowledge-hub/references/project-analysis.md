# Project Analysis

Project analysis is intentionally a future workflow.

For first-version use, do not ask the bundled script to scan repositories. If the user asks to analyze a local project, the host CLI may inspect files using its normal tools and then either:

- Capture the discussion as ordinary conversation knowledge.
- Ingest a manually produced project summary as material.

A later workflow can accept structured project analysis input and write:

```text
wiki/projects/<project>/
  overview.md
  architecture.md
  decisions.md
  lessons.md
  risks.md
```

