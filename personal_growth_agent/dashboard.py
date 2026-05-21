from __future__ import annotations

import json
import os
import webbrowser
from pathlib import Path
from typing import Any

from .audit import classify_sensitivity
from .models import DashboardBuildResult
from .utils import sha256_text, utc_now_iso, write_json
from .wiki import init_llm_wiki, lint_wiki, read_growth_memory_state, read_wiki_write_log


def build_static_dashboard(workspace: Path, wiki_root: Path) -> DashboardBuildResult:
    init_llm_wiki(wiki_root)
    dashboard_root = workspace / "dashboard"
    assets_root = dashboard_root / "assets"
    data_root = dashboard_root / "data"
    assets_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    data, omitted_local_only_count = build_dashboard_data(workspace, wiki_root)
    data_path = data_root / "dashboard-data.json"
    css_path = assets_root / "dashboard.css"
    js_path = assets_root / "dashboard.js"
    entry_path = dashboard_root / "index.html"
    write_json(data_path, data)
    css_path.write_text(_dashboard_css(), encoding="utf-8")
    js_path.write_text(_dashboard_js(), encoding="utf-8")
    entry_path.write_text(_dashboard_html(data), encoding="utf-8")
    return DashboardBuildResult(
        entry_path=str(entry_path),
        data_path=str(data_path),
        assets_path=str(assets_root),
        omitted_local_only_count=omitted_local_only_count,
    )


def build_dashboard_data(workspace: Path, wiki_root: Path) -> tuple[dict[str, Any], int]:
    manifest = _read_manifest(wiki_root)
    safe_sources = []
    omitted_local_only_count = 0
    for entry in manifest:
        sensitivity = str(entry.get("sensitivity") or entry.get("redactionStatus") or "safe")
        if sensitivity == "local_only":
            omitted_local_only_count += 1
            continue
        safe_sources.append(_safe_source_entry(entry))
    lint_issues = lint_wiki(wiki_root)
    data = {
        "builtAt": utc_now_iso(),
        "workspace": str(workspace),
        "wikiRoot": str(wiki_root),
        "reports": _report_index(workspace),
        "wikiPages": _wiki_page_index(wiki_root),
        "wikiWrites": _wiki_write_index(wiki_root),
        "sources": safe_sources,
        "growth": _growth_index(wiki_root),
        "knowledgeGaps": _knowledge_gap_index(wiki_root),
        "privacy": {
            "omittedLocalOnlyCount": omitted_local_only_count,
            "dashboardSafeSourceCount": len(safe_sources),
        },
        "lint": [_lint_issue_to_dict(issue) for issue in lint_issues],
    }
    return data, omitted_local_only_count


def open_static_dashboard(entry_path: Path) -> bool:
    if not entry_path.exists():
        return False
    return bool(webbrowser.open(entry_path.resolve().as_uri()))


def _read_manifest(wiki_root: Path) -> list[dict[str, Any]]:
    manifest_path = wiki_root / "data" / "source-manifest.json"
    if not manifest_path.exists():
        return []
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _wiki_write_index(wiki_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": entry.get("id"),
            "targetPath": entry.get("targetPath"),
            "operation": entry.get("operation"),
            "sourceRawIds": entry.get("sourceRawIds") or [],
            "sourceEvidenceIds": entry.get("sourceEvidenceIds") or [],
            "promptId": entry.get("promptId") or "",
            "promptDigest": entry.get("promptDigest") or "",
            "writtenAt": entry.get("writtenAt") or "",
            "contentHash": entry.get("contentHash") or "",
        }
        for entry in read_wiki_write_log(wiki_root)
    ]


def _safe_source_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourceId": entry.get("sourceId"),
        "rawSourceId": entry.get("rawSourceId"),
        "sourceType": entry.get("sourceType"),
        "originalLocation": entry.get("originalLocation"),
        "originalUrl": entry.get("originalUrl"),
        "ingestedAt": entry.get("ingestedAt"),
        "sensitivity": entry.get("sensitivity") or entry.get("redactionStatus"),
        "hash": entry.get("hash"),
        "tags": entry.get("tags") or [],
        "publisher": entry.get("publisher") or "",
    }


def _report_index(workspace: Path) -> list[dict[str, str]]:
    reports_by_digest = {}
    runs_root = workspace / "runs"
    if not runs_root.exists():
        return []
    for report_path in sorted(runs_root.glob("*/report.md")):
        text = report_path.read_text(encoding="utf-8")
        title = _first_heading(text) or report_path.parent.name
        digest = _report_dedupe_key(title, text)
        generated_at = _run_generated_at(report_path)
        report = reports_by_digest.get(digest)
        if not report:
            reports_by_digest[digest] = {
                "path": str(report_path),
                "title": title,
                "summary": _report_summary(text, report_path),
                "generatedAt": generated_at,
                "runCount": 1,
            }
            continue
        report["runCount"] = int(report.get("runCount") or 1) + 1
        if generated_at >= str(report.get("generatedAt") or ""):
            report["path"] = str(report_path)
            report["generatedAt"] = generated_at
            report["summary"] = _report_summary(text, report_path)
    reports = list(reports_by_digest.values())
    return sorted(reports, key=lambda item: str(item.get("generatedAt") or ""), reverse=True)


def _wiki_page_index(wiki_root: Path) -> list[dict[str, Any]]:
    pages = []
    for page in sorted((wiki_root / "wiki").rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        sensitivity = str(metadata.get("sensitivity") or "safe")
        if sensitivity == "local_only" or classify_sensitivity(text) == "local_only":
            continue
        pages.append(
            {
                "path": str(page),
                "title": _first_heading(text) or page.stem,
                "type": metadata.get("type") or "",
                "status": metadata.get("status") or metadata.get("lifecycle_status") or "",
                "sourceCount": _source_count(metadata),
                "tracks": metadata.get("tracks") or [],
                "tags": metadata.get("tags") or [],
            }
        )
    return pages


def _growth_index(wiki_root: Path) -> dict[str, list[dict[str, Any]]]:
    workspace = wiki_root.parent
    growth_state = read_growth_memory_state(wiki_root)
    return {
        "overview": _growth_overview(wiki_root),
        "tasks": _latest_run_tasks(workspace) or _typed_pages(wiki_root, "growth_task"),
        "diagnoses": _growth_state_records(growth_state["diagnoses"]),
        "maturity": _growth_state_records(growth_state["maturitySnapshots"]),
    }


def _growth_state_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": str(item.get("path") or ""),
            "title": str(item.get("title") or item.get("track") or item.get("id") or ""),
            "tracks": item.get("tracks") or [],
            "status": str(item.get("lifecycle_status") or item.get("evidence_status") or ""),
        }
        for item in items
    ]


def _growth_overview(wiki_root: Path) -> list[dict[str, Any]]:
    diagnoses = _growth_state_records(read_growth_memory_state(wiki_root)["diagnoses"])
    gaps = _knowledge_gap_index(wiki_root)
    items = []
    if diagnoses:
        items.append(
            {
                "title": "成长方向",
                "summary": f"当前有 {len(diagnoses)} 条成长诊断，建议先处理状态为 active 的方向。",
                "items": [diagnosis["title"] for diagnosis in diagnoses[:5]],
            }
        )
    if gaps:
        items.append(
            {
                "title": "知识缺口",
                "summary": f"当前有 {len(gaps)} 条知识缺口，可作为后续学习输入。",
                "items": [gap["title"] for gap in gaps[:5]],
            }
        )
    if not items:
        items.append({"title": "暂无成长概览", "summary": "运行 pga run 后会生成成长方向和任务。", "items": []})
    return items


def _latest_run_tasks(workspace: Path) -> list[dict[str, Any]]:
    runs_root = workspace / "runs"
    if not runs_root.exists():
        return []
    run_dirs = sorted((path for path in runs_root.iterdir() if path.is_dir()), reverse=True)
    for run_dir in run_dirs:
        tasks_path = run_dir / "growth-cycle" / "tasks.json"
        if not tasks_path.exists():
            continue
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        if isinstance(tasks, list):
            return [_task_to_dashboard_item(task, run_dir) for task in tasks if isinstance(task, dict)]
    return []


def _task_to_dashboard_item(task: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    return {
        "id": task.get("id"),
        "title": task.get("title") or "",
        "status": task.get("level") or "",
        "track": task.get("primary_track") or "",
        "tracks": [task.get("primary_track") or "", *(task.get("secondary_tracks") or [])],
        "summary": task.get("why_this_task") or "",
        "startHere": task.get("start_here") or [],
        "steps": task.get("steps") or [],
        "outputPath": task.get("output_path") or "",
        "outputExample": task.get("output_example") or "",
        "doneDefinition": task.get("done_definition") or [],
        "reviewQuestions": task.get("review_questions") or [],
        "glossary": task.get("glossary") or {},
        "timeBudgetMinutes": task.get("time_budget_minutes") or 0,
        "path": str(run_dir / "growth-cycle" / "tasks.json"),
    }


def _knowledge_gap_index(wiki_root: Path) -> list[dict[str, Any]]:
    return _typed_pages(wiki_root, "knowledge_gap")


def _typed_pages(wiki_root: Path, page_type: str) -> list[dict[str, Any]]:
    matches = []
    for page in sorted((wiki_root / "wiki").rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        if metadata.get("type") != page_type:
            continue
        matches.append({"path": str(page), "title": _first_heading(text) or page.stem, "tracks": metadata.get("tracks") or [], "status": metadata.get("status") or metadata.get("lifecycle_status") or ""})
    return matches


def _lint_issue_to_dict(issue: Any) -> dict[str, str]:
    return {
        "id": issue.id,
        "severity": issue.severity,
        "pagePath": issue.page_path,
        "type": issue.type,
        "message": issue.message,
        "suggestedFix": issue.suggested_fix,
    }


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, Any] = {}
    current_list: str | None = None
    for raw_line in parts[1].splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_list:
            metadata.setdefault(current_list, []).append(line[4:])
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_list = None
        if value == "":
            metadata[key] = []
            current_list = key
        else:
            metadata[key] = value
    return metadata


def _source_count(metadata: dict[str, Any]) -> int:
    count = 0
    for key in ("source_evidence_ids", "source_raw_ids", "source_paths"):
        value = metadata.get(key)
        if isinstance(value, list):
            count += len(value)
    return count


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""


def _safe_snippet(text: str) -> str:
    cleaned = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.startswith("---"))
    return cleaned[:240]


def _normalize_report_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _report_dedupe_key(title: str, text: str) -> str:
    if title == "本轮成长任务包":
        return f"task-package:{title}"
    return sha256_text(_normalize_report_text(text))


def _run_generated_at(report_path: Path) -> str:
    run_name = report_path.parent.name
    if run_name == "current":
        return utc_now_iso()
    return run_name


def _report_summary(text: str, report_path: Path) -> str:
    if _first_heading(text) == "本轮成长任务包":
        return f"成长任务包报告，生成批次：{report_path.parent.name}"
    return _safe_snippet(text)


def _dashboard_html(data: dict[str, Any]) -> str:
    inline_data = json.dumps(data, ensure_ascii=False)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '  <meta charset="utf-8">',
            "  <title>Personal Growth Dashboard</title>",
            '  <link rel="stylesheet" href="assets/dashboard.css">',
            "</head>",
            "<body>",
            "  <main>",
            "    <header>",
            "      <h1>Personal Growth Dashboard</h1>",
            "      <p id=\"meta\"></p>",
            "    </header>",
            "    <nav id=\"tabs\"></nav>",
            "    <section id=\"content\"></section>",
            "  </main>",
            f'  <script id="dashboard-data" type="application/json">{inline_data}</script>',
            '  <script src="assets/dashboard.js"></script>',
            "</body>",
            "</html>",
            "",
        ]
    )


def _dashboard_css() -> str:
    return "\n".join(
        [
            "body { margin: 0; font-family: Arial, sans-serif; background: #f7f7f4; color: #1f2933; }",
            "main { max-width: 1180px; margin: 0 auto; padding: 32px; }",
            "header { border-bottom: 1px solid #d9ded6; margin-bottom: 20px; }",
            "h1 { font-size: 28px; margin: 0 0 8px; }",
            "nav { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }",
            "button { border: 1px solid #b8c0b2; background: #ffffff; padding: 8px 12px; border-radius: 6px; cursor: pointer; }",
            "button.active { background: #284b3f; color: #ffffff; }",
            ".grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }",
            ".card { background: #ffffff; border: 1px solid #d9ded6; border-radius: 8px; padding: 14px; }",
            ".card h3 { font-size: 16px; margin: 0 0 8px; }",
            ".task-list { display: grid; gap: 16px; }",
            ".task-card h4 { margin: 14px 0 6px; font-size: 14px; }",
            ".task-card ul { margin: 0; padding-left: 20px; }",
            ".task-card li { margin: 4px 0; }",
            ".muted { color: #667085; font-size: 13px; }",
            "code { word-break: break-all; }",
        ]
    )


def _dashboard_js() -> str:
    return "\n".join(
        [
            "const views = [{id:'overview',label:'概览'},{id:'reports',label:'报告'},{id:'wiki',label:'维基'},{id:'growth',label:'成长'},{id:'tasks',label:'任务'},{id:'gaps',label:'差距'}];",
            "let dashboardData = null;",
            "const embedded = document.getElementById('dashboard-data');",
            "if (embedded && embedded.textContent) { dashboardData = JSON.parse(embedded.textContent); renderTabs(); render('overview'); } else { fetch('data/dashboard-data.json').then(r => r.json()).then(data => { dashboardData = data; renderTabs(); render('overview'); }).catch(err => { document.getElementById('content').textContent = 'Unable to load dashboard data: ' + err; }); }",
            "function renderTabs(){ const tabs = document.getElementById('tabs'); tabs.innerHTML = ''; views.forEach(view => { const b = document.createElement('button'); b.textContent = view.label; b.onclick = () => render(view.id); b.id = 'tab-' + view.id; tabs.appendChild(b); }); }",
            "function render(view){ views.forEach(item => { const el = document.getElementById('tab-' + item.id); if (el) el.className = item.id === view ? 'active' : ''; }); document.getElementById('meta').textContent = dashboardData.builtAt + ' · ' + dashboardData.wikiRoot; const c = document.getElementById('content'); c.innerHTML = ''; if(view === 'overview') return cards(c, [{title:'报告',summary:String(dashboardData.reports.length)},{title:'维基页面',summary:String(dashboardData.wikiPages.length)},{title:'成长方向',summary:String((dashboardData.growth.diagnoses || []).length)},{title:'待做任务',summary:String((dashboardData.growth.tasks || []).length)}]); if(view === 'reports') return cards(c, dashboardData.reports); if(view === 'growth') return overviewCards(c, dashboardData.growth.overview || dashboardData.growth.diagnoses || []); if(view === 'tasks') return taskCards(c, dashboardData.growth.tasks); if(view === 'wiki') return cards(c, dashboardData.wikiPages); if(view === 'gaps') return cards(c, dashboardData.knowledgeGaps); }",
            "function cards(root, items){ const grid = document.createElement('div'); grid.className = 'grid'; items.forEach(item => { const card = document.createElement('article'); card.className = 'card'; const title = item.title || item.type || 'Item'; card.innerHTML = '<h3></h3><p class=\"muted\"></p><code></code>'; card.querySelector('h3').textContent = item.runCount && item.runCount > 1 ? title + '（重复运行 ' + item.runCount + ' 次）' : title; card.querySelector('p').textContent = item.summary || item.status || JSON.stringify(item); card.querySelector('code').textContent = item.path || item.generatedAt || ''; grid.appendChild(card); }); root.appendChild(grid); }",
            "function overviewCards(root, items){ const grid = document.createElement('div'); grid.className = 'grid'; items.forEach(item => { const card = document.createElement('article'); card.className = 'card'; card.appendChild(heading(item.title || '成长概览')); const p = document.createElement('p'); p.className = 'muted'; p.textContent = item.summary || item.status || ''; card.appendChild(p); if (item.items) card.appendChild(section('相关内容', item.items)); grid.appendChild(card); }); root.appendChild(grid); }",
            "function taskCards(root, items){ const list = document.createElement('div'); list.className = 'task-list'; items.forEach(item => { const card = document.createElement('article'); card.className = 'card task-card'; card.appendChild(heading(item.title || '成长任务')); card.appendChild(meta('目标轨道', item.track || '')); card.appendChild(meta('时间预算', String(item.timeBudgetMinutes || '') + ' 分钟')); card.appendChild(section('为什么推荐给你', [item.summary || ''])); card.appendChild(section('从哪里开始', item.startHere || [])); card.appendChild(section('具体步骤', item.steps || [])); card.appendChild(section('结果写到哪里', [item.outputPath || ''])); card.appendChild(section('结果长什么样', [item.outputExample || ''])); card.appendChild(section('完成标准', item.doneDefinition || [])); card.appendChild(section('术语解释', glossaryLines(item.glossary || {}))); list.appendChild(card); }); root.appendChild(list); }",
            "function heading(text){ const el = document.createElement('h3'); el.textContent = text; return el; }",
            "function meta(label, value){ const el = document.createElement('p'); el.className = 'muted'; el.textContent = value ? label + '：' + value : label; return el; }",
            "function section(title, values){ const wrap = document.createElement('section'); const h = document.createElement('h4'); h.textContent = title; wrap.appendChild(h); const list = document.createElement('ul'); values.filter(Boolean).forEach(value => { const li = document.createElement('li'); li.textContent = value; list.appendChild(li); }); wrap.appendChild(list); return wrap; }",
            "function glossaryLines(glossary){ return Object.keys(glossary).map(key => key + '：' + glossary[key]); }",
        ]
    )
