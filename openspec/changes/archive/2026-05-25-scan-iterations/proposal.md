## Why

当前 growth-knowledge-hub 的 project-analysis workflow 只能沉淀宿主 CLI 手动总结的项目经验，无法自动从 git 历史中提取迭代节奏、团队协作模式和代码质量信号。用户需要一个自动化工具，扫描多个项目的 release 分支，生成结构化迭代记录，沉淀到知识库中作为项目记忆的一部分。

## What Changes

- 新增 `scan-iterations` 子命令，扫描指定目录下所有项目的 git 仓库。
- 自动识别 `release/*` 分支（前缀可配置），按分支名日期排序。
- 每个迭代分支与前一个分支对比（首个对比 main/master），提取：主要事项、提交人数、每人代码量、改动文件数、稳定性、规范性。
- 输出 Markdown 表格：迭代记录总表 + 每个迭代的提交人明细。
- 可选沉淀到 `wiki/projects/<project>/iterations.md`。

## Capabilities

### New Capabilities
- `project-iteration-scan`: 扫描多项目 git 仓库，提取 release 分支迭代记录，生成结构化 Markdown 表格并沉淀到知识库。

### Modified Capabilities
- `project-analysis`: 与现有 project workflow 互补，iteration scan 提供客观 git 数据，project workflow 提供主观经验总结。

## Impact

- Affected files: `growth-knowledge-hub/scripts/gkh.py`, `growth-knowledge-hub/SKILL.md`, `growth-knowledge-hub/references/` (新增 `scan-iterations.md`)
- Dependencies: 仅依赖 git CLI（纯本地，无远程 API）
- Breaking: 无，纯新增功能
