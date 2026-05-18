# Personal Growth Agent：成长执行系统设计文档

## 1. 背景与设计原则

Personal Growth Agent 是一个基于 AI 协作记录和项目证据的个人成长执行系统。它分析 Codex、Claude Code、opencode 等工具中的真实工作记录，抽取可追溯证据和标准行为信号，围绕用户的长期成长目标生成一轮可完成、可验证、可复盘的成长任务，并沉淀为可复用的行动资产和 LLM Wiki。

LLM Wiki 是以 Markdown 为载体、LLM 为维护者、人类为监督者的个人成长知识编译层。它将 AI 协作记录、仓库证据、成长任务产物和复盘结果持续转化为可溯源、可链接、可审核、可复用的长期知识资产。

系统不以“评价用户”为终点，而以“驱动下一轮成长行动”为终点。角色画像、职级推断和专业评分只作为任务路由的背景信息，不作为 MVP 的中心产物。

核心设计原则：

- 行动优先：报告首页先给本轮任务，而不是先给评分。
- 证据驱动：所有诊断、任务、WikiPage 和行动资产必须引用 EvidenceItem 或 RawSource。
- 三轨对齐：所有成长任务必须服务 AI Agent 工程能力、业务深度专家能力、AI 系统管理与优化能力中的至少一条。
- 可执行：每个 GrowthTask 必须包含步骤、完成定义、时间预算、复盘问题和预期产物。
- 可复用：每轮至少产出 prompt、checklist、template、agent rule 或 playbook 之一。
- Wiki-first 沉淀：长期知识不直接写成零散笔记，而是通过 raw -> diff -> review -> wiki 的 LLM Wiki 流程沉淀。
- 隐私优先：原始对话和代码默认留在本地，外发内容必须脱敏、压缩和审计。

设计警戒线：

```text
任何不能转化为 GrowthTask、ActionAsset、WikiUpdateProposal 或 WikiPage 的分析结论，都不应该成为 MVP 的核心输出。
```

## 2. 成长 North Star

用户的长期成长目标不是泛化“变得更优秀”，而是围绕三条轨道逐步成长为 AI 系统的管理者和优化者。

长期目标：

1. 逐渐成为 AI Agent 工程师。
2. 从“信息中转者”成长为“业务深度专家”。
3. 成为“AI 系统的管理者和优化者”。

三条能力轨道：

- Track A：AI Agent 工程能力。用户从 AI 工具使用者，成长为能设计、实现、评估和迭代 Agent 系统的人。
- Track B：业务深度专家能力。用户从信息中转者，成长为能理解业务目标、流程、指标、瓶颈和 AI 改造机会的人。
- Track C：AI 系统管理与优化能力。用户从 AI 输出使用者，成长为能评估、归因、优化、治理和持续改进 AI 系统的人。

三条轨道不是互相独立的课程，而是围绕真实工作案例联动成长。例如同一个复杂 AI 编码会话可以同时产出：

- Agent 工程：会话流程图。
- 业务深度：业务目标卡。
- 系统管理：AI 输出验收 Rubric。

```text
                    AI 系统管理与优化者
                             ▲
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 AI Agent 工程能力      业务深度专家能力      AI 系统管理能力
```

## 3. 产品定位与非目标

产品定位：

- 个人成长执行系统。
- AI 协作复盘系统。
- 个人方法论沉淀系统。
- AI 工作流行动资产生成器。
- LLM Wiki 编译器。
- 个人成长知识底座维护器。

产品不是：

- 人格测试。
- 心理诊断工具。
- 绩效评价系统。
- 公司职级评定工具。
- 深度代码审查工具。
- 通用知识管理软件。
- 简单 RAG 系统。
- 无来源的自动笔记生成器。
- 让 LLM 直接覆盖用户知识库的自动写入工具。

第一版不追求完整评价，而追求形成一个可运行闭环：

```text
AI 协作记录 -> 证据信号 -> 成长诊断 -> 本轮任务 -> 行动资产 -> 知识沉淀
```

## 4. 核心闭环：GrowthCycle 与 LLM Wiki Loop

每次运行生成一个 GrowthCycle。它代表一轮成长行动周期，而不是一次静态分析报告。

成长闭环：

```text
Observation -> Signal -> Diagnosis -> GrowthTask -> Review
```

知识闭环：

```text
Raw Sources -> WikiUpdateProposal -> Human Review -> Wiki -> Lint
```

```text
┌──────────────────────┐
│ Observation           │
│ 对话记录 / 仓库结构    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Evidence Signal       │
│ 标准化行为信号         │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Diagnosis             │
│ 瓶颈 / 杠杆 / 缺口      │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ GrowthTask            │
│ 可执行成长任务         │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ ActionAsset           │
│ 提示 / 清单 / 模板 / 规则│
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Review & LLM Wiki     │
│ 复盘 / Wiki 更新 / 下一轮│
└──────────────────────┘
```

GrowthCycle 和 LLM Wiki Loop 互相喂养：

```text
┌──────────────────────────────┐
│ Growth Loop                  │
│ 证据 -> 诊断 -> 任务 -> 复盘   │
└──────────────┬───────────────┘
               │ 产出任务、复盘、行动资产
               ▼
┌──────────────────────────────┐
│ LLM Wiki Loop                │
│ raw -> diff -> review -> wiki │
└──────────────┬───────────────┘
               │ 产出知识、规则、模板
               ▼
┌──────────────────────────────┐
│ 下一轮 AI 协作                 │
└──────────────────────────────┘
```

GrowthCycle 示例：

```json
{
  "id": "cycle_20260509_week1",
  "theme": "从 AI 协作者走向 Agent 流程编排者",
  "cadence": "weekly",
  "constraints": {
    "weeklyTimeBudgetHours": 3,
    "currentFocus": "balanced",
    "availablePracticeContext": [
      "past_conversations",
      "confirmed_repository"
    ]
  },
  "maturityEstimateIds": [],
  "diagnosisIds": [],
  "taskIds": [],
  "actionAssetIds": [],
  "wikiUpdateProposalIds": [],
  "wikiPageIds": [],
  "reviewPlan": {
    "dueAt": "2026-05-16T20:00:00+08:00",
    "questions": [
      "本周哪些任务完成了？",
      "哪个任务摩擦最大？",
      "产出了哪些可复用规则？",
      "下周应该继续、升级还是换方向？"
    ]
  }
}
```

## 5. 用户流程

第一版用户流程：

1. 用户启动系统。
2. 系统自动发现 Codex、Claude Code、opencode 的本地对话记录。
3. 系统生成数据源清单，用户确认隐私边界。
4. 用户提供最小 Growth Constraints，例如本周可投入时间和当前关注重点。
5. 系统解析对话，生成 ConversationSession。
6. 系统本地脱敏、压缩，并抽取 EvidenceItem。
7. 系统抽取 MVP Evidence Signals。
8. 系统围绕三轨目标生成成熟度初判。
9. 系统生成 Diagnosis。
10. 系统路由到 3 个 GrowthTask。
11. 系统生成配套 ActionAsset、WikiUpdateProposal 和必要的 WikiPage 草案。
12. 系统将 LLM Wiki 更新写入 diff/，用户审核后再应用到 wiki/。
13. 系统生成 Wiki Lint Report，标记缺引用、链接错误、低置信内容和隐私风险。
14. 系统输出本轮成长任务包、报告、LLM Wiki 更新建议和隐私审计。

关键交互不是长问卷，而是少量高价值约束：

- 本周愿意投入多少小时？
- 本轮是否有重点轨道？
- 是否确认一个代码仓库作为补充分析来源？

Growth Constraints 示例：

```json
{
  "northStar": [
    "成为 AI Agent 工程师",
    "从信息中转者到业务深度专家",
    "成为 AI 系统的管理者和优化者"
  ],
  "weeklyTimeBudgetHours": 3,
  "currentFocus": "balanced | agent_engineering | business_depth | ai_system_management",
  "availableRepositoryPath": "optional"
}
```

## 6. 总体架构

平台按 5 层组织，避免把所有逻辑平铺成大量难以区分的 Agent。

```text
Data Layer
  Source Plugins
  Conversation Parser
  Repository Analyzer

Evidence Layer
  Privacy & Compression
  Evidence Extractor
  Signal Extractor

Growth Layer
  Maturity Estimator
  Diagnosis Generator
  Task Router
  Growth Execution Agent

Asset & Wiki Layer
  ActionAsset Generator
  LLM Wiki Compiler
  Wiki Diff Generator
  Wiki Lint
  Report Composer

Audit Layer
  Privacy Audit
  Evidence Trace
  Wiki Update Audit
  Output Validation
```

架构图：

```text
┌─────────────────────────────────────────┐
│ Data Layer                              │
│ Codex / Claude / opencode / Git         │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│ Evidence Layer                          │
│ 脱敏 / EvidenceItem / EvidenceSignal     │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│ Growth Layer                            │
│ 三轨成熟度 / Diagnosis / GrowthTask      │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│ Asset & Wiki Layer                      │
│ ActionAsset / WikiPage / Report          │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│ Audit Layer                             │
│ 隐私审计 / 证据追溯 / 输出校验           │
└─────────────────────────────────────────┘
```

### 6.1 Data Layer

Data Layer 负责发现、检查和解析输入来源。它不做能力判断，也不直接生成成长建议。

首批输入：

- Codex 对话记录。
- Claude Code 对话记录。
- opencode 对话记录。
- 用户确认的 Git 仓库路径。

### 6.2 Evidence Layer

Evidence Layer 负责把原始数据变成可追溯、可脱敏、可聚合的证据和信号。

职责：

- 本地清洗和脱敏。
- 对长会话进行压缩摘要。
- 提取 EvidenceItem。
- 聚合 EvidenceSignal。
- 标记敏感等级和置信度。

### 6.3 Growth Layer

Growth Layer 是系统的核心。它负责把证据信号转为成熟度初判、诊断、任务路由和本轮 GrowthCycle。

职责：

- 估计三轨成熟度。
- 识别瓶颈、杠杆点、知识缺口和风险模式。
- 根据目标轨道和时间预算选择任务。
- 生成可执行 GrowthTask。

### 6.4 Asset & Wiki Layer

Asset & Wiki Layer 负责把任务转化为长期可复用的行动资产和 LLM Wiki 更新。

职责：

- 生成 prompt、checklist、template、agent rule 和 playbook。
- 生成 WikiUpdateProposal。
- 生成 WikiPage 草案。
- 生成 Wiki diff，等待人类审核。
- 生成 Wiki lint report。
- 输出 Markdown 和 JSON 报告。
- 组织 llm-wiki/ 目录。

### 6.5 Audit Layer

Audit Layer 贯穿全流程，确保用户知道系统使用了哪些数据、跳过了哪些数据、哪些内容被脱敏、哪些内容可能外发给 LLM，以及哪些 Wiki 更新被生成、审核、应用或拒绝。

## 7. 核心数据模型

主干模型：

```text
ConversationSession
  -> RawSource
  -> EvidenceItem
  -> EvidenceSignal
  -> Diagnosis
  -> GrowthTask
  -> ActionAsset
  -> WikiUpdateProposal
  -> WikiPage
```

辅助模型：

```text
GrowthCycle
MaturityEstimate
PersonalProfile
RoleScorecard
SourceInventory
PrivacyAudit
SourceManifest
WikiLintIssue
WikiLintReport
```

主干关系：

```text
过去                     现在                     未来
│                        │                        │
▼                        ▼                        ▼
EvidenceItem ───────▶ Diagnosis ───────▶ GrowthTask
     │                      │                    │
     ▼                      ▼                    ▼
EvidenceSignal        WikiUpdateProposal   ActionAsset
                              │
                              ▼
                          WikiPage
```

### 7.1 ConversationSession

ConversationSession 是不同 AI 工具对话记录的统一模型。

```json
{
  "id": "session_id",
  "source": "codex | claude_code | opencode",
  "startedAt": "2026-05-09T10:00:00+08:00",
  "endedAt": "2026-05-09T11:00:00+08:00",
  "messages": [],
  "toolCalls": [],
  "referencedFiles": [],
  "projectPaths": [],
  "taskType": "debugging | feature | refactor | design | learning | review",
  "outcome": "completed | partial | failed | unknown"
}
```

会话解析必须保留：

- 用户请求。
- Assistant 回复摘要。
- 工具调用摘要。
- 涉及文件路径。
- 涉及项目路径。
- 任务类型。
- 错误与修复过程。
- 明确决策与结论。

### 7.2 RawSource

RawSource 是 LLM Wiki 的只读原始素材层条目。它可以是脱敏后的会话副本、仓库快照摘要、成长任务产物或 ActionAsset 快照。RawSource 一旦写入，不应被 LLM 修改；如需修正，应新增版本并通过 SourceManifest 保留来源关系。

```json
{
  "id": "raw_20260511_001",
  "type": "conversation | repository_snapshot | growth_artifact | action_asset",
  "path": "llm-wiki/raw/conversations/20260511_codex_debug_case.md",
  "origin": "codex",
  "createdAt": "2026-05-11T10:00:00+08:00",
  "hash": "sha256...",
  "sensitivity": "redacted | local_only",
  "mutable": false
}
```

### 7.3 SourceManifest

SourceManifest 记录原始素材、脱敏副本、EvidenceItem 和 LLM Wiki 页面之间的来源关系。它保证 Wiki 中的结论可以回溯到本地证据，而不是变成无来源总结。

```json
{
  "sourceId": "src_codex_20260511_001",
  "rawSourceId": "raw_20260511_001",
  "originalLocation": "local_pointer_to_codex_session",
  "ingestedAt": "2026-05-11T10:00:00+08:00",
  "sourceType": "conversation",
  "tool": "codex",
  "redactionStatus": "redacted",
  "hash": "sha256..."
}
```

### 7.4 EvidenceItem

EvidenceItem 记录“为什么这么判断”。它来自具体会话、工具调用或仓库结构，不承载复杂结论。

```json
{
  "id": "ev_20260509_001",
  "source": {
    "type": "conversation",
    "tool": "codex",
    "sessionId": "sess_abc",
    "locator": "message_12"
  },
  "observedAt": "2026-05-09T10:35:00+08:00",
  "category": "behavior",
  "signal": "requires_evidence_chain_before_fix",
  "summary": "用户要求在修改业务逻辑前先定位失败点、真实调用链和最终参数。",
  "rawReference": {
    "kind": "local_pointer",
    "value": "runs/.../source-map.json#sess_abc.message_12"
  },
  "sensitivity": "safe | redacted | local_only",
  "confidence": 0.86,
  "tags": ["debugging", "backend", "logic-analysis"]
}
```

### 7.5 EvidenceSignal

EvidenceSignal 把多个证据聚合为标准化行为信号。成熟度判断、诊断和任务路由都应基于 EvidenceSignal，而不是直接让 LLM 对原文做主观评价。

```json
{
  "id": "signal_001",
  "name": "requires_verification",
  "category": "ai_collaboration",
  "polarity": "positive",
  "description": "用户要求 AI 输出经过测试、命令执行、差异检查或其他可验证方式确认。",
  "observedInEvidenceIds": ["ev_001", "ev_009"],
  "frequency": 4,
  "recency": "recent",
  "contexts": ["debugging", "feature"],
  "confidence": 0.84,
  "supportsMaturity": [
    {
      "track": "ai_system_management",
      "level": "C1",
      "weight": 0.7
    }
  ]
}
```

信号强度计算考虑：

- frequency：出现频率。
- recency：最近是否出现。
- context_diversity：是否跨多个场景出现。
- evidence_quality：证据是否清晰、完整、可引用。
- explicitness：是用户明确要求，还是系统间接推断。

### 7.6 Diagnosis

Diagnosis 解释证据共同说明什么瓶颈、杠杆点、知识缺口或风险模式。

```json
{
  "id": "diag_001",
  "type": "bottleneck | leverage_point | knowledge_gap | risk_pattern",
  "title": "问题分析能力较强，但沉淀和复用不足",
  "targetTracks": ["agent_engineering", "ai_system_management"],
  "summary": "用户在即时 AI 协作中表现出较强证据链意识，但尚未稳定转化为可复用工作流和 Agent 规则。",
  "severity": "medium",
  "growthLeverage": "high",
  "confidence": 0.78,
  "supportingSignalIds": ["signal_001", "signal_004"],
  "supportingEvidenceIds": ["ev_001", "ev_009"],
  "counterEvidenceIds": [],
  "insufficientEvidence": [
    "缺少用户是否在真实项目中长期复用这些规则的证据"
  ],
  "recommendedFocus": "把高质量即时判断转化为行动模板和 Agent 规则"
}
```

### 7.7 MaturityEstimate

MaturityEstimate 是围绕三条成长轨道的成熟度初判。它必须区分 Observed、Inferred 和 Unknown。

```json
{
  "track": "business_depth",
  "estimatedLevel": "B1-B2",
  "confidence": 0.62,
  "status": "inferred",
  "observedSignals": ["asks_acceptance_criteria"],
  "missingSignalsForNextLevel": ["models_business_process", "links_task_to_metric"],
  "caution": "当前证据主要来自技术对话，业务场景证据不足。"
}
```

### 7.8 GrowthTask

GrowthTask 规定下一步做什么。没有完成定义的建议不能进入最终任务列表。

```json
{
  "id": "task_001",
  "cycleId": "cycle_20260509_week1",
  "title": "把一次复杂 AI 会话抽象成 Agent 流程图",
  "primaryTrack": "agent_engineering",
  "secondaryTracks": ["ai_system_management", "business_depth"],
  "maturityMove": {
    "track": "agent_engineering",
    "fromLevel": "A1",
    "toLevel": "A2"
  },
  "caseBinding": {
    "caseId": "case_001",
    "caseType": "complex_ai_coding_session"
  },
  "taskType": "case_analysis",
  "level": "weekly",
  "timeBudgetMinutes": 90,
  "whyThisTask": "这次会话包含多轮目标澄清、工具使用和验证过程，适合训练你从 AI 协作提示者升级为 Agent 流程编排者。",
  "steps": [
    "选择一次复杂 Codex、Claude Code 或 opencode 会话",
    "列出这次会话的目标、输入、上下文、工具、状态、失败点和输出",
    "标出至少 2 个人工决策点",
    "标出至少 2 个未来可自动化节点"
  ],
  "doneDefinition": [
    "产出一份 agent-flow-analysis.md",
    "至少包含目标、输入、上下文、工具、状态、失败点、输出",
    "至少引用 3 条 EvidenceItem",
    "至少沉淀 1 条可复用 Agent 规则"
  ],
  "reviewQuestions": [
    "这次任务中哪些步骤可以被 Agent 自动完成？",
    "哪些步骤必须保留人工确认？",
    "下次设计同类 Agent 时第一步应该做什么？"
  ],
  "expectedArtifacts": [
    "llm-wiki/wiki/agent-engineering/agent-flow-analyses/case-001.md",
    "llm-wiki/machine-usable/agent-rules/debugging-evidence-chain.md"
  ]
}
```

### 7.9 ActionAsset

ActionAsset 是可直接进入下一轮工作流的行动资产，帮助用户在真实任务中更容易执行成长动作。

```json
{
  "id": "asset_001",
  "type": "prompt_snippet | checklist | template | agent_rule | playbook",
  "title": "Debug 前置分析提示",
  "trigger": "before_debugging_session",
  "targetTool": "codex | claude_code | opencode | generic",
  "content": "在修改代码前，请先列出：直接失败点、真实调用链、最终查询或计算参数、最小闭环修复方案。",
  "usageInstruction": "下次开始 Debug 类 AI 会话时，将这段提示放在用户请求前。",
  "sourceDiagnosisIds": ["diag_001"],
  "sourceTaskIds": ["task_001"],
  "sourceEvidenceIds": ["ev_001", "ev_009"],
  "reviewMetric": "下一轮 Debug 会话是否至少覆盖提示中的 3 个字段",
  "exportTargets": [
    {
      "type": "markdown",
      "path": "llm-wiki/machine-usable/prompts/pre-debugging-session.md"
    }
  ]
}
```

### 7.10 WikiPage

WikiPage 是 LLM Wiki 的长期知识单元。它可以承载概念、方法论、业务模型、决策记录、行动资产、成长任务产物和评估 Rubric。

```json
{
  "id": "wiki_evidence_chain_analysis",
  "title": "先证据链后修改逻辑",
  "path": "llm-wiki/wiki/concepts/evidence-chain-analysis.md",
  "type": "concept | method | playbook | business_model | rubric | task_artifact | decision | action_asset",
  "status": "draft | review | ready | stale | deprecated",
  "sourceEvidenceIds": ["ev_001", "ev_009"],
  "sourceRawIds": ["raw_001"],
  "linkedPages": ["ai-output-verification"],
  "tracks": ["agent_engineering", "ai_system_management"],
  "confidence": 0.88,
  "lastReviewedAt": "2026-05-11T10:00:00+08:00"
}
```

### 7.11 WikiUpdateProposal

WikiUpdateProposal 是 LLM 生成的 Wiki 更新建议。系统默认不直接覆盖 wiki/，而是生成 diff，等待人类审核。

```json
{
  "id": "wiki_update_001",
  "type": "create | update | merge | deprecate",
  "targetPath": "llm-wiki/wiki/concepts/evidence-chain-analysis.md",
  "reason": "新增证据表明该方法已在多次 Debug 会话中复用。",
  "sourceEvidenceIds": ["ev_001", "ev_009"],
  "sourceRawIds": ["raw_001"],
  "diffPath": "llm-wiki/diff/proposed-updates/20260511_evidence-chain-analysis_diff.md",
  "risk": "low | medium | high",
  "requiresHumanReview": true,
  "status": "proposed | approved | rejected | applied"
}
```

### 7.12 WikiLintIssue

WikiLintIssue 记录 LLM Wiki 健康检查发现的问题。MVP 至少需要检查缺引用、坏链接、非法 frontmatter、隐私风险和重复页面。

```json
{
  "id": "lint_001",
  "severity": "info | warning | error",
  "pagePath": "llm-wiki/wiki/concepts/evidence-chain-analysis.md",
  "type": "missing_source | broken_link | stale_claim | duplicate_page | privacy_risk | invalid_frontmatter",
  "message": "页面包含关键结论，但未引用 EvidenceItem。",
  "suggestedFix": "补充 sourceEvidenceIds 或将结论移入待补充/疑问。"
}
```

### 7.13 KnowledgeCard 兼容关系

KnowledgeCard 可以保留为 WikiPage 的轻量内容类型，用于表达单个知识点、方法、经验或缺口。但它不再是长期沉淀的最终形态。MVP 可以继续生成 KnowledgeCard 草案，但最终应通过 WikiUpdateProposal 写入 llm-wiki/wiki/。

```json
{
  "id": "kc_001",
  "mapsToWikiPageId": "wiki_evidence_chain_analysis",
  "type": "method",
  "title": "先证据链后修改逻辑",
  "sourceEvidenceIds": ["ev_001"],
  "status": "draft"
}
```

## 8. Evidence Signal Taxonomy

Evidence Signal Taxonomy 是系统的观测语言。它把对话和仓库中的模糊行为，转成可累计、可比较、可路由到成长任务的标准信号。

MVP 先支持 20 个高价值信号。

### 8.1 AI 协作信号

- provides_context：提供背景、项目状态、约束、已有设计。
- sets_constraints：明确要求 AI 遵守编码规范、隐私规则、文件编码、测试边界。
- asks_for_plan_before_action：要求先分析或计划，再实现。
- requires_verification：要求运行测试、检查输出或验证结果。
- corrects_ai_assumption：指出 AI 的错误假设，要求回到证据。
- externalizes_ai_rules：把协作经验沉淀为 AGENTS.md、规则、模板或提示。

### 8.2 Agent 工程信号

- decomposes_task_into_pipeline：把任务拆成多个阶段或模块。
- defines_stage_io：说明每个阶段的输入、输出和边界。
- identifies_tool_boundaries：识别哪些步骤需要工具、工具能做什么、不能做什么。
- plans_error_recovery：考虑失败重试、降级和异常处理。

### 8.3 业务深度信号

- asks_business_goal：追问需求背后的业务目标。
- asks_acceptance_criteria：要求验收标准，不只接收需求描述。
- models_business_process：描述或绘制业务流程、角色、输入输出、决策点。
- links_task_to_metric：把需求或技术任务连接到业务指标。

### 8.4 系统管理信号

- identifies_ai_failure_reason：指出 AI 失败原因。
- classifies_failure_type：把失败归类为上下文不足、目标不清、工具误用、验证缺失等。
- updates_rule_after_failure：失败后更新规则、提示、检查清单。
- defines_permission_boundary：定义 AI 能做和不能做的事。

### 8.5 知识沉淀信号

- creates_checklist：把经验整理成检查清单。
- creates_template：产出复盘模板、设计模板、分析模板。

### 8.6 风险与反模式信号

风险信号不是简单扣分项，而是任务路由的重要依据。

- accepts_requirement_as_given：直接接受需求，没有澄清目标或边界。
- solution_before_problem：先想方案，未确认问题。
- missing_verification：完成任务后缺少验证。
- over_relies_on_ai_output：接受 AI 输出但缺少独立判断或测试。
- adds_fallback_without_evidence：在没有证明依赖缺失时引入 fallback。
- treats_guard_as_business_dependency：把 guard clause 误当核心业务依赖。
- lacks_business_metric：无法说明技术任务影响哪个业务指标。
- one_off_fix_without_pattern：修完问题但没有沉淀预防规则。
- unclear_done_definition：任务没有完成定义。
- over_scoped_plan：计划过大，超出时间或上下文约束。

### 8.7 信号到诊断和任务的路由示例

组合 1：强 AI 协作，弱 Agent 抽象。

```text
positive:
provides_context
sets_constraints
requires_verification

missing:
decomposes_task_into_pipeline
defines_stage_io
```

诊断：

```text
已具备高质量 AI 协作能力，但需要从提示层升级到 Agent 流程设计。
```

推荐任务：

```text
把一次复杂 AI 会话抽象成 Agent 流程图。
```

组合 2：强技术分析，弱业务建模。

```text
positive:
requires_verification
identifies_tool_boundaries
plans_error_recovery

missing:
asks_business_goal
links_task_to_metric
models_business_process
```

诊断：

```text
技术问题分析较强，但需要把任务连接到业务目标和流程。
```

推荐任务：

```text
为一个技术任务补业务目标、指标和流程影响卡。
```

组合 3：能验证 AI 输出，但缺少优化闭环。

```text
positive:
requires_verification

missing:
classifies_failure_type
compares_before_after
creates_evaluation_sample
```

诊断：

```text
已具备 AI 输出验收意识，但还没有形成稳定优化机制。
```

推荐任务：

```text
复盘 3 到 5 次 AI 输出失败，建立 failure taxonomy。
```

## 9. 三轨成熟度模型

成熟度不是看用户知道多少名词，而是看用户在真实任务中是否稳定表现出某种行为。

### 9.1 Track A：AI Agent 工程能力

```text
A0 AI 工具使用者
A1 AI 协作提示者
A2 Agent 流程编排者
A3 Agent 工程实现者
A4 Agent 系统设计者
A5 多 Agent / 组织级 AI 系统架构者
```

A1 到 A2 的关键跃迁：

```text
从“把提示写好”
到“把任务流程设计好”
```

A2 到 A3 的关键跃迁：

```text
从“能设计流程”
到“能实现、测试和维护 Agent”
```

### 9.2 Track B：业务深度专家能力

```text
B0 信息接收者
B1 信息中转者
B2 需求澄清者
B3 业务流程建模者
B4 业务指标驱动者
B5 AI 业务转型设计者
```

B1 到 B2 的关键跃迁：

```text
从“翻译需求”
到“澄清需求”
```

B2 到 B3 的关键跃迁：

```text
从“澄清单点需求”
到“建模业务流程”
```

### 9.3 Track C：AI 系统管理与优化能力

```text
C0 AI 输出使用者
C1 AI 输出验证者
C2 AI 失败归因者
C3 AI 工作流优化者
C4 AI 系统治理者
C5 AI 组织能力建设者
```

C1 到 C2 的关键跃迁：

```text
从“检查结果”
到“分析为什么失败”
```

C2 到 C3 的关键跃迁：

```text
从“解释失败”
到“改进流程并验证效果”
```

### 9.4 成熟度输出规则

成熟度输出必须标注证据状态：

- Observed：有直接证据。
- Inferred：合理推断但证据间接。
- Unknown：证据不足。

成熟度判断的主要用途不是展示分数，而是选择下一轮任务。系统应避免直接输出“你是 A2”这类强定级，更合适的表达是：

```text
从可见证据看，你表现出 A1-A2 的行为信号。
缺少足够证据判断 B3 以上能力。
```

## 10. 任务路由与成长任务包

GrowthTask 是系统的核心输出。任务路由要根据 North Star、成熟度初判、Diagnosis、时间预算和可用案例共同决定。

任务生成流程：

```text
EvidenceItem
  -> EvidenceSignal
  -> MaturityEstimate
  -> Diagnosis
  -> Candidate Tasks
  -> Constraint Fit
  -> Top GrowthTasks
```

MVP 内置 6 个任务模板：

### 10.1 A 轨：AI Agent 工程

A-T1：AI 会话流程抽象。

- 输入：一次复杂 Codex、Claude Code 或 opencode 会话。
- 产物：agent-flow-analysis.md。
- 目标：A1 -> A2。

A-T2：Agent Spec 草案。

- 输入：一个真实任务。
- 产物：agent-spec.md。
- 目标：A2 -> A3。

### 10.2 B 轨：业务深度

B-T1：业务目标卡。

- 输入：一个真实需求或技术任务。
- 产物：business-goal-card.md。
- 目标：B1 -> B2。

B-T2：业务流程卡。

- 输入：一个真实流程。
- 产物：business-process-card.md。
- 目标：B2 -> B3。

### 10.3 C 轨：系统管理

C-T1：AI 输出验收 Rubric。

- 输入：一次 AI 输出。
- 产物：ai-output-rubric.md。
- 目标：C1 -> C2。

C-T2：AI 失败归因表。

- 输入：3 到 5 次 AI 输出失败或反复修改案例。
- 产物：failure-taxonomy.md。
- 目标：C2 -> C3。

### 10.4 默认第一轮任务组合

默认第一轮选择同一个复杂 AI 会话，生成三轨联动任务：

```text
同一个复杂 AI 会话
  ├── A-T1：抽象 Agent 流程
  ├── B-T1：补业务目标卡
  └── C-T1：定义 AI 输出验收 Rubric
```

这种组合执行摩擦低，因为它围绕一个真实案例展开，同时服务三条成长轨道。

### 10.5 任务完成定义要求

每个 GrowthTask 必须包含：

- 目标轨道。
- 成熟度跃迁。
- 案例绑定。
- 时间预算。
- 执行步骤。
- 完成定义。
- 复盘问题。
- 预期产物。
- 配套 ActionAsset。

任务建议如果无法落到动作对象、完成标准、时间范围和复盘指标，则不能进入最终报告。

## 11. ActionAsset 与 LLM Wiki

LLM Wiki 是 Personal Growth Agent 的长期记忆层。它以 Markdown 为载体，采用 raw -> diff -> review -> wiki 的流程，把 AI 协作记录、仓库结构、成长任务产物和复盘结果编译为可链接、可溯源、可持续维护的知识资产。

### 11.1 ActionAsset 类型

ActionAsset 是可直接进入下一轮工作流的行动资产。它既是 GrowthCycle 的输出，也是 LLM Wiki 中 machine-usable/ 下的可执行页面。

- prompt_snippet：下次 AI 会话前使用。
- checklist：执行或验收时使用。
- template：写复盘、ADR、方案时使用。
- agent_rule：可放进 AGENTS.md、CLAUDE.md 或 opencode 规则。
- playbook：多步骤操作手册。

ActionAsset 生成原则：

- 必须有触发场景。
- 必须有使用说明。
- 必须引用来源证据或诊断。
- 不得包含未脱敏的项目、公司、客户或代码细节。
- 应尽量能复制到下一轮 Codex、Claude Code 或 opencode 协作中。

### 11.2 LLM Wiki 三层结构

LLM Wiki 由三层组成：

- Raw Sources 原始素材层：只读、不改、可溯源。
- Wiki 结构化知识层：由 LLM 编译、链接、更新，由人类审核。
- Schema 规则定义层：通过 AGENTS.md、SCHEMA.md、页面模板和 lint 规则约束 LLM。

```text
┌────────────────────────────┐
│ Raw Sources 原始素材层       │
│ 只读、不改、可溯源            │
└──────────────┬─────────────┘
               ▼
┌────────────────────────────┐
│ Wiki 结构化知识层            │
│ LLM 整理、链接、更新          │
└──────────────┬─────────────┘
               ▼
┌────────────────────────────┐
│ Schema 规则定义层            │
│ AGENTS.md / 模板 / lint 规则 │
└────────────────────────────┘
```

### 11.3 LLM Wiki 目录

```text
llm-wiki/
  AGENTS.md
  SCHEMA.md
  README.md
  overview.md
  links.md

  raw/
    conversations/
    repositories/
    growth-artifacts/
    action-assets/

  wiki/
    north-star/
      ai-agent-system-leader.md
      growth-map.md

    agent-engineering/
      agent-flow-analyses/
      agent-specs/
      tool-capability-maps/
      memory-design-notes/

    business-depth/
      business-goal-cards/
      business-process-cards/
      metric-dictionary.md
      ai-opportunity-map.md

    ai-system-management/
      evaluation-rubrics/
      failure-taxonomy.md
      optimization-log.md
      governance-rules.md

    concepts/
    decisions/

  machine-usable/
    prompts/
    checklists/
    agent-rules/
    templates/
    playbooks/

  diff/
    proposed-updates/

  report/
    lint-reports/

  data/
    source-manifest.json
    evidence-index.json
    wiki-page-index.json
```

### 11.4 WikiPage 页面类型

LLM Wiki 需要支持以下页面类型：

- NorthStarPage：长期目标和成长地图。
- AgentEngineeringPage：Agent 流程、工具边界、状态、记忆、失败处理。
- BusinessDepthPage：业务目标、流程、指标、瓶颈、AI 改造机会。
- AISystemManagementPage：评估 Rubric、失败分类、优化日志、治理规则。
- ConceptPage：跨轨道核心概念，例如证据链分析、Agent 流程编排、业务流程建模。
- DecisionPage：关键设计决策和成长决策。
- ActionAssetPage：prompt、checklist、template、agent rule、playbook。
- GrowthArtifactPage：成长任务产物，例如 Agent 流程图、业务目标卡、失败归因表。

### 11.5 页面模板与 frontmatter

所有 WikiPage 必须有统一 frontmatter，便于 LLM 维护、lint 检查和证据追溯。

```yaml
---
title: 先证据链后修改逻辑
type: method
status: draft
owners:
  - user
source_count: 3
source_evidence_ids:
  - ev_001
  - ev_009
source_paths:
  - ../raw/conversations/20260511_codex_debug_case.md
last_reviewed: 2026-05-11
sensitivity: internal
confidence: 0.88
tracks:
  - ai_system_management
  - agent_engineering
related:
  - "[[AI 输出验证]]"
  - "[[Debug 前置分析提示]]"
---
```

页面状态：

- draft：LLM 初稿。
- review：等待人类审核。
- ready：可稳定复用。
- stale：可能过时。
- deprecated：已废弃但保留历史。

### 11.6 Diff-first 更新机制

LLM Wiki Compiler 默认不能直接覆盖 wiki/。它必须生成 WikiUpdateProposal 和 diff，等待人类审核后再应用。

硬规则：

- raw/ 只读，LLM 禁止修改。
- wiki/ 不直接覆盖，默认生成 diff。
- 重要页面必须人工审核后应用。
- 关键结论必须引用 EvidenceItem 或 RawSource。
- 不确定内容写入“待补充/疑问”。
- 禁止删除页面，只能标记 deprecated。
- 更新 Wiki 后必须同步更新 overview.md 和 links.md。

### 11.7 Wiki Lint 与健康检查

MVP 至少需要生成 Wiki Lint Report，检查：

- 关键结论是否有来源。
- 页面是否缺少 frontmatter。
- 是否存在未解决的“待补充/疑问”。
- 是否存在无效链接。
- 是否存在重复页面或明显冲突页面。
- ActionAsset 是否包含敏感信息。

### 11.8 知识沉淀范围

- Agent 工程知识：Agent 流程、工具边界、状态、记忆、失败处理。
- 业务深度知识：业务目标、流程、指标、瓶颈、AI 改造机会。
- AI 系统管理知识：评估 Rubric、失败分类、优化日志、治理规则。
- 个人方法论：适合用户自己的工作流、复盘模板、代码审查清单。
- 行动资产：可直接用于下一轮 AI 协作的提示、清单、模板和规则。

## 12. 数据源插件与会话解析

首批数据源：

- Codex。
- Claude Code。
- opencode。
- Git 仓库结构。

每个数据源插件实现统一接口：

- discover：发现默认记录路径和候选文件。
- inspect：生成数据清单，不读取或暴露完整原文。
- parse：解析为 ConversationSession。
- validate：判断格式版本、字段完整性和异常文件。
- summarizeFailure：输出失败原因和可操作提示。

Codex、Claude Code 和 opencode 的路径规则可能随版本变化，插件必须允许路径规则配置化，并在无法识别时输出清晰错误。

数据源服务于证据信号抽取，不是为了完整读取所有历史。系统应该优先处理最近、高信号密度、可解析且隐私风险可控的会话。

## 13. 隐私、脱敏与审计

平台默认按“本地优先、最小外发、可审计”设计。

核心规则：

- 原始对话不直接发送给 LLM。
- 代码内容默认不外发。
- 敏感信息先本地脱敏，再进入摘要和证据包。
- 所有外发内容生成审计记录，用户可查看。
- 所有结论保留证据索引，但证据索引默认指向本地，不暴露原文。
- 用户可选择禁用外部 LLM，退化成本地规则报告。
- 仓库扫描必须二次确认路径，不自动扫全盘项目目录。
- ActionAsset 不得泄露原始项目、公司、客户或代码细节。
- raw/ 默认只存脱敏副本或本地指针，不强制复制原始敏感内容。
- WikiPage 不得包含未脱敏的公司、客户、项目代号、密钥或业务代码。
- WikiUpdateProposal 必须记录来源、风险等级和是否需要人工审核。

敏感信息类型：

- API Key、Token、Secret、Cookie、私钥。
- 邮箱、手机号、身份证、住址。
- 内网域名、数据库连接串、服务器地址。
- 公司名、客户名、项目代号。
- 代码中的业务规则和专有实现。
- 对话中的个人隐私、财务、健康、家庭信息。

脱敏分三层：

1. 规则脱敏：用正则和文件类型规则处理 key、token、邮箱、URL、连接串等明确敏感模式。
2. 语义脱敏：识别公司、客户、项目等上下文敏感内容，并替换为占位符。
3. 外发前审查：生成 OutboundPayloadPreview，记录外发目的、证据数量、脱敏数量和 payload 摘要。

OutboundPayloadPreview 示例：

```json
{
  "target": "llm_provider",
  "purpose": "diagnosis_and_task_generation",
  "includedEvidenceCount": 128,
  "redactedItemsCount": 43,
  "containsRawCode": false,
  "containsOriginalMessages": false,
  "payloadDigest": "sha256..."
}
```

隐私审计需要记录：

- 使用了哪些数据源。
- 跳过了哪些文件。
- 脱敏了哪些类型信息。
- 哪些内容进入 LLM payload。
- 哪些内容被标记为 local_only。
- 生成了哪些可外部复用的 ActionAsset。
- 哪些 RawSource 被摄入到 llm-wiki/raw/。
- 哪些 WikiUpdateProposal 被生成、应用或拒绝。
- 哪些 WikiPage 被标记为 draft、review、ready、stale 或 deprecated。
- Wiki Lint 发现了哪些问题。

## 14. 程序员仓库补充分析

仓库分析的目的不是做深度代码审查，而是补充三类信号：

- 工程化信号。
- Agent 工程实践信号。
- ActionAsset 项目适配线索。

当系统从对话中识别到程序员或 AI Agent 工程方向信号时，Repository Analyzer 进入待确认状态。

触发流程：

1. 系统说明检测到程序员或 AI Agent 工程相关信号。
2. 系统请求用户确认一个或多个仓库路径。
3. 用户确认后，系统只扫描指定路径。
4. 系统生成 Repository Evidence Pack。
5. Evidence Layer 将其转换为仓库工程化信号。
6. Growth Layer 使用这些信号补充任务路由和 ActionAsset 生成。

第一版分析：

- Git 提交时间、频率和提交信息特征。
- 文件类型和语言分布。
- 顶层目录结构。
- 测试、文档、CI、脚本、配置存在情况。
- 是否存在 AGENTS.md、CLAUDE.md、规则文件或模板。

第一版不分析：

- 业务代码正确性。
- 完整架构质量。
- 安全漏洞。
- 性能瓶颈。
- 代码风格细节。
- 团队贡献归因。

仓库工程化信号示例：

- has_tests：存在测试目录或测试文件。
- has_ci：存在 CI 配置。
- has_docs：存在 README、docs 或设计文档。
- has_scripts：存在自动化脚本。
- structured_modules：目录结构有明显模块边界。
- has_agent_rules：存在 AGENTS.md、CLAUDE.md 或类似 Agent 规则文件。

这些信号只作为辅助，不单独推断能力。例如没有测试文件不一定说明测试意识差，可能只是仓库类型不同。

## 15. 报告输出结构

报告首页必须是任务面板。评分和画像是附录，不是主输出。

建议结构：

1. 本轮成长任务包。
2. 本周只做这 3 件事。
3. 为什么是这 3 件事。
4. 三轨成熟度初判。
5. 关键诊断与证据信号。
6. 配套 ActionAssets。
7. LLM Wiki 更新建议。
8. Wiki Lint 摘要。
9. 数据来源与隐私审计。
10. 角色画像与评分附录。

报告首页示例：

```text
# 本轮成长任务包

## 本周只做这 3 件事

1. 把一次复杂 AI 会话抽象成 Agent 流程图
   目标轨道：AI Agent 工程能力
   时间预算：90 分钟
   产物：agent-flow-analysis.md

2. 为该会话补业务目标卡
   目标轨道：业务深度专家能力
   时间预算：45 分钟
   产物：business-goal-card.md

3. 为该会话定义 AI 输出验收 Rubric
   目标轨道：AI 系统管理与优化能力
   时间预算：45 分钟
   产物：ai-output-rubric.md
```

## 16. 错误处理与降级策略

关键错误不直接中断，而是降级处理。

- 找不到某个工具记录：继续分析其他来源，并在报告中说明缺失。
- 文件格式不兼容：记录失败文件、跳过该文件、输出解析失败原因。
- 对话过长：本地分块摘要，再聚合。
- 敏感内容无法确认：标记为 local_only，不外发。
- LLM 调用失败：保留证据包，输出本地规则版任务包。
- 无法判定成熟度：输出 Unknown，不生成强结论。
- 无法绑定真实案例：生成模板型任务，并标记低个性化。
- 时间预算过低：只生成 Micro Action。
- 缺少业务证据：B 轨生成业务信息补采任务，不强行判断业务深度。
- 程序员仓库路径未确认：跳过仓库分析，不影响对话分析。
- 仓库过大：只分析 Git 元数据、顶层结构和抽样文件类型统计。

报告里必须明确区分：

- 能力不足。
- 证据不足。
- 数据源缺失。
- 分析置信度较低。
- 任务个性化程度不足。

## 17. MVP 范围与验收标准

MVP 定义：

```text
从本地 AI 协作记录中抽取成长证据信号，围绕“AI Agent 工程能力、业务深度专家能力、AI 系统管理与优化能力”生成一轮可执行成长任务包，并输出可复用的提示、清单、模板、WikiUpdateProposal 和 WikiPage 草案。
```

更完整地说，MVP 需要跑通一轮 GrowthCycle，并生成可审核的 LLM Wiki 更新建议，而不是直接把知识写死到最终页面。

MVP 必须包含：

- 自动扫描 Codex、Claude Code、opencode 默认记录路径。
- 生成数据源清单。
- 解析为 ConversationSession。
- 本地脱敏和压缩。
- EvidenceItem 抽取。
- MVP 20 个 Evidence Signals。
- 三轨 North Star。
- Growth Constraints。
- 三轨成熟度初判。
- Diagnosis 生成。
- 至少 1 个 GrowthCycle。
- 3 个 GrowthTask。
- 每个任务有 Done Definition。
- 至少 3 个 ActionAsset。
- llm-wiki/ 持久目录。
- raw/ 只读来源层。
- wiki/ 结构化知识层。
- AGENTS.md 或 SCHEMA.md 操作规则。
- WikiPage 输出。
- WikiUpdateProposal 输出。
- diff/ proposed updates。
- Wiki Lint Report。
- KnowledgeCard 草案输出，作为 WikiPage 兼容类型。
- 三轨 LLM Wiki 目录。
- Markdown 和 JSON 输出。
- 隐私审计文件。

MVP 不包含：

- Web UI。
- 趋势图。
- 精确职级评分。
- 完整角色体系。
- 自动写入 Agent 配置。
- 深度代码审查。
- 多仓库批量分析。
- 业务系统数据接入。
- 自动应用 diff。
- Obsidian 插件集成。
- qmd 搜索。
- GraphRAG。
- 团队协作权限。
- 微调数据集生成。

验收标准：

```text
给定一组脱敏 AI 对话样本，系统能够：
1. 发现至少一个 AI 对话数据源。
2. 解析 ConversationSession。
3. 抽取 EvidenceItem。
4. 标注 MVP 信号。
5. 输出三轨成熟度初判。
6. 生成 GrowthCycle。
7. 生成 3 个可执行 GrowthTask。
8. 每个任务都有步骤、完成定义、复盘问题和预期产物。
9. 生成 prompt、checklist、template 三类 ActionAsset。
10. 输出 privacy-audit.json。
11. 报告首页优先展示任务包。
12. 生成 llm-wiki/ 基础结构。
13. 至少生成 1 个 WikiUpdateProposal。
14. WikiUpdateProposal 必须引用 EvidenceItem 或 RawSource。
15. 生成 Wiki Lint Report。
16. raw/ 下内容不被修改。
17. WikiPage frontmatter 符合模板。
```

## 18. 运行产物结构

系统需要区分一次运行快照和长期知识资产：

- runs/ 是一次运行快照。
- llm-wiki/ 是长期资产。

每次运行生成一个独立 runs/ 目录：

```text
runs/
  2026-05-11-103000/
    source-inventory.json
    privacy-audit.json

    evidence/
      evidence-items.json
      signals.json
      maturity-estimate.json
      diagnoses.json

    growth-cycle/
      plan.md
      tasks.json
      review-template.md

    wiki-update-proposals/
      proposed-updates.json
      wiki-lint-report.md

    report.md
    report.json
    errors.log
```

长期 LLM Wiki 目录：

```text
llm-wiki/
  AGENTS.md
  SCHEMA.md
  README.md
  overview.md
  links.md

  raw/
    conversations/
    repositories/
    growth-artifacts/
    action-assets/

  wiki/
    north-star/
    agent-engineering/
    business-depth/
    ai-system-management/
    concepts/
    decisions/

  machine-usable/
    prompts/
    checklists/
    agent-rules/
    templates/
    playbooks/

  diff/
    proposed-updates/

  report/
    lint-reports/

  data/
    source-manifest.json
    evidence-index.json
    wiki-page-index.json
```

运行产物需要支持用户回看：

- 用了哪些数据。
- 哪些数据没有读成功。
- 哪些内容被脱敏。
- 哪些内容被发送给 LLM。
- 哪些证据支撑了哪些结论。
- 哪些任务来自哪些诊断。
- 哪些 ActionAsset 可以用于下一轮 AI 协作。
- 哪些 WikiUpdateProposal 等待审核。
- 哪些 WikiPage 处于 draft、review、ready、stale 或 deprecated。

## 19. 测试策略

测试类型：

1. 数据源插件测试：验证 Codex、Claude Code、opencode 不同记录格式能否被识别、解析和跳过异常文件。
2. 脱敏测试：构造包含 key、邮箱、URL、连接串、公司名、代码片段的样本，确认外发 payload 中不会出现原文。
3. EvidenceSignal 抽取测试：输入典型会话片段，验证是否能识别 MVP 20 个信号。
4. 成熟度判定测试：给定信号组合，验证三轨成熟度输出是否标注 Observed、Inferred 或 Unknown。
5. 任务路由测试：给定诊断和约束，验证系统是否路由到预期任务模板。
6. GrowthTask 可执行性测试：每个任务必须有时间预算、步骤、完成定义、复盘问题和证据引用。
7. ActionAsset 安全测试：不得包含未脱敏敏感信息，必须有明确触发场景和使用方式。
8. LLM Wiki 目录结构测试：确认 raw、wiki、machine-usable、diff、report、data 存在。
9. RawSource 不可变测试：确认系统不会修改 raw/ 中已有内容。
10. WikiPage frontmatter 测试：确认所有页面有 title、type、status、source_count、sensitivity、confidence。
11. WikiUpdateProposal 测试：确认 diff 有目标路径、来源证据、风险等级、人类审核标记。
12. Wiki Lint 测试：检查缺引用、坏链接、重复页、隐私风险、非法 frontmatter。
13. 知识卡片兼容测试：验证 KnowledgeCard 草案能映射到 WikiPage 或 WikiUpdateProposal。
14. 端到端快照测试：用一组脱敏样本对话生成完整报告，固定输出结构，不固定 LLM 文案。

重点测试规则：

- 任务建议如果没有 Done Definition，应判定为无效输出。
- 成熟度判断如果没有足够证据，应输出 Unknown，而不是强行定级。
- ActionAsset 如果包含原始项目名、客户名、密钥或代码细节，应判定为隐私失败。
- WikiPage 如果包含未脱敏敏感信息，应判定为隐私失败。
- WikiUpdateProposal 如果没有 EvidenceItem 或 RawSource 引用，应判定为无效输出。
- raw/ 如果被覆盖或修改，应判定为严重错误。
- 报告首页如果没有优先展示 GrowthTask，应判定为产品目标偏移。

## 20. 后续演进

后续可以逐步扩展：

- 从离线报告到在线工作流介入。
- 自动将 ActionAsset 应用到 AGENTS.md、CLAUDE.md、opencode 配置。
- 周期复盘和任务完成反馈。
- AI 协作成熟度趋势。
- 业务领域知识图谱。
- Agent 系统评估样本库。
- Obsidian Vault 兼容。
- qmd 或 ripgrep 轻量搜索。
- Wiki 查询命令。
- Wiki 回写闭环。
- 自动生成 diff 并发起审核。
- GraphRAG 强化关系检索。
- 团队版 LLM Wiki。
- Wiki 内容生成微调数据集。
- 本地向量检索。
- Web UI 和可视化成长面板。
- 更多数据源，例如 GitHub、Jira、飞书、Slack。
- 本地模型模式，降低外部 LLM 依赖。

## 21. 核心验收问题

设计与后续实现需要能回答：

- 读取哪些数据，不读取哪些数据。
- 哪些内容留在本地，哪些内容可能发给 LLM。
- 每个层级的职责、输入和输出是什么。
- EvidenceItem 和 EvidenceSignal 如何支撑诊断。
- 三轨成熟度如何避免胡乱推断。
- GrowthTask 如何做到可完成、可验证、可复盘。
- ActionAsset 如何进入下一轮真实工作流。
- 程序员仓库分析如何触发、分析到什么程度。
- 如何把 AI 协作记录和项目经验沉淀成 LLM Wiki。
- 如何保证 raw/ 只读、Wiki 更新走 diff-first 审核。
- 如何通过 Wiki Lint 防止错误知识固化。
- 如何区分能力不足、证据不足和数据源缺失。
- MVP 做什么，不做什么。
