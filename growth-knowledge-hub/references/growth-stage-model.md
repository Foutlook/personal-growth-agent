# Growth Stage Model — AI Agent Engineer

This document defines the 4-stage model for growing into an AI Agent Engineer. The host CLI uses these definitions to assess the user's current stage from conversation content and generate tasks that push toward the next stage.

## Stage Definitions

### L1: Tool User

**Capability**: Uses Claude Code / Copilot / Codex for daily coding tasks.

**Signals in conversation**:
- Single-file edits, bug fixes, simple refactors
- Basic prompt-and-response patterns
- Using built-in commands without customization
- No mention of SKILL.md, system prompt, or agent behavior

**Next stage goal**: Begin controlling agent behavior through structured prompts.

### L2: Prompt Engineer

**Capability**: Writes SKILL.md and system prompts that reliably control agent behavior.

**Signals in conversation**:
- Writing or editing SKILL.md, AGENTS.md, system prompts
- Debugging prompt output, iterating on instructions
- Discussing tool selection, context window, prompt structure
- Creating slash commands or custom workflows

**Next stage goal**: Design multi-component agent systems with tool chains and memory.

### L3: Agent Architect

**Capability**: Designs multi-agent collaboration, tool chains, and memory systems.

**Signals in conversation**:
- Designing agent orchestration, multi-agent workflows
- Building MCP servers, custom tools, hook systems
- Architecting memory/knowledge systems (like this skill)
- Discussing context management, state persistence, agent communication

**Next stage goal**: Package agent capabilities into deliverable products.

### L4: Agent Product

**Capability**: Ships agent-based products as installable skills, packages, or services.

**Signals in conversation**:
- Publishing skills, creating release workflows
- Writing evaluation harnesses, test prompts, benchmarks
- Handling user feedback, iterating on product-market fit
- Documenting for external users, not just self

**Next stage goal**: Scale and maintain agent products in production.

## Task Generation Rules

When generating growth tasks, follow these rules:

1. **Assess current stage**: Look at the conversation content. What stage do the user's actions and discussions represent?
2. **Target next stage**: Generate tasks that bridge from the current stage to the next one.
3. **Be concrete**: Each task must be a specific action the user can do in their next session, not a vague goal.
4. **Include done definition**: Every task needs a clear completion criterion.
5. **Explain rationale**: Briefly why this task now, based on the conversation.
6. **1-3 tasks per capture**: Don't overwhelm. Pick the most impactful tasks.
7. **Respect dedup**: If a similar active task already exists in `wiki/growth/tasks/`, skip it.

## Task Examples by Stage Transition

### L1 → L2 tasks
- "为当前项目的 README 写一个 SKILL.md，定义 3 条 agent 行为规则"
- "用 system prompt 控制 agent 在代码审查时只关注安全问题，观察效果"
- "写一个 slash command 封装常用的 git 工作流"

### L2 → L3 tasks
- "设计一个双 agent 协作流程：一个写代码，一个审查，定义它们的通信协议"
- "为当前项目实现一个 MCP server，暴露 3 个自定义工具"
- "设计一个 hook 系统，在 agent 每次编辑文件后自动运行 lint"

### L3 → L4 tasks
- "把当前的 agent 工作流打包成可安装的 skill，写好 README 和 test-prompts"
- "为 skill 编写 3 个测试用例，验证触发准确性和输出质量"
- "收集 2 个用户对 skill 的反馈，记录到 wiki 并规划改进"
