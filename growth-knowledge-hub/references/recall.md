# Recall

Use this workflow when the user asks what they previously decided, learned, captured, reviewed, or planned.

Start with compact recall:

```bash
python scripts/gkh.py search --query "成长知识中枢" --limit 10
python scripts/gkh.py context --query "成长知识中枢" --limit 5
```

Read selected pages only when the user needs details:

```bash
python scripts/gkh.py read --path "wiki/growth/decisions/example.md"
```

## Guidance

- Do not read the entire Wiki into context.
- Prefer `context` for current-task context packs.
- Use `read` only for selected pages from search/context results.
- Respect `local_only` and sensitivity metadata. If a page is local-only, do not expose its body.
- Cite page paths or titles when answering from recall.
