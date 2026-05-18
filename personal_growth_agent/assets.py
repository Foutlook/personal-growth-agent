from __future__ import annotations

from .audit import assert_no_sensitive_content
from .models import ActionAsset, Diagnosis, EvidenceItem, GrowthTask
from .utils import stable_id


ASSET_BY_TRACK = {
    "agent_engineering": ("prompt_snippet", "Agent 流程设计前置提示", "before_agent_design", "prompts/pre-agent-design.md"),
    "business_depth": ("template", "业务目标卡模板", "before_requirement_analysis", "templates/business-goal-card.md"),
    "ai_system_management": ("checklist", "AI 输出验收清单", "before_accepting_ai_output", "checklists/ai-output-verification.md"),
}


def generate_action_assets(tasks: list[GrowthTask], diagnoses: list[Diagnosis], evidence: list[EvidenceItem]) -> list[ActionAsset]:
    evidence_ids = [item.id for item in evidence[:5]]
    assets: list[ActionAsset] = []
    for task in tasks:
        asset_type, title, trigger, relative_path = ASSET_BY_TRACK.get(
            task.primary_track,
            ("playbook", f"{task.title} Playbook", "during_growth_task", "playbooks/growth-task.md"),
        )
        content = _content_for(task)
        assert_no_sensitive_content(content)
        assets.append(
            ActionAsset(
                id=stable_id("asset", task.id, asset_type),
                type=asset_type,
                title=title,
                trigger=trigger,
                target_tool="generic",
                content=content,
                usage_instruction="在下一轮 AI 协作前复制或引用该资产。",
                source_task_ids=[task.id],
                source_diagnosis_ids=task.source_diagnosis_ids,
                source_evidence_ids=evidence_ids,
                review_metric="下一轮相关会话是否使用该资产并产生复盘记录。",
                export_path=f"llm-wiki/machine-usable/{relative_path}",
            )
        )
    return assets


def export_action_assets(wiki_root, assets: list[ActionAsset]) -> None:
    from pathlib import Path

    root = Path(wiki_root)
    for asset in assets:
        relative = asset.export_path.removeprefix("llm-wiki/")
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        assert_no_sensitive_content(asset.content)
        path.write_text(asset.content, encoding="utf-8")


def _content_for(task: GrowthTask) -> str:
    lines = [
        f"# {task.title}",
        "",
        "## 使用时机",
        task.task_type,
        "",
        "## 执行步骤",
    ]
    lines.extend(f"- {step}" for step in task.steps)
    lines.append("")
    lines.append("## 完成定义")
    lines.extend(f"- {item}" for item in task.done_definition)
    return "\n".join(lines)
