from __future__ import annotations

from pathlib import Path

from .models import ActionAsset, EvidenceItem, EvidenceSignal, GrowthCycle, GrowthRunSnapshot, WikiLintIssue, WikiUpdateProposal
from .utils import write_json


def write_reports(run_dir: Path, cycle: GrowthCycle, evidence: list[EvidenceItem], signals: list[EvidenceSignal], assets: list[ActionAsset], proposals: list[WikiUpdateProposal], lint_issues: list[WikiLintIssue], growth_snapshot: GrowthRunSnapshot | None = None, growth_memory_proposals: list[WikiUpdateProposal] | None = None, analyzer: dict[str, object] | None = None) -> None:
    markdown = _render_markdown(cycle, assets, proposals, lint_issues, growth_snapshot, growth_memory_proposals or [], analyzer or {})
    (run_dir / "report.md").write_text(markdown, encoding="utf-8")
    write_json(
        run_dir / "report.json",
        {
            "growthCycle": cycle,
            "evidenceIds": [item.id for item in evidence],
            "signalIds": [signal.id for signal in signals],
            "actionAssetIds": [asset.id for asset in assets],
            "wikiUpdateIds": [proposal.id for proposal in proposals],
            "growthMemoryUpdateIds": [proposal.id for proposal in growth_memory_proposals or []],
            "growthRunSnapshotId": growth_snapshot.id if growth_snapshot else "",
            "analyzer": analyzer or {},
            "wikiLintIssueIds": [issue.id for issue in lint_issues],
        },
    )


def _render_markdown(cycle: GrowthCycle, assets: list[ActionAsset], proposals: list[WikiUpdateProposal], lint_issues: list[WikiLintIssue], growth_snapshot: GrowthRunSnapshot | None, growth_memory_proposals: list[WikiUpdateProposal], analyzer: dict[str, object]) -> str:
    lines = ["# 本轮成长任务包", "", "## 本周只做这 3 件事", ""]
    for index, task in enumerate(cycle.tasks, start=1):
        task_kind = "延续任务" if task.task_type == "carried_forward" else "新任务"
        lines.extend(
            [
                f"{index}. {task.title}（{task_kind}）",
                f"   目标轨道：{task.primary_track}",
                f"   时间预算：{task.time_budget_minutes} 分钟",
                f"   产物：{', '.join(task.expected_artifacts)}",
                f"   从哪里开始：{'; '.join(task.start_here)}",
                f"   结果写到哪里：{task.output_path}",
                f"   结果长什么样：{task.output_example}",
                "",
            ]
        )
    lines.extend(["## 为什么是这 3 件事", ""])
    lines.extend(f"- {diagnosis.title}: {diagnosis.summary}" for diagnosis in cycle.diagnoses)
    lines.extend(["", "## 三轨成熟度初判", ""])
    lines.extend(f"- {item.track}: {item.estimated_level} ({item.status})" for item in cycle.maturity_estimates)
    lines.extend(["", "## 分析器状态", ""])
    lines.append(f"- Provider: {analyzer.get('provider', 'local')}")
    lines.append(f"- Mode: {analyzer.get('analysisMode', 'local')}")
    lines.append(f"- Outbound approved: {analyzer.get('approved', False)}")
    lines.append(f"- Validation: {analyzer.get('validationStatus', 'local')}")
    lines.append(f"- Fallback: {analyzer.get('fallbackMode', '')}")
    if analyzer.get("credentialSource"):
        lines.append(f"- Credential source: {analyzer.get('credentialSource')}")
    if analyzer.get("message"):
        lines.append(f"- Message: {analyzer.get('message')}")
    warnings = analyzer.get("warnings") or []
    if isinstance(warnings, list) and warnings:
        lines.append("- Warnings:")
        for warning in warnings:
            lines.append(f"  - {warning}")
    prompts = analyzer.get("prompts") or []
    if isinstance(prompts, list) and prompts:
        lines.append("- Prompts:")
        for prompt in prompts:
            if isinstance(prompt, dict):
                lines.append(f"  - {prompt.get('id')}@{prompt.get('version')} ({prompt.get('scenario')})")
    lines.extend(["", "## 配套 ActionAssets", ""])
    lines.extend(f"- {asset.title}: {asset.export_path}" for asset in assets)
    lines.extend(["", "## LLM Wiki 已更新", ""])
    lines.extend(f"- {proposal.target_path}: {proposal.status}" for proposal in proposals)
    lines.extend(["", "## 成长记忆更新", ""])
    if growth_snapshot:
        lines.append(f"- Raw growth run snapshot: {growth_snapshot.path}")
    lines.extend(f"- {proposal.target_path}: {proposal.status}" for proposal in growth_memory_proposals)
    if cycle.tasks:
        lines.extend(["", "## 术语解释", ""])
        glossary = {}
        for task in cycle.tasks:
            glossary.update(task.glossary)
        for term, description in glossary.items():
            lines.append(f"- {term}: {description}")
    lines.extend(["", "## Wiki Lint 摘要", ""])
    lines.extend(f"- {issue.severity}: {issue.type} {issue.page_path}" for issue in lint_issues)
    if not lint_issues:
        lines.append("- No lint issues.")
    return "\n".join(lines) + "\n"
