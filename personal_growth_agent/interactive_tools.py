from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audit import classify_sensitivity, redact_text
from .dashboard import build_static_dashboard, build_dashboard_data, open_static_dashboard
from .pipeline import run_growth_cycle
from .utils import utc_now_iso, write_json


@dataclass
class ToolContext:
    workspace: Path
    wiki_root: Path
    config_path: Path
    source_paths: dict[str, list[Path]] | None = None
    run_constraints: dict[str, object] | None = None
    growth_runner: Any | None = None


@dataclass
class ToolResult:
    name: str
    status: str
    result: dict[str, Any]
    error: str = ""


TOOL_NAMES = [
    "get_latest_report",
    "list_growth_tasks",
    "complete_growth_task",
    "list_wiki_pages",
    "read_wiki_page",
    "list_knowledge_gaps",
    "run_growth_cycle",
    "build_open_dashboard",
]


def list_tool_names() -> list[str]:
    return list(TOOL_NAMES)


def execute_tool(name: str, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
    if name not in TOOL_NAMES:
        return ToolResult(name=name, status="rejected", result={}, error=f"unapproved tool: {name}")
    if name == "get_latest_report":
        return ToolResult(name=name, status="ok", result=get_latest_report(context.workspace))
    if name == "list_growth_tasks":
        return ToolResult(name=name, status="ok", result={"tasks": list_growth_tasks(context.wiki_root)})
    if name == "complete_growth_task":
        task_id = str(arguments.get("task_id") or arguments.get("id") or "")
        completed = complete_growth_task(context.wiki_root, task_id)
        if not completed:
            return ToolResult(name=name, status="error", result={}, error=f"task not found: {task_id}")
        return ToolResult(name=name, status="ok", result={"task_id": completed})
    if name == "list_wiki_pages":
        return ToolResult(name=name, status="ok", result={"pages": list_wiki_pages(context.wiki_root)})
    if name == "read_wiki_page":
        path = str(arguments.get("path") or arguments.get("title") or "")
        return ToolResult(name=name, status="ok", result=read_wiki_page(context.wiki_root, path))
    if name == "list_knowledge_gaps":
        return ToolResult(name=name, status="ok", result={"gaps": list_knowledge_gaps(context.wiki_root)})
    if name == "run_growth_cycle":
        source_paths = context.source_paths or {}
        constraints = context.run_constraints or {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"}
        runner = context.growth_runner or run_growth_cycle
        result = runner(source_paths, context.workspace, constraints)
        return ToolResult(name=name, status="ok", result=result)
    dashboard_result = build_static_dashboard(context.workspace, context.wiki_root)
    opened = open_static_dashboard(Path(dashboard_result.entry_path))
    return ToolResult(name=name, status="ok", result={"entry_path": dashboard_result.entry_path, "opened": opened})


def get_latest_report(workspace: Path) -> dict[str, str]:
    report_path = _latest_report_path(workspace)
    if report_path is None:
        return {"path": "", "title": "", "summary": ""}
    text = report_path.read_text(encoding="utf-8")
    return {"path": str(report_path), "title": _first_heading(text) or report_path.parent.name, "summary": _safe_snippet(text)}


def list_growth_tasks(wiki_root: Path) -> list[dict[str, Any]]:
    active_path = wiki_root / "data" / "growth-tasks" / "active.json"
    if not active_path.exists():
        return []
    value = json.loads(active_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        return []
    return [_compact_task(item) for item in value if isinstance(item, dict)]


def complete_growth_task(wiki_root: Path, task_id: str) -> str:
    tasks_root = wiki_root / "data" / "growth-tasks"
    active_path = tasks_root / "active.json"
    archive_path = tasks_root / "archive.json"
    if not active_path.exists() or not task_id:
        return ""
    active_tasks = json.loads(active_path.read_text(encoding="utf-8"))
    archive_tasks = []
    if archive_path.exists():
        archive_tasks = json.loads(archive_path.read_text(encoding="utf-8"))
    remaining = []
    completed_task = None
    for task in active_tasks:
        if isinstance(task, dict) and task.get("id") == task_id:
            completed_task = task
            continue
        remaining.append(task)
    if completed_task is None:
        return ""
    completed_task["status"] = "completed"
    completed_task["archived_at"] = utc_now_iso()
    archive_by_id = {str(task.get("id")): task for task in archive_tasks if isinstance(task, dict) and task.get("id")}
    archive_by_id[task_id] = completed_task
    write_json(active_path, remaining)
    write_json(archive_path, list(archive_by_id.values()))
    return task_id


def list_wiki_pages(wiki_root: Path) -> list[dict[str, Any]]:
    pages = []
    wiki_path = wiki_root / "wiki"
    if not wiki_path.exists():
        return pages
    for page in sorted(wiki_path.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        sensitivity = str(metadata.get("sensitivity") or "")
        if sensitivity == "local_only":
            continue
        pages.append(
            {
                "path": str(page),
                "title": _first_heading(text) or page.stem,
                "type": metadata.get("type") or "",
                "status": metadata.get("status") or metadata.get("lifecycle_status") or "",
            }
        )
    return pages


def read_wiki_page(wiki_root: Path, path_or_title: str) -> dict[str, str]:
    page = _find_wiki_page(wiki_root, path_or_title)
    if page is None:
        return {"path": "", "title": "", "content": ""}
    text = page.read_text(encoding="utf-8")
    if classify_sensitivity(text) == "local_only":
        return {"path": str(page), "title": _first_heading(text) or page.stem, "content": "[LOCAL_ONLY]"}
    redacted, _ = redact_text(text)
    return {"path": str(page), "title": _first_heading(text) or page.stem, "content": redacted[:4000]}


def list_knowledge_gaps(wiki_root: Path) -> list[dict[str, Any]]:
    return [page for page in list_wiki_pages(wiki_root) if page.get("type") == "knowledge_gap"]


def summarize_tool_result(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): summarize_tool_result(item) for key, item in value.items()}
    if isinstance(value, list):
        return [summarize_tool_result(item) for item in value[:20]]
    if isinstance(value, str):
        redacted, _ = redact_text(value)
        if "private key" in redacted.lower():
            return "[LOCAL_ONLY]"
        return redacted[:500]
    return value


def sanitize_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    sanitized = {}
    for key, value in arguments.items():
        key_text = str(key)
        lowered = key_text.lower()
        if "key" in lowered or "token" in lowered or "secret" in lowered:
            sanitized[key_text] = "[REDACTED]"
            continue
        sanitized[key_text] = summarize_tool_result(value)
    return sanitized


def format_tasks(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return "暂无 active 成长任务。"
    lines = []
    for task in tasks:
        title = task.get("title") or ""
        task_id = task.get("id") or ""
        status = task.get("status") or ""
        lines.append(f"- {task_id} [{status}] {title}")
    return "\n".join(lines)


def format_pages(title: str, pages: list[dict[str, Any]]) -> str:
    if not pages:
        return f"{title}：暂无数据。"
    lines = [f"{title}："]
    for page in pages:
        page_title = page.get("title") or ""
        page_type = page.get("type") or ""
        path = page.get("path") or ""
        lines.append(f"- {page_title} ({page_type}) {path}")
    return "\n".join(lines)


def _latest_report_path(workspace: Path) -> Path | None:
    runs_root = workspace / "runs"
    if not runs_root.exists():
        return None
    today_report = runs_root / utc_now_iso()[:10] / "report.md"
    if today_report.exists():
        return today_report
    reports = sorted(runs_root.glob("*/report.md"))
    return reports[-1] if reports else None


def _compact_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": task.get("id"),
        "title": task.get("title") or "",
        "status": task.get("status") or task.get("level") or "",
        "track": task.get("primary_track") or "",
        "summary": task.get("why_this_task") or "",
        "steps": task.get("steps") or [],
        "doneDefinition": task.get("done_definition") or [],
    }


def _safe_snippet(text: str) -> str:
    if classify_sensitivity(text) == "local_only":
        return "[LOCAL_ONLY]"
    redacted, _ = redact_text(text)
    cleaned = " ".join(line.strip() for line in redacted.splitlines() if line.strip() and not line.startswith("---"))
    return cleaned[:500]


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, Any] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.rstrip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _find_wiki_page(wiki_root: Path, path_or_title: str) -> Path | None:
    candidate = Path(path_or_title)
    if candidate.exists() and candidate.is_file():
        return candidate
    wiki_path = wiki_root / "wiki"
    if not wiki_path.exists():
        return None
    normalized = path_or_title.strip().lower()
    for page in sorted(wiki_path.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        title = _first_heading(text).lower()
        if normalized in {str(page).lower(), page.stem.lower(), title}:
            return page
    return None
