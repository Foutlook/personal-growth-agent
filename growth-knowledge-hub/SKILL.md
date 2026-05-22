---
name: growth-knowledge-hub
description: Use this skill whenever the user wants to沉淀, capture, save, recall, search, review, or organize personal growth knowledge, current AI collaboration discussions, external learning material, notes, articles, knowledge-base summaries, or local project lessons into a durable local LLM Wiki. Also use it when the user asks what they previously decided, learned, reviewed, or planned, because the skill can recall compact context from the local growth knowledge base.
compatibility: Requires Python 3.10+ for bundled standard-library scripts.
---

# Growth Knowledge Hub

Growth Knowledge Hub turns mature AI CLIs such as Codex, Claude Code, and OpenCode into a personal growth knowledge system. The host CLI does the thinking: it reads the current conversation, materials, or project context and creates structured JSON. This skill's bundled script does the deterministic local work: validate, redact, write Markdown, update provenance, search, recall, and build a small dashboard.

Use this skill for:

- Capturing the current discussion as growth knowledge.
- Saving external materials, articles, notes, or third-party knowledge summaries.
- Writing growth reviews, bottlenecks, knowledge gaps, and next actions.
- Recalling prior decisions, lessons, summaries, tasks, and growth notes.
- Building a local no-server dashboard for the knowledge base.

Do not use this skill to replace the host CLI's chat, tool calling, file reading, or model routing. The host CLI remains the agent; this skill is the memory layer.

## Workflow Selection

Read only the reference needed for the user's current intent:

| Intent | Reference |
| --- | --- |
| "沉淀这次讨论", "保存这次对话", "capture this conversation" | `references/conversation-capture.md` |
| "整理这篇文章", "保存资料", "导入知识库摘要", "ingest this material" | `references/material-ingest.md` |
| "做一次复盘", "本周成长回顾", "下一步怎么练" | `references/growth-review.md` |
| "我之前怎么想的", "查一下我的知识库", "recall prior decisions" | `references/recall.md` |
| Need exact local Wiki layout or metadata rules | `references/llm-wiki-schema.md` |
| Local project analysis request | `references/project-analysis.md` |

## Bundled Script

Run the script from the skill directory:

```bash
python scripts/gkh.py init
python scripts/gkh.py capture --input capture.json
python scripts/gkh.py ingest --input material.json
python scripts/gkh.py review --input review.json
python scripts/gkh.py search --query "成长知识中枢"
python scripts/gkh.py context --query "agent 架构" --limit 5
python scripts/gkh.py read --path "wiki/growth/reviews/example.md"
python scripts/gkh.py dashboard
```

Data is stored outside the skill directory:

1. `GKH_HOME` when set.
2. Project-local `.growth-knowledge/` when `--scope project` is used and that directory exists or can be created.
3. User-level `~/.growth-knowledge-hub/` by default.

The local Wiki lives at `<data-home>/llm-wiki/`.

## Safety Rules

- Never dump the whole Wiki into model context. Use `search` or `context`, then `read` selected pages only when needed.
- Do not persist full third-party content by default. Save summary-first notes and source locators.
- If the user provides secrets, tokens, private keys, or local-only material, redact or reject before writing.
- The script does not call remote models, does not execute arbitrary skills, and does not scan repositories unless a future workflow explicitly supports it.
