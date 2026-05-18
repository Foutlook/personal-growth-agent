## Context

当前项目尚处于设计与 OpenSpec 建模阶段。已有设计文档定义了 Personal Growth Agent 的目标：基于 Codex、Claude Code、opencode 对话记录和可选仓库结构，抽取成长证据，生成一轮可执行 GrowthCycle，并将长期知识沉淀到可审核的 LLM Wiki。

本 change 覆盖多个横向能力：本地数据发现、会话解析、证据与信号抽取、三轨成熟度判断、成长任务生成、行动资产输出、LLM Wiki 维护、隐私审计和仓库补充分析。因此实现应采用分层管线，而不是单个大提示词或单个“大 Agent”。

关键约束：

- 原始对话、代码和敏感内容默认留在本地。
- 任何外发给 LLM 的内容必须先脱敏、压缩和审计。
- 成长结论必须可追溯到 EvidenceItem 或 RawSource。
- LLM Wiki 更新必须走 diff-first，人类审核前不能覆盖 wiki/。
- MVP 聚焦一次 GrowthCycle，不做 Web UI、趋势图、GraphRAG、自动应用 diff 或深度代码审查。

## Goals / Non-Goals

**Goals:**

- 建立本地优先的数据摄入与证据抽取管线。
- 将 Codex、Claude Code、opencode 记录统一解析为 ConversationSession。
- 生成 EvidenceItem、EvidenceSignal、Diagnosis、MaturityEstimate、GrowthTask、ActionAsset、WikiUpdateProposal 和隐私审计产物。
- 维护长期 `llm-wiki/` 目录，并区分只读 raw sources、结构化 wiki pages、machine-usable action assets、diff proposals 和 lint reports。
- 输出一次运行快照到 `runs/<timestamp>/`，同时让长期知识资产沉淀到 `llm-wiki/`。
- 为可选仓库路径提取工程化和 Agent 工作流信号，但不进行深度代码审查。

**Non-Goals:**

- 不实现 Web UI 或可视化仪表盘。
- 不实现团队协作权限、GraphRAG、向量库或微调数据集生成。
- 不自动写入用户项目的 AGENTS.md、CLAUDE.md 或 opencode 配置。
- 不自动应用 Wiki diff。
- 不评价业务代码正确性、安全漏洞、性能瓶颈或团队贡献归因。
- 不输出强职级定级作为核心结果。

## Decisions

### Decision 1: Use a layered pipeline instead of a monolithic Agent

The implementation SHALL use five conceptual layers:

```text
Data Layer -> Evidence Layer -> Growth Layer -> Asset & Wiki Layer -> Audit Layer
```

Rationale:

- Data parsing, evidence extraction, task routing, Wiki maintenance, and privacy audit have different failure modes.
- A layered pipeline makes intermediate outputs inspectable and testable.
- The system can later replace individual stages with LLM, local rules, or local models without rewriting the entire flow.

Alternatives considered:

- Single LLM prompt over all source data: simpler initially, but weak on privacy, traceability, testing, and deterministic validation.
- Fully plugin-based multi-Agent runtime from day one: extensible, but too heavy for MVP.

### Decision 2: Treat EvidenceItem and EvidenceSignal as the stable analysis boundary

Raw source content SHALL be transformed into EvidenceItem and EvidenceSignal before growth diagnosis or task generation.

Rationale:

- EvidenceItem gives traceability and sensitivity metadata.
- EvidenceSignal normalizes repeated behavior into a controlled vocabulary.
- Diagnosis and task routing can distinguish evidence absence from negative evidence.

Alternatives considered:

- Let the LLM infer directly from raw sessions: faster but produces opaque conclusions.
- Use only handcrafted rules: safer but less expressive for nuanced conversations.

### Decision 3: Make GrowthCycle the primary product output

The report SHALL prioritize the current GrowthCycle and its executable tasks over role scorecards.

Rationale:

- The product goal is growth executability, not personality assessment or performance scoring.
- A task package with done definitions and review questions is easier to act on than abstract advice.
- Three-track maturity estimates are useful only insofar as they route the next task.

Alternatives considered:

- Score-first report: easier to market, but weaker at driving behavior change.
- Full dashboard-first approach: useful later, but unnecessary for MVP.

### Decision 4: Model LLM Wiki as a persistent long-term memory layer

The system SHALL maintain `llm-wiki/` separately from per-run outputs.

Rationale:

- `runs/<timestamp>/` represents an immutable execution snapshot.
- `llm-wiki/` is a long-lived knowledge asset that should evolve across runs.
- Separating them prevents duplicated Wiki copies and makes review, lint, and versioning clearer.

The LLM Wiki layout SHALL include:

```text
llm-wiki/
  AGENTS.md
  SCHEMA.md
  raw/
  wiki/
  machine-usable/
  diff/
  report/
  data/
```

Alternatives considered:

- Store knowledge under each run: simple but prevents cumulative learning.
- Store only JSON data and generate Markdown on demand: easier for machines, weaker for human review and Obsidian-style workflows.

### Decision 5: Use diff-first Wiki updates

The system MUST generate WikiUpdateProposal and diff files before changing existing wiki/ pages.

Rationale:

- LLM-generated summaries can be wrong, overconfident, or privacy unsafe.
- Human review is necessary before long-term knowledge becomes ready.
- Diff artifacts make updates auditable and reversible.

Alternatives considered:

- Directly update wiki/ pages: faster but risks solidifying incorrect knowledge.
- Never update existing pages: safe but prevents the Wiki from evolving.

### Decision 6: Keep repository analysis shallow in MVP

Repository analysis SHALL only inspect confirmed repository paths and extract metadata, structure, and engineering signals.

Rationale:

- The user's original requirement allows repository analysis only after confirmation.
- Deep code review would expand scope and privacy risk.
- Metadata and structure are enough to enrich Agent engineering and engineering practice signals for MVP.

Alternatives considered:

- Full code quality review: valuable later, but not aligned with MVP.
- No repository analysis: simpler, but loses useful programmer and Agent engineering context.

### Decision 7: Use local validators around LLM-generated content

LLM-generated Diagnosis, GrowthTask, ActionAsset, WikiPage, and WikiUpdateProposal outputs SHALL be validated locally before export.

Validators should check:

- Required fields.
- Evidence or RawSource references.
- Done definitions for tasks.
- Privacy constraints.
- Wiki frontmatter.
- Diff-first requirements.
- Unknown status when evidence is insufficient.

Rationale:

- The LLM can draft nuanced content, but local validation enforces product invariants.
- Validation failures can be reported and regenerated without corrupting long-term assets.

## Risks / Trade-offs

- LLM over-summarizes or invents stable knowledge -> require EvidenceItem or RawSource references, confidence, status, and Wiki lint.
- Sensitive content leaks into ActionAsset or WikiPage -> run privacy checks before export and block unsafe outputs.
- Users ignore generated tasks -> keep GrowthTask scoped by time budget, include done definitions, and generate machine-usable assets that reduce friction.
- Business-depth maturity is under-evidenced from coding conversations -> output Unknown or generate business information collection tasks instead of strong conclusions.
- Wiki update review adds friction -> keep MVP diff proposals small and focused on high-value pages.
- Too many capabilities make MVP large -> implement a thin vertical slice through all layers before optimizing any individual module.

## Migration Plan

This is a new capability set, so there is no existing production migration.

Suggested rollout:

1. Create project skeleton and data model definitions.
2. Implement sample-data based pipeline before scanning real user data.
3. Add source discovery for one AI tool, then expand to Codex, Claude Code, and opencode.
4. Add local redaction and privacy audit before any LLM integration.
5. Generate EvidenceItem and EvidenceSignal from controlled fixtures.
6. Generate one GrowthCycle and three GrowthTasks from sample evidence.
7. Generate ActionAsset and WikiUpdateProposal outputs.
8. Initialize `llm-wiki/` and `runs/<timestamp>/` outputs.
9. Add optional repository signal analysis after user path confirmation.

Rollback strategy:

- Because MVP writes files locally, rollback consists of deleting or archiving the generated `runs/<timestamp>/` directory and rejecting unapplied WikiUpdateProposal files.
- Existing raw sources and wiki/ pages must not be overwritten without review.

## Open Questions

- Which concrete local paths and file formats should be supported first for Codex, Claude Code, and opencode?
- Should `llm-wiki/` live inside the project root by default or be configurable as a user-level workspace?
- Should the MVP use an external LLM for diagnosis and task drafting, or first provide a local-rule-only baseline?
- What is the first supported CLI command shape for running a GrowthCycle?
- How should human approval for WikiUpdateProposal be represented in the first implementation: file status, CLI command, or manual edit?
