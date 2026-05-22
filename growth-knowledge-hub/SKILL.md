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

When the user's intent is still fuzzy, pause before writing anything and decide which workflow fits best. A short clarification is better than saving the wrong thing into long-lived memory.

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

If the user says something broad like "帮我记一下" or "整理一下", first decide whether it is conversation capture, external material ingestion, growth review, recall, or project analysis. If more than one path looks plausible, ask one concise question before writing.

## Execution Loop

For write workflows, use this loop:

1. Select exactly one reference workflow and read it.
2. Extract structured data from the conversation or material:
   - **capture**: Pull `title` (topic), `summary` (3-5 bullet points), `decisions` (what was decided), `insights` (non-obvious takeaways), `next_actions` (concrete next steps). Use the user's own words for key decisions.
   - **ingest**: Pull `title`, `summary_points` (max 6 durable points), `key_concepts` (terms to remember), `why_it_matters` (how this changes practice), `application_ideas` (what to do with this knowledge).
   - **review**: Pull `title`, `period` (e.g. "2026-W21"), `observations` (what happened), `progress` (what moved forward), `bottlenecks` (what blocked), `knowledge_gaps` (what's missing), `next_tasks` (concrete small tasks).
   - **project**: Let the host CLI inspect the project with its normal tools, then pull `project`, `summary`, `architecture`, `decisions`, `lessons`, `risks`, `next_actions`, and `source_paths`.
   - **Checkpoint**: Before proceeding, verify the extracted data matches the user's intent. If the intent is ambiguous, the content looks sensitive, or more than one workflow could apply, pause and ask one concise clarification question (see Pause Points).
3. Store the JSON in a temporary file or host-managed scratch file.
4. Run the matching `gkh.py` command.
   - **Checkpoint**: If the script returns an error, do not proceed to step 5. Report the error plainly, keep or show the temporary JSON, and ask the user whether to revise and retry.
5. Report the result in human terms: what was written, where it was written, whether anything was redacted, and how to recall it later.

For recall workflows, start with `search` or `context`. Use `read` only for selected pages from the result list.

### End-to-End Example

User says: "我们刚才讨论了 skill 架构，帮我沉淀一下"

Host CLI actions:
1. Read `references/conversation-capture.md`
2. Generate JSON:
   ```json
   {
     "title": "Skill 架构设计讨论",
     "captured_from": "current_conversation",
     "summary": ["项目从独立 agent 转向 skill 化记忆层"],
     "decisions": ["宿主 CLI 负责对话，skill 负责本地沉淀"],
     "insights": ["长期知识闭环才是核心价值"],
     "open_questions": ["如何同时服务多个宿主 CLI？"],
     "next_actions": ["实现 capture 和 recall 命令"],
     "growth_tracks": ["agent_engineering"],
     "tags": ["skill", "architecture"]
   }
   ```
3. Save to `capture.json`
4. Run: `python scripts/gkh.py capture --input capture.json`
5. Report: "已写入 `wiki/growth/reviews/skill-架构设计讨论.md`，包含摘要、决策、洞察和下一步。可通过 `search --query 'skill 架构'` 召回。"

## Bundled Script

Run the script from the skill directory:

```bash
python scripts/gkh.py init
python scripts/gkh.py capture --input capture.json
python scripts/gkh.py ingest --input material.json
python scripts/gkh.py review --input review.json
python scripts/gkh.py project --input project.json
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
- The script does not call remote models, does not execute arbitrary skills, and does not scan repositories. For project analysis, the host CLI inspects files and passes structured lessons to `project`.

## Pause Points

Stop and ask the user before proceeding when any of these are true:

1. The request could map to more than one reference workflow.
2. The host CLI only has raw material and cannot tell whether the user wants capture, ingest, or review.
3. The content looks sensitive, but the host CLI has not yet decided whether redaction or rejection is more appropriate.
4. The user asked for local project analysis, but the scope of the project lesson is unclear.

These checkpoints keep the skill from turning every vague prompt into a permanent memory write.
