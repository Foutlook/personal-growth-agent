# Growth Knowledge Hub

Growth Knowledge Hub 是一个面向 Codex、Claude Code、OpenCode 等 AI CLI 的个人成长知识 Skill。它不再实现独立 agent、交互式 REPL 或模型调用流程，而是专注做一件事：把 AI 协作、外部资料、成长复盘和项目经验沉淀为本地长期知识库，并在之后按需召回。

宿主 CLI 负责对话理解、工具编排、资料读取和总结分析；本项目提供可被宿主调用的 skill 说明与本地确定性脚本。

## 核心定位

- 个人学习记忆库：长期保存用户可读的成长笔记、决策、知识缺口、复盘和下一步行动。
- 本地知识沉淀系统：默认写入本机 `llm-wiki/`，不需要服务端，不默认上传原始素材。
- AI CLI skill：把 `growth-knowledge-hub/` 放到 Codex、Claude Code、OpenCode 等宿主的 skill 目录后，由宿主模型按需读取说明并调用脚本。
- Summary-first 外部资料沉淀：三方知识库、网页、文章和笔记默认只长期保存 6 条以内摘要要点、来源 locator 和后续按需读取策略。
- 紧凑召回：通过 `search`、`context`、`read` 返回小而可溯源的上下文，避免把整个知识库塞进模型上下文。
- 静态 Dashboard：生成无需启动服务的本地查看页面。

## 目录结构

```text
growth-knowledge-hub/
  SKILL.md
  skill.json
  references/
    conversation-capture.md
    material-ingest.md
    growth-review.md
    recall.md
    llm-wiki-schema.md
    project-analysis.md
  scripts/
    gkh.py
```

`SKILL.md` 是宿主 CLI 首先读取的能力说明。`references/` 存放分场景说明，宿主模型只需要读取当前意图对应的文件。`scripts/gkh.py` 只使用 Python 标准库，负责本地校验、脱敏、写入、索引、召回和 Dashboard 生成。

## 安装到宿主 CLI

把 `growth-knowledge-hub/` 整个目录复制或软链接到宿主 CLI 的 skill 目录即可。不同宿主的目录规范不同，但最终都应该让宿主能看到：

```text
growth-knowledge-hub/SKILL.md
growth-knowledge-hub/references/
growth-knowledge-hub/scripts/gkh.py
```

本项目不要求安装 Python package，也不提供独立 `pga` 命令。

## 数据目录

默认数据目录：

```text
~/.growth-knowledge-hub/llm-wiki
```

也可以通过环境变量覆盖：

```powershell
$env:GKH_HOME = "D:\my-growth-memory"
python growth-knowledge-hub\scripts\gkh.py init
```

项目级知识可以使用：

```bash
python growth-knowledge-hub/scripts/gkh.py --scope project init
```

项目级模式会使用当前项目下的 `.growth-knowledge/llm-wiki/`。

## 常用命令

初始化：

```bash
python growth-knowledge-hub/scripts/gkh.py init
```

沉淀当前对话：

```bash
python growth-knowledge-hub/scripts/gkh.py capture --input capture.json
```

沉淀外部资料摘要：

```bash
python growth-knowledge-hub/scripts/gkh.py ingest --input material.json
```

写入成长复盘：

```bash
python growth-knowledge-hub/scripts/gkh.py review --input review.json
```

搜索与召回：

```bash
python growth-knowledge-hub/scripts/gkh.py search --query "成长知识中枢" --limit 10
python growth-knowledge-hub/scripts/gkh.py context --query "项目经验沉淀" --limit 5
python growth-knowledge-hub/scripts/gkh.py read --path "wiki/growth/reviews/example.md"
```

生成静态 Dashboard：

```bash
python growth-knowledge-hub/scripts/gkh.py dashboard
```

## 宿主调用方式

典型流程：

1. 用户在 Codex、Claude Code 或 OpenCode 中说“沉淀这次讨论”“整理这篇资料”“查一下我之前怎么想的”。
2. 宿主 CLI 读取 `growth-knowledge-hub/SKILL.md`。
3. 宿主模型根据意图读取一个 reference 文件，例如 `references/conversation-capture.md`。
4. 宿主模型把当前对话、资料或复盘整理成结构化 JSON。
5. 宿主调用 `scripts/gkh.py` 写入或召回本地 `llm-wiki/`。

```text
用户意图
  │
  ▼
宿主 CLI / 模型
  │  读取 SKILL.md + 一个 reference
  │  生成结构化 JSON 或查询参数
  ▼
growth-knowledge-hub/scripts/gkh.py
  │
  ├─ validate / redact
  ├─ write markdown
  ├─ update manifest / index / write-log
  └─ search / context / dashboard
```

## 输入示例

对话沉淀：

```json
{
  "title": "重新定位为成长知识 Skill",
  "captured_from": "current_conversation",
  "summary": ["项目从 standalone agent 转向可被宿主 CLI 调用的成长知识 skill。"],
  "decisions": ["宿主 CLI 负责对话和工具编排，skill 负责本地沉淀与召回。"],
  "insights": ["独特价值是长期成长知识，而不是另一个 agent runtime。"],
  "open_questions": ["如何同时服务 Codex、Claude Code 和 OpenCode？"],
  "next_actions": ["实现 capture、ingest、review 和 recall。"],
  "growth_tracks": ["agent_engineering", "knowledge_management"],
  "tags": ["skill", "llm-wiki"]
}
```

外部资料摘要：

```json
{
  "title": "Agent Harness Engineering",
  "source_type": "external_material",
  "source_locator": "ima:media:opaque-id-or-url",
  "summary_points": ["Harness connects model decisions to safe tool execution."],
  "key_concepts": ["tool boundary", "provenance", "recall context"],
  "why_it_matters": "This helps turn agent experience into reusable design knowledge.",
  "application_ideas": ["Use compact context packs for local memory recall."],
  "open_questions": ["How should project-level memories differ from user-level memories?"],
  "tags": ["agent_engineering"]
}
```

`summary_points` 最多保留 6 条。完整三方内容默认不落盘，只保存来源 locator 和 `full_content_policy: fetch_on_demand`，后续需要细节时由宿主 CLI 再按需访问原始来源。

## 本地 Wiki

`llm-wiki/` 是长期知识库：

```text
llm-wiki/
  AGENTS.md
  SCHEMA.md
  wiki/
    growth/
    knowledge/
    projects/
  data/
    source-manifest.json
    wiki-write-log.json
    index.json
  dashboard/
    index.html
```

`wiki/` 中保存用户可读 Markdown；`data/` 保存机器可读索引、来源和写入记录；`dashboard/` 保存静态页面。

可以直接用 Obsidian 或任意 Markdown 编辑器打开 `llm-wiki/`。Dashboard 更适合快速查看页面索引、来源、写入记录和隐私状态。

## 隐私边界

- 默认不调用远程模型，脚本只做本地确定性读写。
- 默认不保存三方完整原文，只保存摘要与来源。
- 写入前会对常见 secret、token、private key 等内容脱敏或拒绝。
- `context` 默认返回紧凑上下文；需要细节时再 `read` 指定页面。
- 不扫描宿主 CLI 对话数据库，不接管宿主工具系统，不执行任意 shell。

## 开发验证

运行测试：

```bash
python -m pytest -q
```

校验 OpenSpec：

```bash
openspec validate --all --strict
```

当前代码主路径只覆盖 `growth-knowledge-hub` skill。旧独立 agent、`pga` CLI、交互 REPL、provider 配置和旧测试已经不再是项目目标。
