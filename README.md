# Personal Growth Agent

Personal Growth Agent 是一个本地优先的个人成长检测反馈工具。它会分析 Codex、Claude Code、opencode 等 AI 协作对话，抽取行为证据，生成角色/能力诊断、成长任务、Action Assets，并把长期知识沉淀到 LLM Wiki。

它也可以把网页文章、公众号文章摘录、个人笔记、本地 Markdown 文档等外部知识纳入同一个 LLM Wiki，并生成无需启动服务的静态 Dashboard。

## 核心能力

- 分析 AI 协作对话，推断角色、能力特点、优势、风险和成长方向。
- 面向 AI Agent 工程师、业务深度专家、AI 系统管理者三个方向生成成长任务。
- 提供 `pga` 交互模式：自由对话、流式回答、`/` 快捷命令和受控本地工具调用。
- 将报告、诊断、任务、成熟度快照、知识缺口沉淀到 `llm-wiki/`。
- 摄取外部知识：note、file、web/article text。
- 生成静态 Dashboard，可直接打开 HTML 文件查看报告、Wiki、成长任务、来源和隐私状态。
- 默认本地处理原始资料。成长分析的外部 LLM 调用需要显式批准；交互模式的自由对话会按已配置的 provider/model 直接调用外部 LLM。

## 安装与升级

建议使用 Python 3.10+。

本地开发安装：

```powershell
cd C:\Users\lingq\Documents\trae_projects\personal-growth-agent
python --version
python -m pip install -e .
```

安装后验证：

```powershell
pga --help
```

如果 `pga` 命令不可用，可以先用模块方式运行：

```powershell
python -m personal_growth_agent.cli --help
```

更新：

```powershell
cd C:\Users\lingq\Documents\trae_projects\personal-growth-agent
git pull
python -m pip install -e .
```

如果不是 Git 仓库，只需要替换项目文件后重新执行：

```powershell
python -m pip install -e .
```

卸载：

```powershell
python -m pip uninstall personal-growth-agent
```

卸载包不会自动删除你的工作区数据。默认工作区是：

```text
C:\Users\<你>\pga-workspace
```

## 5 分钟开始

初始化工作区：

```bash
pga init
```

可选：如果希望交互对话或增强分析调用 DeepSeek，在默认工作区的 `config.toml` 里配置 API key，或设置环境变量：

```powershell
setx PGA_DEEPSEEK_API_KEY "你的 DeepSeek API Key"
```

进入交互模式：

```bash
pga
```

在交互模式里可以直接提问：

```text
我最近最应该补哪块能力？
帮我总结最新成长报告。
哪些知识缺口最影响我现在的任务？
```

也可以使用本地快捷命令：

```text
/tasks
/summary
/run
/dashboard
```

如果你更喜欢传统命令式流程，也可以直接运行：

```bash
pga sources scan
pga run
pga dashboard open
```

## 交互模式

执行 `pga` 且不带子命令时，会进入终端交互模式。

输入分两类：

- 普通输入：作为自由对话发送给已配置 LLM，支持流式输出和受控本地工具调用。
- `/` 开头：本地快捷命令，不经过 LLM，确定性执行。

内置快捷命令：

```text
/help
/tasks
/task complete <task-id>
/wiki
/gaps
/summary
/run
/dashboard
/exit
/quit
```

自由对话可调用的本地工具限定为白名单：

```text
get_latest_report
list_growth_tasks
complete_growth_task
list_wiki_pages
read_wiki_page
list_knowledge_gaps
run_growth_cycle
build_open_dashboard
```

不会开放任意 shell，不会让模型随意读写本地文件。

对话记录会保存到：

```text
C:\Users\<你>\pga-workspace\conversations\YYYY-MM-DD\<session-id>.jsonl
```

这些记录只做本地留存，不会写入 `llm-wiki/`，也不会加入 Wiki source manifest。

## 常用命令

初始化：

```bash
pga init
```

扫描默认 AI 对话来源：

```bash
pga sources scan
```

运行一次成长分析：

```bash
pga run
```

如果要允许成长分析调用远程 LLM：

```bash
pga run --approve-outbound
```

查看最新报告路径：

```bash
pga report latest
```

查看当前 Wiki 路径：

```bash
pga wiki path
```

生成并打开静态 Dashboard：

```bash
pga dashboard build
pga dashboard open
```

完成成长任务：

```bash
pga tasks complete <task-id>
```

查看 prompt 目录和某个场景的 prompt 文件：

```bash
pga prompts path
pga prompts show role_profile
```

所有命令都支持同一套工作区解析规则，可用 `--workspace <path>` 或 `--wiki <path>` 覆盖默认位置。

## 工作区结构

执行 `pga init` 后只生成必要文件：

```text
pga-workspace/
  config.toml
  llm-wiki/
    AGENTS.md
    SCHEMA.md
```

默认工作区位于：

```text
C:\Users\<你>\pga-workspace
```

其他目录会在使用对应功能时按需生成：

- `conversations/YYYY-MM-DD/`：交互模式对话记录，不进入 Wiki。
- `runs/YYYY-MM-DD/`：执行 `pga run` 后生成，保存当天分析输出、证据链、privacy audit 和报告。
- `source-manifests/`：执行 `pga sources scan` 后生成，保存本地 AI CLI 对话来源扫描结果。
- `dashboard/`：执行 `pga dashboard build` 后生成，保存无需启动服务的静态页面。
- `llm-wiki/raw/knowledge/`：执行 `pga ingest ...` 后生成，保存外部知识原始素材。
- `llm-wiki/wiki/`：执行 `pga run` 或 `pga ingest ...` 后生成，保存结构化 Markdown 知识页。
- `llm-wiki/data/`：保存成长任务、成长记忆机器状态、source manifest、Wiki 写入日志、知识摄取索引等数据。
- `llm-wiki/report/`：保存 Wiki lint 等报告。

成长任务当前未完成项保存在：

```text
C:\Users\<你>\pga-workspace\llm-wiki\data\growth-tasks\active.json
```

完成任务后会移动到：

```text
C:\Users\<你>\pga-workspace\llm-wiki\data\growth-tasks\archive.json
```

## LLM Wiki

`llm-wiki/` 是长期知识库，遵循直接合并版 LLM Wiki 结构：

- `raw/`：原始素材层，只读、可溯源。外部知识在 `raw/knowledge/`，成长运行快照在 `raw/growth-runs/`。
- `wiki/`：结构化 Markdown 知识层，只放面向人阅读的编译结果。
- `data/`：机器状态层，保存 source manifest、`wiki-write-log.json`、成长任务和 `growth-memory/`。
- `prompts/`：摄取、分析、Wiki 编译等提示词。
- `report/`：Wiki lint 和运行报告。
- `AGENTS.md` / `SCHEMA.md`：约束 LLM 如何维护 Wiki。

AI 对话扫描结果不写入 `llm-wiki/raw/`。成长运行会把脱敏快照写入 `raw/growth-runs/`，把周期、诊断、成熟度快照等机器状态写入 `data/growth-memory/`。`wiki/growth/` 中只保留面向人阅读的成长概览、当前关注、任务和复盘页面。

本项目不走人工审核队列。LLM Wiki 更新采用 direct merge：系统从 raw/source 和 prompt 编译内容后直接写入 `wiki/`，并在 `data/wiki-write-log.json` 记录目标路径、来源、prompt digest、写入时间和内容 hash，便于追溯和回滚。

可以直接用 Obsidian 打开 `llm-wiki/` 目录，把它作为本地 Markdown Vault 使用：

```bash
pga wiki path
```

适合在 Obsidian 中查看的内容：

- `wiki/knowledge/`：外部知识和知识缺口。
- `wiki/growth/`：成长概览、当前关注、成长任务和复盘。
- `wiki/profile/`：个人画像和角色相关沉淀。
- `data/growth-memory/`：诊断、成熟度快照、周期等机器可读状态。
- `data/wiki-write-log.json`：Wiki 直接写入记录。
- `report/lint-reports/`：Wiki lint 报告。
- `AGENTS.md` / `SCHEMA.md`：Wiki 维护规则和结构约束。

推荐把 Obsidian 当作 Wiki IDE：用于阅读、搜索、双链和图谱。报告汇总、成长任务、隐私状态和 source manifest 更适合用静态 Dashboard 查看。

## 摄取外部知识

摄取一段个人笔记：

```bash
pga ingest note --title "Agent 评估笔记" --content "Agent 输出需要评价闭环。"
```

摄取本地 Markdown 文件：

```bash
pga ingest file ./notes/llm-wiki.md
```

摄取网页或公众号文章的复制文本：

```bash
pga ingest web \
  --title "LLM Wiki 方法" \
  --url "https://example.com/article" \
  --content "这里放复制后的文章正文"
```

默认不会偷偷抓取 URL。只有显式传入 `--fetch` 时才会尝试网络获取，并记录 fetch 审计信息：

```bash
pga ingest web \
  --title "远程文章" \
  --url "https://example.com/article" \
  --fetch
```

摄取结果会写入 `llm-wiki/raw/knowledge/`，并自动沉淀为 `llm-wiki/wiki/knowledge/` 下的正式 Wiki 页面。

也可以指定 raw 路径和 prompt 路径执行一次 Wiki 编译：

```bash
pga wiki compile --raw ./llm-wiki/raw/knowledge/files --prompt ./prompts/knowledge_ingest.zh.md
```

## 静态 Dashboard

生成并打开 Dashboard：

```bash
pga dashboard build
pga dashboard open
```

Dashboard 输出到：

```text
pga-workspace/dashboard/index.html
```

它是静态页面，不需要 `pga serve` 或任何本地服务。页面数据会同时写入 JSON 并内嵌到 HTML，便于直接用浏览器打开。

Dashboard 会展示：

- 最新成长报告
- Wiki 页面索引
- 成长任务
- 成熟度快照
- 诊断和知识缺口
- source manifest
- 隐私和 lint 状态

## 隐私边界

系统默认本地优先处理原始资料：

- 原始对话、代码、知识素材先在本地处理。
- source inventory 不包含原始消息正文。
- Dashboard 默认不暴露 raw message、raw code、secret、local-only 内容。
- `conversations/` 只保存交互对话留存，不写入 `llm-wiki/`。
- 任何 outbound payload 都应记录用途、目标、摘要、redaction 状态和 digest。

远程 LLM 调用分两类：

- 成长分析：需要显式 `--approve-outbound`，否则只生成 preview 或回退本地规则。
- 交互对话：按已配置的 provider/model 直接调用；如果没有 API key，会提示配置位置。

如果内容包含密钥、邮箱、内部 URL、手机号等敏感信息，系统会尝试脱敏或标记为 `local_only`。

## 模型配置

初始化后，配置文件在工作区：

```text
C:\Users\<你>\pga-workspace\config.toml
```

使用 DeepSeek 时，把 API key 填到：

```toml
[llm.providers.deepseek]
api_key = "你的 DeepSeek API Key"
```

也可以不写入文件，改用环境变量：

```powershell
setx PGA_DEEPSEEK_API_KEY "你的 DeepSeek API Key"
```

默认 DeepSeek 配置包含：

```toml
default_model = "deepseek-v4-flash"

[llm.providers.deepseek.models]
flash = "deepseek-v4-flash"
pro = "deepseek-v4-pro"
```

如果没有配置 API key，远程 LLM 调用会跳过或提示缺失凭证；成长分析仍可使用本地规则生成基础分析。

## Prompt 管理

不同分析场景使用不同 prompt，而不是共用一个大 prompt。

初始化后可以查看 prompt 目录：

```bash
pga prompts path
```

查看某个场景使用的 prompt 文件：

```bash
pga prompts show role_profile
```

默认场景包括：

- `role_profile`
- `maturity_scoring`
- `growth_planning`
- `evidence_enrichment`
- `knowledge_ingest`
- `wiki_maintenance`
- `report_generation`

Prompt 文件可直接编辑。系统会在 analyzer audit 中记录 prompt ID、version、digest、scenario、provider 和 model，便于追踪提示词变更对分析结果的影响。

## OpenSpec 开发流程

项目使用 OpenSpec 管理变更：

```bash
/opsx:propose <change-name>
/opsx:apply <change-name>
/opsx:sync <change-name>
/opsx:archive <change-name>
```

主规格在：

```text
openspec/specs/
```

已归档变更在：

```text
openspec/changes/archive/
```

当前已覆盖的能力包括 conversation source ingestion、interactive agent REPL、LLM Wiki maintenance、growth memory integration、external knowledge ingestion、static dashboard generation、privacy audit 等。

## 测试

运行完整测试：

```bash
python -m pytest
```

当前测试覆盖 CLI、workspace/config、对话 source adapter、交互模式、LLM provider、隐私脱敏、成长任务、LLM Wiki、外部知识摄取、静态 Dashboard 和 OpenSpec 变更相关行为。

## 设计原则

- 本地优先，不默认上传原始素材。
- 交互模式优先服务日常使用；传统 CLI 命令保留用于自动化。
- `/` 命令是确定性本地操作；普通输入是 LLM 自由对话。
- LLM 工具调用只开放白名单，不开放任意 shell。
- 对话记录留存在 `conversations/`，不自动进入 Wiki。
- raw 不覆盖，Wiki 默认自动写入正式 `wiki/` 页面。
- 外部知识是学习上下文，不是个人能力证据。
- 成熟度评估必须来自行为证据、仓库信号、用户确认或复盘。
- Dashboard 是静态查看界面，不是服务端应用。
- Obsidian 可以作为 Markdown Wiki IDE，但不是必需依赖。
