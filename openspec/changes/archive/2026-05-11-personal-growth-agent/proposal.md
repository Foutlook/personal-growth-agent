## Why

AI 协作记录、代码仓库结构和成长任务产物中包含大量高价值成长证据，但这些信息通常散落在 Codex、Claude Code、opencode 对话和本地项目中，难以转化为持续行动。需要一个个人成长执行系统，把真实协作证据转化为可完成、可验证、可复盘的成长任务，并沉淀为可溯源、可审核、可复用的 LLM Wiki 长期知识资产。

这个 change 以“成为 AI Agent 工程师、从信息中转者到业务深度专家、成为 AI 系统的管理者和优化者”为 North Star，建立从数据摄入、证据抽取、成长任务生成到 LLM Wiki 维护的最小闭环。

## What Changes

- 引入本地 AI 协作记录发现与解析能力，优先支持 Codex、Claude Code、opencode。
- 引入 EvidenceItem 和 EvidenceSignal，用标准化证据信号支撑诊断、成熟度初判和任务路由。
- 引入三轨成长模型：AI Agent 工程能力、业务深度专家能力、AI 系统管理与优化能力。
- 引入 GrowthCycle，生成一轮可执行成长任务包，包括 GrowthTask、完成定义、复盘问题和预期产物。
- 引入 ActionAsset，生成可进入下一轮 AI 协作的 prompt、checklist、template、agent rule 和 playbook。
- 引入 LLM Wiki 维护能力，采用 raw -> diff -> review -> wiki 的流程维护长期知识资产。
- 引入隐私脱敏和审计能力，确保原始对话、代码和敏感信息默认留在本地，并记录外发、脱敏和 Wiki 更新情况。
- 引入可选仓库补充分析能力，仅在用户确认仓库路径后扫描 Git 元数据、目录结构和工程化信号。

## Capabilities

### New Capabilities

- `conversation-source-ingestion`: 发现、检查和解析 Codex、Claude Code、opencode 的本地 AI 协作记录，并生成统一 ConversationSession。
- `evidence-signal-extraction`: 从会话、工具调用和仓库摘要中抽取 EvidenceItem，并聚合为标准化 EvidenceSignal。
- `growth-cycle-execution`: 基于三轨 North Star、成熟度初判和 Diagnosis 生成一轮 GrowthCycle 与可执行 GrowthTask。
- `action-asset-generation`: 为成长任务生成可复用 ActionAsset，包括 prompt、checklist、template、agent rule 和 playbook。
- `llm-wiki-maintenance`: 维护 llm-wiki/ 长期知识资产，支持 RawSource、SourceManifest、WikiPage、WikiUpdateProposal、diff-first 审核和 Wiki Lint。
- `privacy-audit`: 对本地数据读取、脱敏、外发 payload、ActionAsset、WikiPage 和 WikiUpdateProposal 进行隐私控制与审计。
- `repository-signal-analysis`: 在用户确认仓库路径后，提取 Git 元数据、目录结构、文档、测试、CI、脚本和 Agent 规则文件等工程化信号。

### Modified Capabilities

None. There are no existing OpenSpec capabilities in this project yet.

## Impact

- Affected systems: new local analysis pipeline, OpenSpec specifications, future CLI or service entrypoint, report generation, persistent `llm-wiki/` workspace, and `runs/` execution snapshots.
- Data model impact: introduces ConversationSession, RawSource, SourceManifest, EvidenceItem, EvidenceSignal, Diagnosis, MaturityEstimate, GrowthCycle, GrowthTask, ActionAsset, WikiPage, WikiUpdateProposal, WikiLintIssue, and PrivacyAudit.
- Storage impact: creates long-lived `llm-wiki/` assets and per-run `runs/<timestamp>/` outputs.
- Privacy impact: requires strict local-first defaults, redaction before LLM use, auditable outbound payloads, read-only raw sources, and diff-first human review for Wiki updates.
- Non-goals for this change: Web UI, trend dashboard, automatic diff application, deep code review, multi-repository batch scanning, business system integration, GraphRAG, team permissions, and fine-tuning dataset generation.
