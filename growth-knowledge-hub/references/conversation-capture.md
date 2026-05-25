# Conversation Capture

Use this workflow when the user asks to沉淀, save, record, capture, or summarize the current discussion into long-lived growth knowledge.

The host CLI should first summarize the current conversation. Then write a JSON file and call:

```bash
python scripts/gkh.py capture --input capture.json
```

## Input Shape

```json
{
  "title": "重新定位为成长知识 Skill",
  "captured_from": "current_conversation",
  "summary": ["The discussion reframed the project from agent app to skill-based memory layer."],
  "decisions": ["Host CLIs handle chat and tool orchestration."],
  "insights": ["The unique value is durable growth knowledge, not another agent runtime."],
  "open_questions": ["Which host CLI install locations should be documented first?"],
  "next_actions": ["Create the growth-knowledge-hub skill package."],
  "growth_tasks": [
    {
      "title": "为 growth-knowledge-hub 编写 SKILL.md，定义 3 条行为规则",
      "stage": "L2",
      "done_definition": "SKILL.md 存在且包含至少 3 条可验证的行为规则",
      "rationale": "当前对话展示了架构设计能力，但缺少 prompt 工程实践"
    }
  ],
  "tags": ["skill", "llm-wiki"]
}
```

## Guidance

- Keep `summary`, `decisions`, `insights`, `open_questions`, and `next_actions` concise and user-readable.
- Prefer the user's actual words for important decisions.
- Do not include raw secrets, credentials, or full private conversation logs.
- Capture durable meaning: decisions, reframes, reusable principles, and next actions.
- If the discussion has no durable value, answer normally without writing.
- Do not capture one-off troubleshooting chatter, temporary command output, or casual conversation unless it produced a durable decision, lesson, or next action.
- After a successful write, tell the user the written page path, the main sections saved, and any redaction reported by the script.
- If the script returns an error, do not say the capture succeeded. Show the error and revise the JSON before retrying.

### Growth Tasks Generation

- Read `references/growth-stage-model.md` before generating tasks.
- Assess which stage (L1-L4) the conversation reflects based on what the user was doing.
- Generate 1-3 tasks that push toward the **next** stage, not the current one.
- Each task must be concrete and actionable: something the user can do in their next session.
- `done_definition` must be verifiable — something you can check yes/no.
- `rationale` should explain why this task is relevant now, based on the conversation.
- If the conversation is trivial (simple bug fix, one-line change), skip `growth_tasks` entirely.
- If a similar task already exists in `wiki/growth/tasks/` with status `active`, do not include it — the script will skip it anyway, but don't waste the user's attention.
