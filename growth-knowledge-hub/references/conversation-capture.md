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
  "growth_tracks": ["agent_engineering", "knowledge_management"],
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
