from __future__ import annotations

from .models import Diagnosis, EvidenceSignal, GrowthCycle, GrowthMemoryContext, GrowthTask, MaturityEstimate
from .utils import stable_id


TRACKS = {
    "agent_engineering": "AI Agent 工程能力",
    "business_depth": "业务深度专家能力",
    "ai_system_management": "AI 系统管理与优化能力",
}


def generate_growth_cycle(signals: list[EvidenceSignal], constraints: dict[str, object], memory_context: GrowthMemoryContext | None = None) -> GrowthCycle:
    maturity_estimates = _estimate_maturity(signals)
    diagnoses = _generate_diagnoses(signals)
    cycle_id = stable_id("cycle", ",".join(signal.name for signal in signals), constraints)
    tasks = _generate_tasks(cycle_id, diagnoses, constraints)
    if memory_context and memory_context.active_tasks:
        carried_task = _carried_forward_task(cycle_id, memory_context.active_tasks[0], diagnoses, constraints)
        tasks = [carried_task, *tasks[:2]]
    if memory_context and memory_context.knowledge_gaps:
        gap_task = _knowledge_gap_task(cycle_id, memory_context.knowledge_gaps[0], diagnoses, constraints)
        tasks = [gap_task, *tasks[:2]]
    _validate_tasks(tasks)
    return GrowthCycle(
        id=cycle_id,
        theme="从 AI 协作者走向 Agent 流程编排者",
        cadence="weekly",
        constraints=constraints,
        maturity_estimates=maturity_estimates,
        diagnoses=diagnoses,
        tasks=tasks,
    )


def _estimate_maturity(signals: list[EvidenceSignal]) -> list[MaturityEstimate]:
    signal_names = {signal.name for signal in signals}
    return [
        MaturityEstimate(
            track="agent_engineering",
            estimated_level="A1-A2" if signal_names & {"decomposes_task_into_pipeline", "defines_stage_io"} else "A1",
            confidence=0.72 if signal_names & {"decomposes_task_into_pipeline", "defines_stage_io"} else 0.48,
            status="Observed" if signal_names & {"decomposes_task_into_pipeline", "defines_stage_io"} else "Inferred",
            observed_signals=sorted(signal_names & {"decomposes_task_into_pipeline", "defines_stage_io", "identifies_tool_boundaries", "plans_error_recovery"}),
            missing_signals_for_next_level=["implements_tool_interface", "tests_agent_behavior"],
        ),
        MaturityEstimate(
            track="business_depth",
            estimated_level="B1-B2" if signal_names & {"asks_business_goal", "asks_acceptance_criteria"} else "Unknown",
            confidence=0.62 if signal_names & {"asks_business_goal", "asks_acceptance_criteria"} else 0.2,
            status="Inferred" if signal_names & {"asks_business_goal", "asks_acceptance_criteria"} else "Unknown",
            observed_signals=sorted(signal_names & {"asks_business_goal", "asks_acceptance_criteria", "models_business_process", "links_task_to_metric"}),
            missing_signals_for_next_level=["models_business_process", "links_task_to_metric"],
            caution="业务场景证据不足时，不强行判断业务深度。",
        ),
        MaturityEstimate(
            track="ai_system_management",
            estimated_level="C1-C2" if signal_names & {"requires_verification", "updates_rule_after_failure", "corrects_ai_assumption"} else "C1",
            confidence=0.75 if signal_names & {"requires_verification", "updates_rule_after_failure", "corrects_ai_assumption"} else 0.45,
            status="Observed" if signal_names & {"requires_verification", "updates_rule_after_failure", "corrects_ai_assumption"} else "Inferred",
            observed_signals=sorted(signal_names & {"requires_verification", "identifies_ai_failure_reason", "updates_rule_after_failure", "classifies_failure_type"}),
            missing_signals_for_next_level=["compares_before_after", "creates_evaluation_sample"],
        ),
    ]


def _generate_diagnoses(signals: list[EvidenceSignal]) -> list[Diagnosis]:
    signal_names = {signal.name for signal in signals}
    evidence_ids = sorted({evidence_id for signal in signals for evidence_id in signal.observed_in_evidence_ids})
    diagnoses: list[Diagnosis] = []
    if signal_names & {"requires_verification", "sets_constraints", "decomposes_task_into_pipeline"}:
        diagnoses.append(
            Diagnosis(
                id=stable_id("diag", "agent-flow", ",".join(sorted(signal_names))),
                type="leverage_point",
                title="AI 协作能力可升级为 Agent 流程编排能力",
                target_tracks=["agent_engineering", "ai_system_management"],
                summary="已有上下文、约束和验证意识，下一步应把会话抽象为可复用 Agent 流程。",
                confidence=0.78,
                supporting_signal_ids=[signal.id for signal in signals if signal.name in signal_names],
                supporting_evidence_ids=evidence_ids,
                recommended_focus="将复杂 AI 会话拆成目标、输入、状态、工具、失败点和输出。",
            )
        )
    if not signal_names & {"models_business_process"}:
        diagnoses.append(
            Diagnosis(
                id=stable_id("diag", "business-depth", ",".join(sorted(signal_names))),
                type="knowledge_gap",
                title="业务流程建模证据不足",
                target_tracks=["business_depth"],
                summary="当前证据中业务目标和验收信号存在，但业务流程建模仍需要补采和练习。",
                confidence=0.62,
                supporting_signal_ids=[signal.id for signal in signals if signal.name in {"asks_business_goal", "asks_acceptance_criteria", "links_task_to_metric"}],
                supporting_evidence_ids=evidence_ids,
                recommended_focus="为真实 AI 协作案例补充业务目标、指标和流程影响。",
            )
        )
    if signal_names & {"requires_verification", "corrects_ai_assumption", "updates_rule_after_failure"}:
        diagnoses.append(
            Diagnosis(
                id=stable_id("diag", "ai-output-rubric", ",".join(sorted(signal_names))),
                type="bottleneck",
                title="AI 输出验证需要形成稳定 Rubric",
                target_tracks=["ai_system_management"],
                summary="已有验证和纠错意识，下一步应沉淀为 AI 输出验收 Rubric 和失败归因模板。",
                confidence=0.76,
                supporting_signal_ids=[signal.id for signal in signals if signal.name in signal_names],
                supporting_evidence_ids=evidence_ids,
                recommended_focus="定义正确性、完整性、可执行性、安全性和业务价值维度。",
            )
        )
    return diagnoses


def _generate_tasks(cycle_id: str, diagnoses: list[Diagnosis], constraints: dict[str, object]) -> list[GrowthTask]:
    minutes = int(constraints.get("weeklyTimeBudgetHours", 3)) * 60
    task_budget = max(30, minutes // 3)
    source_diagnosis_ids = [diagnosis.id for diagnosis in diagnoses]
    return [
        GrowthTask(
            id=stable_id("task", cycle_id, "agent-flow"),
            cycle_id=cycle_id,
            title="把一次复杂 AI 会话抽象成 Agent 流程图",
            primary_track="agent_engineering",
            secondary_tracks=["ai_system_management", "business_depth"],
            maturity_move={"track": "agent_engineering", "fromLevel": "A1", "toLevel": "A2"},
            task_type="case_analysis",
            level="weekly",
            time_budget_minutes=task_budget,
            why_this_task="将高质量 AI 协作经验转化为 Agent 流程编排能力。",
            start_here=["运行 pga report latest 找到最新报告", "运行 pga dashboard open 打开静态仪表盘", "在报告的 Evidence 或 Dashboard 的推荐任务中选择一次最近印象最深的 AI 协作会话"],
            source_diagnosis_ids=source_diagnosis_ids,
            steps=["写清这次会话要解决的真实问题", "列出你给 AI 的输入、补充约束和使用到的工具", "标出哪些步骤由 AI 完成、哪些步骤需要你确认", "记录返工、误判或需要人工兜底的地方", "提炼 1 条下次可以复用的 Agent 规则"],
            output_path="llm-wiki/wiki/agent-engineering/agent-flow-analyses/<日期>-case.md",
            output_example="# Agent 流程复盘：默认工作区改造\n\n## 目标\n让 pga 命令默认使用本地工作区。\n\n## 流程\n1. 读取 CLI 参数解析\n2. 补默认工作区测试\n3. 修改 config 和 README\n4. 运行测试验证\n\n## 人工确认点\n默认目录是否符合真实使用习惯。\n\n## 可复用规则\nCLI 默认行为变更必须同步测试和 README。",
            done_definition=["产出 agent-flow-analysis.md", "至少引用 3 条 EvidenceItem", "至少沉淀 1 条 Agent 规则"],
            review_questions=["哪些步骤可自动化？", "哪些步骤必须人工确认？", "下次同类 Agent 第一约束是什么？"],
            expected_artifacts=["llm-wiki/wiki/agent-engineering/agent-flow-analyses/case.md"],
            glossary={"Agent 流程": "把一次 AI 协作拆成可重复执行的目标、输入、工具、判断点和输出。", "EvidenceItem": "系统从你的 AI 对话里抽取出的行为证据，不是原始聊天全文。"},
        ),
        GrowthTask(
            id=stable_id("task", cycle_id, "business-goal"),
            cycle_id=cycle_id,
            title="为该会话补业务目标卡",
            primary_track="business_depth",
            secondary_tracks=["agent_engineering"],
            maturity_move={"track": "business_depth", "fromLevel": "B1", "toLevel": "B2"},
            task_type="business_modeling",
            level="weekly",
            time_budget_minutes=task_budget,
            why_this_task="把技术任务连接到业务目标、指标和流程影响，减少信息中转倾向。",
            start_here=["打开最新报告里的任务列表", "选择一个最近完成的功能、修复或系统设计任务", "优先选你能说清楚用户、业务目标和验收标准的案例"],
            source_diagnosis_ids=source_diagnosis_ids,
            steps=["写出这个任务服务的用户或业务角色", "写出业务目标，而不是技术动作", "写出成功后应该变化的指标、成本或风险", "写出验收标准：什么结果算完成", "补一句 AI 在这个任务里实际降低了什么成本"],
            output_path="llm-wiki/wiki/business-depth/business-goal-cards/<日期>-case.md",
            output_example="# 业务目标卡：默认工作区改造\n\n## 用户\n本地使用 PGA 的开发者。\n\n## 业务目标\n降低每次运行命令的心智负担。\n\n## 验收标准\n用户可以直接执行 pga run，不需要反复输入 --workspace。\n\n## AI 介入价值\n帮助发现 README、CLI 行为和测试之间的不一致。",
            done_definition=["产出 business-goal-card.md", "至少包含目标、指标、基线或验收标准", "至少引用 1 条 EvidenceItem"],
            review_questions=["真实业务目标是什么？", "影响哪个指标？", "AI 介入降低了什么成本？"],
            expected_artifacts=["llm-wiki/wiki/business-depth/business-goal-cards/case.md"],
            glossary={"业务目标卡": "把一个技术任务翻译成用户、目标、指标和验收标准的简短文档。", "验收标准": "判断这件事是否真正完成的可检查条件。"},
        ),
        GrowthTask(
            id=stable_id("task", cycle_id, "ai-rubric"),
            cycle_id=cycle_id,
            title="为该会话定义 AI 输出验收 Rubric",
            primary_track="ai_system_management",
            secondary_tracks=["agent_engineering"],
            maturity_move={"track": "ai_system_management", "fromLevel": "C1", "toLevel": "C2"},
            task_type="evaluation_design",
            level="weekly",
            time_budget_minutes=task_budget,
            why_this_task="把即时验证意识升级为可复用的 AI 系统管理机制。",
            start_here=["打开一次你曾经让 AI 改代码、写文档或分析问题的会话", "找出其中一次 AI 输出让你不满意、需要返工或需要验证的地方", "把这次失败或风险整理成检查项"],
            source_diagnosis_ids=source_diagnosis_ids,
            steps=["写出这类 AI 输出最容易错在哪里", "定义正确性标准：什么事实或代码路径必须对", "定义完整性标准：哪些内容缺失就不能接受", "定义可执行性标准：用户下一步能不能直接执行", "定义安全性和隐私边界", "把标准整理成下次可复用的检查清单"],
            output_path="llm-wiki/wiki/ai-system-management/evaluation-rubrics/<日期>-case.md",
            output_example="# AI 输出验收 Rubric：README 命令说明\n\n## 适用场景\nAI 修改项目使用文档。\n\n## 检查维度\n- 正确性：命令必须和 CLI 实际行为一致。\n- 完整性：安装、更新、卸载都要覆盖。\n- 可执行性：用户能按顺序复制执行。\n- 安全性：不能泄露 API key。\n- 验证：必须说明跑过哪些命令。",
            done_definition=["产出 ai-output-rubric.md", "至少包含 5 个评分维度", "至少包含 3 个失败标签"],
            review_questions=["AI 输出最常在哪类环节失败？", "如何提前发现失败？", "下次如何比较优化前后？"],
            expected_artifacts=["llm-wiki/wiki/ai-system-management/evaluation-rubrics/case.md"],
            glossary={"Rubric": "一组评分或验收维度，用来判断 AI 输出能不能被接受。", "失败标签": "给常见问题分类的短标签，例如事实错误、缺少验证、不可执行。"},
        ),
    ]


def _carried_forward_task(cycle_id: str, prior_task: dict[str, object], diagnoses: list[Diagnosis], constraints: dict[str, object]) -> GrowthTask:
    minutes = int(constraints.get("weeklyTimeBudgetHours", 3)) * 60
    task_budget = max(30, minutes // 3)
    source_diagnosis_ids = [diagnosis.id for diagnosis in diagnoses]
    prior_title = str(prior_task.get("title") or "历史成长任务")
    tracks = prior_task.get("tracks")
    primary_track = "agent_engineering"
    if isinstance(tracks, list) and tracks:
        primary_track = str(tracks[0])
    return GrowthTask(
        id=stable_id("task", cycle_id, "carried-forward", prior_task.get("path", prior_title)),
        cycle_id=cycle_id,
        title=f"延续并复盘：{prior_title}",
        primary_track=primary_track,
        secondary_tracks=["ai_system_management"],
        maturity_move={"track": primary_track, "fromLevel": "current", "toLevel": "reviewed"},
        task_type="carried_forward",
        level="weekly",
        time_budget_minutes=task_budget,
        why_this_task="历史 LLM Wiki 中仍有未完成或未复盘的成长任务，优先闭环再新增任务。",
        start_here=["打开 Dashboard 的 tasks 页面", "找到这条历史任务对应的 Wiki 页面", "先判断它是继续、缩小还是关闭"],
        source_diagnosis_ids=source_diagnosis_ids,
        steps=["找到历史任务原文", "补充完成状态和阻塞点", "产出复盘记录", "决定继续、调整或关闭该任务"],
        output_path="llm-wiki/wiki/growth/reviews/carried-forward-review.md",
        output_example="# 成长任务复盘\n\n## 原任务\n写出历史任务标题。\n\n## 当前状态\n完成 / 部分完成 / 放弃。\n\n## 阻塞点\n说明为什么没有闭环。\n\n## 下一步\n继续、缩小或关闭。",
        done_definition=["产出 growth-review.md", "明确任务状态", "至少写出 1 条下一轮改进依据"],
        review_questions=["这个任务为什么没有闭环？", "是否仍符合当前目标？", "下一轮应该继续、缩小还是关闭？"],
        expected_artifacts=["llm-wiki/wiki/growth/reviews/carried-forward-review.md"],
        glossary={"复盘": "回看任务结果、阻塞点和下一步决策。"},
    )


def _knowledge_gap_task(cycle_id: str, gap: dict[str, object], diagnoses: list[Diagnosis], constraints: dict[str, object]) -> GrowthTask:
    minutes = int(constraints.get("weeklyTimeBudgetHours", 3)) * 60
    task_budget = max(30, minutes // 3)
    source_diagnosis_ids = [diagnosis.id for diagnosis in diagnoses]
    title = str(gap.get("title") or "知识缺口")
    tracks = gap.get("tracks")
    primary_track = "agent_engineering"
    if isinstance(tracks, list) and tracks:
        primary_track = str(tracks[0])
    return GrowthTask(
        id=stable_id("task", cycle_id, "knowledge-gap", gap.get("path", title)),
        cycle_id=cycle_id,
        title=f"围绕知识缺口做一次应用练习：{title}",
        primary_track=primary_track,
        secondary_tracks=["ai_system_management"],
        maturity_move={"track": primary_track, "fromLevel": "context", "toLevel": "applied"},
        task_type="knowledge_gap",
        level="weekly",
        time_budget_minutes=task_budget,
        why_this_task="外部知识只能作为学习上下文，需要通过可验证练习转化为个人能力证据。",
        start_here=["打开 Obsidian 或 Dashboard 查看知识缺口页面", "选择一个你能在当前项目中实践的问题", "把实践目标缩小到 1 小时内能完成"],
        source_diagnosis_ids=source_diagnosis_ids,
        steps=["阅读关联知识页", "抽取 1 个可实践问题", "在真实项目或案例中应用", "记录结果和证据"],
        output_path="llm-wiki/wiki/growth/tasks/knowledge-gap-application.md",
        output_example="# 知识应用练习\n\n## 知识点\n写出本次应用的知识页。\n\n## 实践问题\n写出要解决的具体问题。\n\n## 应用过程\n记录你怎么用它改变设计或实现。\n\n## 结果\n说明得到的产物和证据。",
        done_definition=["产出 knowledge-gap-application.md", "引用知识页和原始来源", "补充至少 1 条个人实践证据"],
        review_questions=["这条知识如何改变实际决策？", "哪里仍然只是理解而非掌握？", "下一次如何验证效果？"],
        expected_artifacts=["llm-wiki/wiki/growth/tasks/knowledge-gap-application.md"],
        glossary={"知识缺口": "已经收集到但尚未通过真实实践证明掌握的知识点。"},
    )


def _validate_tasks(tasks: list[GrowthTask]) -> None:
    for task in tasks:
        if not task.done_definition or not task.review_questions or not task.steps or not task.expected_artifacts or not task.start_here or not task.output_path:
            raise ValueError(f"invalid growth task: {task.id}")
