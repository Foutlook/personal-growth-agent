from __future__ import annotations

from collections import defaultdict

from .audit import classify_sensitivity
from .models import ConversationSession, EvidenceItem, EvidenceSignal, RepositoryEvidencePack
from .utils import stable_id


SIGNAL_RULES: dict[str, dict[str, object]] = {
    "provides_context": {"category": "ai_collaboration", "terms": ["背景", "上下文", "项目状态"]},
    "sets_constraints": {"category": "ai_collaboration", "terms": ["约束", "规则", "必须", "不要"]},
    "asks_for_plan_before_action": {"category": "ai_collaboration", "terms": ["先分析", "先计划", "不要改代码"]},
    "requires_verification": {"category": "ai_collaboration", "terms": ["验证", "测试", "检查输出"]},
    "corrects_ai_assumption": {"category": "ai_collaboration", "terms": ["假设错", "错误假设"]},
    "externalizes_ai_rules": {"category": "ai_collaboration", "terms": ["更新规则", "检查清单", "模板"]},
    "decomposes_task_into_pipeline": {"category": "agent_engineering", "terms": ["拆成", "数据层", "证据层", "成长层", "Wiki 层"]},
    "defines_stage_io": {"category": "agent_engineering", "terms": ["输入输出", "输入", "输出"]},
    "identifies_tool_boundaries": {"category": "agent_engineering", "terms": ["工具边界", "工具"]},
    "plans_error_recovery": {"category": "agent_engineering", "terms": ["失败降级", "降级", "重试"]},
    "asks_business_goal": {"category": "business_depth", "terms": ["业务目标", "指标"]},
    "asks_acceptance_criteria": {"category": "business_depth", "terms": ["验收标准"]},
    "models_business_process": {"category": "business_depth", "terms": ["业务流程", "流程"]},
    "links_task_to_metric": {"category": "business_depth", "terms": ["错误率", "处理时长", "指标"]},
    "identifies_ai_failure_reason": {"category": "ai_system_management", "terms": ["失败原因", "假设错"]},
    "classifies_failure_type": {"category": "ai_system_management", "terms": ["归因", "分类"]},
    "updates_rule_after_failure": {"category": "ai_system_management", "terms": ["更新规则"]},
    "defines_permission_boundary": {"category": "ai_system_management", "terms": ["人工确认", "权限", "边界"]},
    "creates_checklist": {"category": "knowledge_curation", "terms": ["检查清单"]},
    "creates_template": {"category": "knowledge_curation", "terms": ["模板"]},
}


def extract_evidence(sessions: list[ConversationSession], repository_packs: list[RepositoryEvidencePack] | None = None) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    for session in sessions:
        text = "\n".join(str(message.get("content", "")) for message in session.messages)
        for signal, rule in SIGNAL_RULES.items():
            terms = [str(term) for term in rule["terms"]]
            if any(term in text for term in terms):
                evidence.append(
                    EvidenceItem(
                        id=stable_id("ev", session.id, signal),
                        source_session_id=session.id,
                        source_ref=session.source_ref,
                        category=str(rule["category"]),
                        signal=signal,
                        summary=f"Session {session.id} shows {signal}.",
                        sensitivity=classify_sensitivity(text),
                        confidence=0.82,
                        tags=[session.task_type, str(rule["category"])],
                    )
                )
    for pack in repository_packs or []:
        for signal, enabled in pack.signals.items():
            if enabled:
                evidence.append(
                    EvidenceItem(
                        id=stable_id("ev", pack.path, signal),
                        source_session_id="repository",
                        source_ref=pack.path,
                        category="repository",
                        signal=signal,
                        summary=f"Repository signal detected: {signal}.",
                        sensitivity="safe",
                        confidence=0.7,
                        tags=["repository"],
                    )
                )
    return evidence


def aggregate_signals(evidence: list[EvidenceItem]) -> list[EvidenceSignal]:
    grouped: dict[str, list[EvidenceItem]] = defaultdict(list)
    for item in evidence:
        grouped[item.signal].append(item)

    signals: list[EvidenceSignal] = []
    for signal_name, items in sorted(grouped.items()):
        category = SIGNAL_RULES.get(signal_name, {}).get("category", items[0].category)
        contexts = sorted({tag for item in items for tag in item.tags if tag})
        signals.append(
            EvidenceSignal(
                id=stable_id("signal", signal_name, ",".join(item.id for item in items)),
                name=signal_name,
                category=str(category),
                polarity="positive",
                observed_in_evidence_ids=[item.id for item in items],
                frequency=len(items),
                contexts=contexts,
                confidence=min(0.95, sum(item.confidence for item in items) / len(items)),
                supports_maturity=_supports_maturity(signal_name),
            )
        )
    return signals


def _supports_maturity(signal_name: str) -> list[dict[str, object]]:
    category = SIGNAL_RULES.get(signal_name, {}).get("category")
    if category == "agent_engineering":
        return [{"track": "agent_engineering", "level": "A2", "weight": 0.7}]
    if category == "business_depth":
        return [{"track": "business_depth", "level": "B2", "weight": 0.7}]
    if category == "ai_system_management":
        return [{"track": "ai_system_management", "level": "C2", "weight": 0.7}]
    if category == "ai_collaboration":
        return [{"track": "ai_system_management", "level": "C1", "weight": 0.5}]
    return []
