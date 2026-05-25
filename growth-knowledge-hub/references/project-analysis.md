# Project Analysis

Use this workflow when the user asks to analyze a local project and preserve reusable architecture decisions, lessons, risks, or follow-up work in the growth knowledge base.

The host CLI must inspect the project with its normal tools. The bundled script must not scan repositories, call models, or infer project meaning by itself. After the host has produced structured lessons, write a JSON file and call:

```bash
python scripts/gkh.py project --input project.json
```

## Input Shape

```json
{
  "project": "personal-growth-agent",
  "title": "Growth Knowledge Hub 重构经验",
  "summary": ["项目从独立 agent 收敛为可复用 skill。"],
  "architecture": ["宿主 CLI 负责对话和工具调用，skill 负责本地知识沉淀。"],
  "decisions": ["删除旧 pga CLI，保留 gkh.py 标准库脚本。"],
  "lessons": ["不要重复造 Codex、Claude、OpenCode 已经成熟的 agent runtime。"],
  "risks": ["project 命令只能接收宿主总结，不能自行扫描代码。"],
  "next_actions": ["补项目经验召回入口。"],
  "source_paths": ["growth-knowledge-hub/SKILL.md", "growth-knowledge-hub/scripts/gkh.py"],
  "tags": ["project-analysis", "architecture"]
}
```

## Output

The script writes:

```text
wiki/projects/<project>/
  overview.md
  architecture.md
  decisions.md
  lessons.md
  risks.md
```

## Guidance

- Keep `source_paths` as relative paths or safe labels. Do not paste full source code into the JSON.
- Focus on durable project lessons: architecture, decisions, tradeoffs, risks, and future reuse.
- Do not use project analysis as proof of personal mastery; it is project memory and learning context.
- After a successful write, tell the user the project page paths and how to recall them later.
- If the script returns an error, do not claim the project analysis was saved. Fix the structured input before retrying.
