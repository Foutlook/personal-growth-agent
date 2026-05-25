#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import uuid4


VALID_STAGES = {"L1", "L2", "L3", "L4"}

SECRET_RE = re.compile(r"(?i)(sk-[a-z0-9_-]+|token\s*=\s*[^ \n]+|api[_-]?key\s*=\s*[^ \n]+)")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://[^\s)]+")
PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")
PRIVATE_KEY_RE = re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")


@dataclass
class WriteResult:
    target_path: str
    path: Path
    operation: str
    source_raw_ids: list[str]
    content_hash: str


@dataclass
class HistoryMessage:
    role: str
    content: str
    timestamp: str


@dataclass
class HistorySession:
    source: str
    session_id: str
    started_at: str
    title: str
    messages: list[HistoryMessage]
    path: Path
    content_hash: str


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Growth Knowledge Hub local writer and recall helper")
    parser.add_argument("--home", type=Path, default=None, help="Override data home. Defaults to GKH_HOME or ~/.growth-knowledge-hub.")
    parser.add_argument("--scope", choices=["user", "project"], default="user", help="Use user-level or project-local data home.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--input", required=True, type=Path)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--input", required=True, type=Path)

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("--input", required=True, type=Path)

    project_parser = subparsers.add_parser("project")
    project_parser.add_argument("--input", required=True, type=Path)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=10)

    read_parser = subparsers.add_parser("read")
    read_parser.add_argument("--path", required=True)

    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("--query", required=True)
    context_parser.add_argument("--limit", type=int, default=5)

    scan_parser = subparsers.add_parser("scan-iterations")
    scan_parser.add_argument("--repo", type=Path, default=None, help="Single project repository path.")
    scan_parser.add_argument("--dir", type=Path, default=None, help="Directory containing multiple project repositories.")
    scan_parser.add_argument("--branch-prefix", default="release", help="Branch name prefix to scan (default: release).")
    scan_parser.add_argument("--output", choices=["stdout", "wiki"], default="stdout", help="Output target.")

    history_parser = subparsers.add_parser("analyze-history")
    history_parser.add_argument("--source", choices=["codex", "claude", "opencode", "all"], required=True)
    history_parser.add_argument("--source-dir", type=Path, default=None)
    history_parser.add_argument("--source-map", action="append", default=[])
    history_parser.add_argument("--since", default="")
    history_parser.add_argument("--until", default="")
    history_parser.add_argument("--limit", type=int, default=50)
    history_parser.add_argument("--dry-run", action="store_true")
    history_parser.add_argument("--output", choices=["stdout", "json", "wiki"], default="stdout")

    gen_tasks_parser = subparsers.add_parser("generate-tasks")
    gen_tasks_parser.add_argument("--input", required=True, type=Path)

    subparsers.add_parser("index")
    subparsers.add_parser("dashboard")

    args = parser.parse_args(argv)
    try:
        home = resolve_home(args.home, args.scope)
        wiki_root = home / "llm-wiki"
        if args.command == "init":
            init_wiki(wiki_root)
            return print_json({"status": "ok", "home": str(home), "wiki": str(wiki_root)})
        if args.command == "capture":
            result = write_capture(wiki_root, read_input(args.input))
            return print_json(result)
        if args.command == "ingest":
            result = write_material(wiki_root, read_input(args.input))
            return print_json(result)
        if args.command == "review":
            result = write_review(wiki_root, read_input(args.input))
            return print_json(result)
        if args.command == "project":
            result = write_project(root=wiki_root, data=read_input(args.input))
            return print_json(result)
        if args.command == "search":
            result = search_wiki(wiki_root, args.query, args.limit)
            return print_json({"status": "ok", "items": result})
        if args.command == "read":
            result = read_page(wiki_root, args.path)
            return print_json({"status": "ok", "page": result})
        if args.command == "context":
            result = context_pack(wiki_root, args.query, args.limit)
            return print_json({"status": "ok", "query": args.query, "items": result})
        if args.command == "index":
            index = rebuild_index(wiki_root)
            return print_json({"status": "ok", "indexPath": str(wiki_root / "data" / "index.json"), "count": len(index)})
        if args.command == "scan-iterations":
            result = scan_iterations_command(args.repo, args.dir, args.branch_prefix, args.output, wiki_root)
            return print_json(result)
        if args.command == "analyze-history":
            result = analyze_history_command(
                args.source,
                args.source_dir,
                args.source_map,
                args.since,
                args.until,
                args.limit,
                args.dry_run,
                args.output,
                wiki_root,
            )
            return print_json(result)
        if args.command == "generate-tasks":
            result = write_generate_tasks(wiki_root, read_input(args.input))
            return print_json(result)
        if args.command == "dashboard":
            result = build_dashboard(home, wiki_root)
            return print_json(result)
    except Exception as exc:
        print_json({"status": "error", "error": str(exc)}, stream=sys.stderr)
        return 1
    print_json({"status": "error", "error": f"unsupported command: {args.command}"}, stream=sys.stderr)
    return 1


def resolve_home(explicit_home: Path | None, scope: str) -> Path:
    if explicit_home is not None:
        return explicit_home.expanduser().resolve()
    env_home = os.environ.get("GKH_HOME")
    if env_home:
        return Path(env_home).expanduser().resolve()
    if scope == "project":
        project_home = find_project_home(Path.cwd())
        if project_home is not None:
            return project_home.resolve()
        return (Path.cwd() / ".growth-knowledge").resolve()
    return (Path.home() / ".growth-knowledge-hub").resolve()


def find_project_home(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        marker = candidate / ".growth-knowledge"
        if marker.exists():
            return marker
    return None


def read_input(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def print_json(value: dict[str, Any], stream=None) -> int:
    output = stream or sys.stdout
    output.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    return 0


def init_wiki(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(parents=True, exist_ok=True)
    write_if_missing(root / "AGENTS.md", "# Growth Knowledge Hub\n\n本地成长知识库，供 AI CLI skill 读写。\n")
    write_if_missing(root / "SCHEMA.md", "# LLM Wiki Schema\n\n所有 Wiki 页面必须包含 frontmatter、来源和写入日志。\n")


def write_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_capture(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    init_wiki(root)
    title = required_text(data, "title")
    summary = string_list(data, "summary")
    decisions = string_list(data, "decisions")
    insights = string_list(data, "insights")
    open_questions = string_list(data, "open_questions", required=False)
    next_actions = string_list(data, "next_actions")
    tags = string_list(data, "tags", required=False)
    tracks = string_list(data, "growth_tracks", required=False)
    growth_tasks = _parse_growth_tasks(data)
    source_text = "\n".join(summary + decisions + insights + open_questions + next_actions)
    safe_text, sensitivity, findings = redact_or_reject(source_text)
    summary = redact_items(summary)
    decisions = redact_items(decisions)
    insights = redact_items(insights)
    open_questions = redact_items(open_questions)
    next_actions = redact_items(next_actions)
    raw_source = write_raw(
        root,
        "conversation_capture",
        "conversations",
        title,
        data.get("captured_from") or "current_conversation",
        safe_text,
        sensitivity,
        tags,
    )
    body = frontmatter(
        {
            "type": "growth_capture",
            "status": "ready",
            "source_raw_ids": [raw_source["rawSourceId"]],
            "captured_date": now_iso(),
            "sensitivity": sensitivity,
            "evidence_status": "Inferred",
            "tracks": tracks,
            "tags": tags,
        }
    )
    body += f"\n# {title}\n\n"
    body += section("摘要", summary)
    body += section("关键决策", decisions)
    body += section("洞察", insights)
    body += section("未决问题", open_questions)
    body += section("下一步", next_actions)
    body += "\n## 来源\n"
    body += f"- {raw_source['rawSourceId']}: {raw_source['path']}\n"
    write = write_wiki_page(root, f"wiki/growth/reviews/{slug(title)}.md", body, [raw_source["rawSourceId"]])
    task_writes = _write_growth_tasks(root, growth_tasks, title, tags, [raw_source["rawSourceId"]])
    rebuild_index(root)
    writes = [write_to_dict(write), *task_writes]
    return {"status": "ok", "kind": "capture", "rawSource": raw_source, "writes": writes, "redactions": findings}


def _parse_growth_tasks(data: dict[str, Any]) -> list[dict[str, str]]:
    raw = data.get("growth_tasks")
    if not raw or not isinstance(raw, list):
        return []
    tasks: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("each growth_task must be an object")
        title = str(item.get("title") or "").strip()
        if not title:
            raise ValueError("growth_task.title is required")
        stage = str(item.get("stage") or "").strip()
        if stage and stage not in VALID_STAGES:
            raise ValueError(f"growth_task.stage must be one of {sorted(VALID_STAGES)}, got: {stage}")
        tasks.append({
            "title": title,
            "stage": stage,
            "done_definition": str(item.get("done_definition") or "").strip(),
            "rationale": str(item.get("rationale") or "").strip(),
        })
    return tasks


def _write_growth_tasks(
    root: Path,
    tasks: list[dict[str, str]],
    source_title: str,
    tags: list[str],
    source_raw_ids: list[str],
) -> list[dict[str, Any]]:
    writes: list[dict[str, Any]] = []
    for task in tasks:
        result = write_task_page(
            root,
            task["title"],
            task["stage"],
            task["done_definition"],
            task["rationale"],
            source_title,
            tags,
            source_raw_ids,
        )
        writes.append(result if isinstance(result, dict) else write_to_dict(result))
    return writes


def write_generate_tasks(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    init_wiki(root)
    source = str(data.get("source") or "manual").strip()
    tasks = _parse_growth_tasks(data)
    if not tasks:
        raise ValueError("growth_tasks list is required and must not be empty")
    source_title = f"任务生成：{source}"
    tags = [source, "auto_generated"]
    task_writes = _write_growth_tasks(root, tasks, source_title, tags, [])
    rebuild_index(root)
    return {"status": "ok", "kind": "generate_tasks", "source": source, "count": len(tasks), "writes": task_writes}


def write_material(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    init_wiki(root)
    title = required_text(data, "title")
    source_type = str(data.get("source_type") or "external_material")
    source_locator = str(data.get("source_locator") or "")
    summary_points = cap_points(string_list(data, "summary_points"))
    key_concepts = string_list(data, "key_concepts", required=False)
    application_ideas = string_list(data, "application_ideas", required=False)
    open_questions = string_list(data, "open_questions", required=False)
    tags = string_list(data, "tags", required=False)
    why_it_matters = str(data.get("why_it_matters") or "")
    source_text = "\n".join(summary_points + key_concepts + application_ideas + open_questions + [why_it_matters])
    safe_text, sensitivity, findings = redact_or_reject(source_text)
    summary_points = redact_items(summary_points)
    key_concepts = redact_items(key_concepts)
    application_ideas = redact_items(application_ideas)
    open_questions = redact_items(open_questions)
    why_it_matters = redact_inline(why_it_matters)
    raw_source = write_raw(root, source_type, "materials", title, source_locator or title, safe_text, sensitivity, tags)
    page_type = "external_skill_summary" if "external" in source_type else "knowledge_page"
    folder = "external-summaries" if page_type == "external_skill_summary" else "concepts"
    body = frontmatter(
        {
            "type": page_type,
            "status": "ready",
            "source_raw_ids": [raw_source["rawSourceId"]],
            "source_locator": source_locator,
            "summary_policy": "max_6_points",
            "full_content_policy": "fetch_on_demand",
            "retention": "long_lived",
            "captured_date": now_iso(),
            "sensitivity": sensitivity,
            "evidence_role": "learning_context",
            "tags": tags,
        }
    )
    body += f"\n# {title}\n\n"
    body += section("摘要", summary_points)
    body += section("关键概念", key_concepts)
    body += text_section("为什么重要", why_it_matters)
    body += section("应用想法", application_ideas)
    body += section("未决问题", open_questions)
    body += "\n## 来源\n"
    body += f"- Locator: {source_locator or title}\n"
    body += f"- Raw source: {raw_source['rawSourceId']}\n"
    write = write_wiki_page(root, f"wiki/knowledge/{folder}/{slug(title)}.md", body, [raw_source["rawSourceId"]])
    gap_write = None
    if open_questions:
        gap_write = write_gap_page(root, title, open_questions, tags, [raw_source["rawSourceId"]])
    rebuild_index(root)
    writes = [write_to_dict(write)]
    if gap_write is not None:
        writes.append(write_to_dict(gap_write))
    return {"status": "ok", "kind": "material", "rawSource": raw_source, "writes": writes, "redactions": findings}


def write_review(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    init_wiki(root)
    title = required_text(data, "title")
    period = str(data.get("period") or "")
    observations = string_list(data, "observations")
    progress = string_list(data, "progress", required=False)
    bottlenecks = string_list(data, "bottlenecks", required=False)
    knowledge_gaps = string_list(data, "knowledge_gaps", required=False)
    next_tasks = string_list(data, "next_tasks", required=False)
    related_pages = string_list(data, "related_pages", required=False)
    tags = string_list(data, "tags", required=False)
    source_text = "\n".join(observations + progress + bottlenecks + knowledge_gaps + next_tasks)
    safe_text, sensitivity, findings = redact_or_reject(source_text)
    observations = redact_items(observations)
    progress = redact_items(progress)
    bottlenecks = redact_items(bottlenecks)
    knowledge_gaps = redact_items(knowledge_gaps)
    next_tasks = redact_items(next_tasks)
    raw_source = write_raw(root, "growth_review", "reviews", title, period or title, safe_text, sensitivity, tags)
    body = frontmatter(
        {
            "type": "growth_review",
            "status": "ready",
            "source_raw_ids": [raw_source["rawSourceId"]],
            "period": period,
            "captured_date": now_iso(),
            "sensitivity": sensitivity,
            "evidence_status": "Inferred",
            "tags": tags,
            "related": related_pages,
        }
    )
    body += f"\n# {title}\n\n"
    body += text_section("周期", period)
    body += section("观察", observations)
    body += section("进展", progress)
    body += section("瓶颈", bottlenecks)
    body += section("知识缺口", knowledge_gaps)
    body += section("下一步任务", next_tasks)
    body += section("相关页面", related_pages)
    write = write_wiki_page(root, f"wiki/growth/reviews/{slug(title)}.md", body, [raw_source["rawSourceId"]])
    task_writes = []
    for task in next_tasks:
        result = write_task_page(root, task, "", "", "", title, tags, [raw_source["rawSourceId"]])
        task_writes.append(result if isinstance(result, dict) else write_to_dict(result))
    rebuild_index(root)
    writes = [write_to_dict(write), *task_writes]
    return {"status": "ok", "kind": "review", "rawSource": raw_source, "writes": writes, "redactions": findings}


def write_project(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    init_wiki(root)
    project = required_text(data, "project")
    title = required_text(data, "title")
    summary = string_list(data, "summary")
    architecture = string_list(data, "architecture", required=False)
    decisions = string_list(data, "decisions", required=False)
    lessons = string_list(data, "lessons", required=False)
    risks = string_list(data, "risks", required=False)
    next_actions = string_list(data, "next_actions", required=False)
    source_paths = string_list(data, "source_paths", required=False)
    tags = string_list(data, "tags", required=False)
    source_text = "\n".join(summary + architecture + decisions + lessons + risks + next_actions + source_paths)
    safe_text, sensitivity, findings = redact_or_reject(source_text)
    summary = redact_items(summary)
    architecture = redact_items(architecture)
    decisions = redact_items(decisions)
    lessons = redact_items(lessons)
    risks = redact_items(risks)
    next_actions = redact_items(next_actions)
    source_paths = redact_items(source_paths)
    project_slug = slug(project)
    raw_source = write_raw(
        root,
        "project_analysis",
        "projects",
        title,
        project,
        safe_text,
        sensitivity,
        tags,
    )
    common_metadata = {
        "status": "ready",
        "project": project,
        "source_raw_ids": [raw_source["rawSourceId"]],
        "source_paths": source_paths,
        "captured_date": now_iso(),
        "sensitivity": sensitivity,
        "evidence_status": "host_generated",
        "tags": tags,
    }
    pages = [
        ("overview", "project_overview", title, [("摘要", summary), ("下一步", next_actions)]),
        ("architecture", "project_architecture", f"{project} 架构", [("架构", architecture)]),
        ("decisions", "project_decisions", f"{project} 决策", [("决策", decisions)]),
        ("lessons", "project_lessons", f"{project} 经验", [("经验", lessons)]),
        ("risks", "project_risks", f"{project} 风险", [("风险", risks)]),
    ]
    writes = []
    for page_name, page_type, page_title, sections in pages:
        body = frontmatter({"type": page_type, **common_metadata})
        body += f"\n# {page_title}\n\n"
        for section_title, section_items in sections:
            body += section(section_title, section_items)
        body += section("来源路径", source_paths)
        write = write_wiki_page(root, f"wiki/projects/{project_slug}/{page_name}.md", body, [raw_source["rawSourceId"]])
        writes.append(write)
    rebuild_index(root)
    return {"status": "ok", "kind": "project", "rawSource": raw_source, "writes": [write_to_dict(write) for write in writes], "redactions": findings}


def required_text(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not value:
        raise ValueError(f"missing required field: {key}")
    return value


def string_list(data: dict[str, Any], key: str, required: bool = True) -> list[str]:
    value = data.get(key)
    if value is None:
        if required:
            raise ValueError(f"missing required field: {key}")
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
    else:
        raise ValueError(f"{key} must be a string or list of strings")
    if required and not items:
        raise ValueError(f"missing required field: {key}")
    return items


def cap_points(items: list[str], limit: int = 6) -> list[str]:
    return [item[:500] for item in items[:limit]]


def redact_or_reject(text: str) -> tuple[str, str, list[dict[str, str]]]:
    if PRIVATE_KEY_RE.search(text):
        raise ValueError("local-only private key content detected")
    redacted = text
    findings: list[dict[str, str]] = []
    patterns = [
        ("secret", SECRET_RE, "[SECRET_REDACTED]"),
        ("email", EMAIL_RE, "[EMAIL_REDACTED]"),
        ("url", URL_RE, "[URL_REDACTED]"),
        ("phone", PHONE_RE, "[PHONE_REDACTED]"),
    ]
    for finding_type, pattern, replacement in patterns:
        matches = pattern.findall(redacted)
        if matches:
            findings.extend({"type": finding_type, "replacement": replacement} for _ in matches)
            redacted = pattern.sub(replacement, redacted)
    sensitivity = "redacted" if findings else "safe"
    return redacted, sensitivity, findings


def redact_items(items: list[str]) -> list[str]:
    return [redact_inline(item) for item in items]


def redact_inline(text: str) -> str:
    redacted, _sensitivity, _findings = redact_or_reject(text)
    return redacted


def write_raw(root: Path, source_type: str, folder: str, title: str, locator: str, content: str, sensitivity: str, tags: list[str]) -> dict[str, Any]:
    digest = sha256_text(f"{source_type}|{locator}|{title}|{content}")
    raw_id = stable_id("raw", digest)
    path = root / "raw" / folder / f"{raw_id}.md"
    if not path.exists():
        raw_body = frontmatter(
            {
                "title": title,
                "source_type": source_type,
                "original_location": locator,
                "captured_at": now_iso(),
                "sensitivity": sensitivity,
                "tags": tags,
            }
        )
        raw_body += "\n" + content + "\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw_body, encoding="utf-8")
    entry = {
        "sourceId": stable_id("src", raw_id, locator),
        "rawSourceId": raw_id,
        "originalLocation": locator,
        "ingestedAt": now_iso(),
        "capturedAt": now_iso(),
        "sourceType": source_type,
        "tool": "growth-knowledge-hub",
        "sensitivity": sensitivity,
        "redactionStatus": sensitivity,
        "hash": digest,
        "tags": tags,
        "path": str(path),
    }
    append_json_list(root / "data" / "source-manifest.json", entry)
    return entry


def write_wiki_page(root: Path, relative_path: str, body: str, source_raw_ids: list[str]) -> WriteResult:
    if is_sensitive(body):
        raise ValueError("unsafe content detected in wiki body")
    path = root / relative_path
    operation = "update" if path.exists() else "create"
    content = body if body.endswith("\n") else body + "\n"
    content_hash = sha256_text(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    result = WriteResult(relative_path, path, operation, source_raw_ids, content_hash)
    append_json_list(
        root / "data" / "wiki-write-log.json",
        {
            "id": stable_id("wiki_write", relative_path, content_hash),
            "targetPath": relative_path,
            "path": str(path),
            "operation": operation,
            "sourceRawIds": source_raw_ids,
            "sourceEvidenceIds": [],
            "compiler": "growth-knowledge-hub",
            "provider": "host_cli",
            "model": "",
            "contentHash": content_hash,
            "writtenAt": now_iso(),
        },
    )
    return result


def write_gap_page(root: Path, title: str, questions: list[str], tags: list[str], source_raw_ids: list[str]) -> WriteResult:
    body = frontmatter(
        {
            "type": "knowledge_gap",
            "status": "draft",
            "source_raw_ids": source_raw_ids,
            "captured_date": now_iso(),
            "sensitivity": "safe",
            "tags": tags,
        }
    )
    body += f"\n# 知识缺口：{title}\n\n"
    body += section("问题", questions)
    return write_wiki_page(root, f"wiki/knowledge/gaps/{slug(title)}.md", body, source_raw_ids)


def write_task_page(
    root: Path,
    task_title: str,
    stage: str,
    done_definition: str,
    rationale: str,
    source_title: str,
    tags: list[str],
    source_raw_ids: list[str],
) -> WriteResult | dict[str, str]:
    if stage and stage not in VALID_STAGES:
        raise ValueError(f"stage must be one of {sorted(VALID_STAGES)}, got: {stage}")
    short_title = task_title[:80]
    prefix = f"{stage}-" if stage else ""
    relative_path = f"wiki/growth/tasks/{prefix}{slug(short_title)}.md"
    existing_path = root / relative_path
    if existing_path.exists():
        existing_text = existing_path.read_text(encoding="utf-8")
        existing_meta = parse_frontmatter(existing_text)
        if existing_meta.get("status") == "active":
            return {"skipped": "duplicate_active", "path": relative_path}
    meta: dict[str, Any] = {
        "type": "growth_task",
        "status": "active",
        "source_raw_ids": source_raw_ids,
        "captured_date": now_iso(),
        "sensitivity": "safe",
        "tags": tags,
    }
    if stage:
        meta["stage"] = stage
    if done_definition:
        meta["done_definition"] = done_definition
    body = frontmatter(meta)
    body += f"\n# {short_title}\n\n"
    body += f"来源：{source_title}\n\n"
    if stage:
        body += f"## 阶段\n{stage}\n\n"
    if done_definition:
        body += f"## 完成定义\n{done_definition}\n\n"
    if rationale:
        body += f"## 生成依据\n{rationale}\n\n"
    return write_wiki_page(root, relative_path, body, source_raw_ids)


def frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def section(title: str, items: list[str]) -> str:
    lines = [f"## {title}"]
    if not items:
        lines.append("- 暂无")
    else:
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines) + "\n\n"


def text_section(title: str, value: str) -> str:
    return f"## {title}\n{value or '暂无'}\n\n"


def append_json_list(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with file_lock(lock_path):
        items: list[dict[str, Any]] = []
        if path.exists():
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, list):
                items = [item for item in value if isinstance(item, dict)]
        items.append(entry)
        temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        temp_path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(path)


@contextlib.contextmanager
def file_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    try:
        lock_handle(handle)
        yield
    finally:
        unlock_handle(handle)
        handle.close()


def lock_handle(handle) -> None:
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def unlock_handle(handle) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def rebuild_index(root: Path) -> list[dict[str, Any]]:
    init_wiki(root)
    pages = []
    wiki_root = root / "wiki"
    if wiki_root.exists():
        for path in sorted(wiki_root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            metadata = parse_frontmatter(text)
            if metadata.get("sensitivity") == "local_only" or "private key" in text.lower():
                continue
            rel = path.relative_to(root).as_posix()
            page = {
                "title": first_heading(text) or path.stem,
                "path": rel,
                "type": metadata.get("type") or "",
                "status": metadata.get("status") or "",
                "tags": parse_list_value(metadata.get("tags") or ""),
                "summary": summarize_page(text),
                "sourceRawIds": parse_list_value(metadata.get("source_raw_ids") or ""),
                "contentHash": sha256_text(text),
                "updatedAt": now_iso(),
            }
            pages.append(page)
    index_path = root / "data" / "index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def search_wiki(root: Path, query: str, limit: int) -> list[dict[str, Any]]:
    index = load_or_rebuild_index(root)
    terms = [term.lower() for term in re.split(r"\s+", query) if term.strip()]
    scored = []
    for item in index:
        haystack = " ".join(str(item.get(key) or "") for key in ("title", "type", "summary", "path")).lower()
        score = sum(2 if term in str(item.get("title", "")).lower() else 1 for term in terms if term in haystack)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], str(pair[1].get("path") or "")))
    return [compact_result(item, score) for score, item in scored[: max(0, limit)]]


def context_pack(root: Path, query: str, limit: int) -> list[dict[str, Any]]:
    results = search_wiki(root, query, limit)
    context_items = []
    for item in results:
        page = read_page(root, str(item.get("path") or ""))
        context_items.append(
            {
                "title": page.get("title"),
                "path": page.get("path"),
                "type": page.get("type"),
                "summary": item.get("summary"),
                "highlights": highlights(str(page.get("content") or ""), query),
                "tags": item.get("tags") or [],
                "sourceRawIds": page.get("sourceRawIds") or [],
            }
        )
    return context_items


def read_page(root: Path, requested_path: str) -> dict[str, Any]:
    path = safe_page_path(root, requested_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"page not found: {requested_path}")
    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    if metadata.get("sensitivity") == "local_only" or "private key" in text.lower():
        content = "[LOCAL_ONLY]"
    else:
        content, _sensitivity, _findings = redact_or_reject(strip_frontmatter(text))
    return {
        "title": first_heading(text) or path.stem,
        "path": path.relative_to(root).as_posix(),
        "type": metadata.get("type") or "",
        "status": metadata.get("status") or "",
        "sourceRawIds": parse_list_value(metadata.get("source_raw_ids") or ""),
        "content": content[:8000],
    }


def safe_page_path(root: Path, requested_path: str) -> Path:
    candidate = Path(requested_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        normalized = requested_path.replace("\\", "/")
        if normalized.startswith("llm-wiki/"):
            normalized = normalized.removeprefix("llm-wiki/")
        resolved = (root / normalized).resolve()
    root_resolved = root.resolve()
    if root_resolved not in [resolved, *resolved.parents]:
        raise ValueError("requested page escapes the local wiki")
    return resolved


def load_or_rebuild_index(root: Path) -> list[dict[str, Any]]:
    index_path = root / "data" / "index.json"
    if not index_path.exists():
        return rebuild_index(root)
    value = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        return rebuild_index(root)
    return [item for item in value if isinstance(item, dict)]


def build_dashboard(home: Path, root: Path) -> dict[str, Any]:
    index = rebuild_index(root)
    dashboard_root = home / "dashboard"
    dashboard_root.mkdir(parents=True, exist_ok=True)
    entry = dashboard_root / "index.html"
    cards = []
    for item in index:
        cards.append(
            "<article><h2>{}</h2><p>{}</p><code>{}</code></article>".format(
                html.escape(str(item.get("title") or "")),
                html.escape(str(item.get("summary") or "")),
                html.escape(str(item.get("path") or "")),
            )
        )
    body = "\n".join(cards) or "<p>No pages yet.</p>"
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<title>Growth Knowledge Hub</title>
<style>
body{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:32px;line-height:1.5;background:#f7f7f5;color:#1f2933}}
main{{max-width:960px;margin:auto}}
article{{background:white;border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0}}
h1{{font-size:28px}} h2{{font-size:18px}} code{{color:#52606d}}
</style>
<main>
<h1>Growth Knowledge Hub</h1>
<p>Built at: {html.escape(now_iso())}</p>
{body}
</main>
</html>
"""
    entry.write_text(html_text, encoding="utf-8")
    return {"status": "ok", "entryPath": str(entry), "pageCount": len(index)}


# ---------------------------------------------------------------------------
# analyze-history
# ---------------------------------------------------------------------------

HISTORY_SOURCES = ("codex", "claude", "opencode")


def analyze_history_command(
    source: str,
    source_dir: Path | None,
    source_maps: list[str],
    since: str,
    until: str,
    limit: int,
    dry_run: bool,
    output: str,
    wiki_root: Path,
) -> dict[str, Any]:
    source_map = parse_source_maps(source_maps)
    selected_sources = list(HISTORY_SOURCES) if source == "all" else [source]
    validate_history_args(source, source_dir, source_map, limit)
    since_date = parse_date_filter(since, "since")
    until_date = parse_date_filter(until, "until")
    warnings: list[str] = []
    sessions: list[HistorySession] = []
    source_results: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for item_source in selected_sources:
        resolved_dir = resolve_history_source_dir(item_source, source, source_dir, source_map, warnings)
        if resolved_dir is None:
            source_results.append({"source": item_source, "path": "", "analyzed": 0, "warnings": ["source directory not found"]})
            continue
        parsed_sessions = parse_history_source(item_source, resolved_dir, warnings)
        filtered_sessions = filter_history_sessions(parsed_sessions, since_date, until_date)
        accepted: list[HistorySession] = []
        for session in filtered_sessions:
            if session.content_hash in seen_hashes:
                warnings.append(f"{item_source}: duplicate session skipped: {session.path}")
                continue
            seen_hashes.add(session.content_hash)
            accepted.append(session)
            if len(sessions) + len(accepted) >= max(0, limit):
                break
        sessions.extend(accepted)
        source_results.append({"source": item_source, "path": str(resolved_dir), "analyzed": len(accepted), "warnings": []})
        if len(sessions) >= max(0, limit):
            break
    analyzed_items = [compact_history_session(session) for session in sessions]
    result: dict[str, Any] = {
        "status": "ok",
        "kind": "history_analysis",
        "dryRun": dry_run,
        "output": output,
        "analyzed": len(analyzed_items),
        "sources": source_results,
        "sessions": analyzed_items,
        "warnings": warnings,
    }
    if output == "wiki" and not dry_run:
        writes = write_history_to_wiki(wiki_root, sessions)
        result["writes"] = [write_to_dict(write) for write in writes]
    return result


def validate_history_args(source: str, source_dir: Path | None, source_map: dict[str, Path], limit: int) -> None:
    if source == "all" and source_dir is not None:
        raise ValueError("--source all cannot use --source-dir; use repeated --source-map source=path entries")
    if limit < 0:
        raise ValueError("--limit must be non-negative")
    for key in source_map:
        if key not in HISTORY_SOURCES:
            raise ValueError(f"unknown source in --source-map: {key}")


def parse_source_maps(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--source-map must use source=path")
        key, raw_path = value.split("=", 1)
        source = key.strip().lower()
        if source not in HISTORY_SOURCES:
            raise ValueError(f"unknown source in --source-map: {source}")
        result[source] = Path(raw_path).expanduser().resolve()
    return result


def parse_date_filter(value: str, label: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"--{label} must use YYYY-MM-DD") from exc


def resolve_history_source_dir(
    item_source: str,
    requested_source: str,
    source_dir: Path | None,
    source_map: dict[str, Path],
    warnings: list[str],
) -> Path | None:
    if item_source in source_map:
        mapped = source_map[item_source]
        if mapped.is_dir():
            return mapped
        warnings.append(f"{item_source}: mapped source directory not found: {mapped}")
        return None
    if requested_source != "all" and source_dir is not None:
        resolved = source_dir.expanduser().resolve()
        if resolved.is_dir():
            return resolved
        raise ValueError(f"source directory not found: {resolved}")
    discovered = discover_history_source_dir(item_source)
    if discovered is not None:
        return discovered
    warnings.append(f"{item_source}: source directory not found; provide --source-dir or --source-map")
    return None


def discover_history_source_dir(source: str) -> Path | None:
    home = Path.home()
    candidates: list[Path] = []
    if source == "codex":
        candidates = [home / ".codex" / "sessions", home / ".codex" / "history"]
    elif source == "claude":
        candidates = [home / ".claude" / "projects", home / ".claude" / "sessions"]
    elif source == "opencode":
        candidates = [
            home / ".opencode" / "sessions",
            home / "AppData" / "Local" / "opencode",
            home / ".local" / "share" / "opencode",
        ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return None


def parse_history_source(source: str, source_dir: Path, warnings: list[str]) -> list[HistorySession]:
    sessions: list[HistorySession] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        try:
            session = parse_history_file(source, path)
        except Exception as exc:
            warnings.append(f"{source}: skipped {path}: {exc}")
            continue
        if session is None:
            warnings.append(f"{source}: skipped unsupported file: {path}")
            continue
        if contains_private_key(session):
            warnings.append(f"{source}: skipped private key session: {path}")
            continue
        sessions.append(session)
    sessions.sort(key=lambda item: item.started_at or "")
    return sessions


def parse_history_file(source: str, path: Path) -> HistorySession | None:
    if path.suffix.lower() == ".jsonl":
        messages = parse_jsonl_messages(path)
        return make_history_session(source, path, "", messages)
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        messages = parse_json_messages(value)
        session_id = str(value.get("session_id") or value.get("id") or "")
        return make_history_session(source, path, session_id, messages, value)
    if isinstance(value, list):
        messages = parse_message_list(value)
        return make_history_session(source, path, "", messages)
    return None


def parse_jsonl_messages(path: Path) -> list[HistoryMessage]:
    messages: list[HistoryMessage] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            message = history_message_from_dict(value)
            if message is not None:
                messages.append(message)
    return messages


def parse_json_messages(value: dict[str, Any]) -> list[HistoryMessage]:
    for key in ("messages", "conversation", "turns"):
        raw_messages = value.get(key)
        if isinstance(raw_messages, list):
            return parse_message_list(raw_messages)
    return []


def parse_message_list(values: list[Any]) -> list[HistoryMessage]:
    messages: list[HistoryMessage] = []
    for value in values:
        if isinstance(value, dict):
            message = history_message_from_dict(value)
            if message is not None:
                messages.append(message)
    return messages


def history_message_from_dict(value: dict[str, Any]) -> HistoryMessage | None:
    role = str(value.get("role") or value.get("type") or value.get("speaker") or "").strip().lower()
    if role not in {"user", "assistant", "system", "tool"}:
        return None
    content_value = value.get("content")
    if content_value is None:
        content_value = value.get("text")
    content = stringify_history_content(content_value)
    if not content:
        return None
    timestamp = str(value.get("timestamp") or value.get("created_at") or value.get("time") or "").strip()
    return HistoryMessage(role=role, content=content, timestamp=timestamp)


def stringify_history_content(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [stringify_history_content(item) for item in value]
        return "\n".join(part for part in parts if part).strip()
    if isinstance(value, dict):
        for key in ("text", "content", "value"):
            if key in value:
                return stringify_history_content(value.get(key))
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def make_history_session(
    source: str,
    path: Path,
    session_id: str,
    messages: list[HistoryMessage],
    metadata: dict[str, Any] | None = None,
) -> HistorySession | None:
    if not messages:
        return None
    metadata = metadata or {}
    started_at = first_non_empty(
        str(metadata.get("created_at") or ""),
        str(metadata.get("timestamp") or ""),
        str(metadata.get("started_at") or ""),
        messages[0].timestamp,
    )
    title = first_non_empty(str(metadata.get("title") or ""), first_user_prompt(messages)[:80], path.stem)
    content_seed = "\n".join(f"{message.role}:{message.content}" for message in messages)
    digest = sha256_text(f"{source}|{path}|{started_at}|{content_seed}")
    stable_session_id = session_id or stable_id("session", source, started_at, digest)
    return HistorySession(
        source=source,
        session_id=stable_session_id,
        started_at=started_at,
        title=title,
        messages=messages,
        path=path,
        content_hash=digest,
    )


def first_non_empty(*values: str) -> str:
    for value in values:
        stripped = value.strip()
        if stripped:
            return stripped
    return ""


def contains_private_key(session: HistorySession) -> bool:
    text = "\n".join(message.content for message in session.messages)
    return bool(PRIVATE_KEY_RE.search(text))


def filter_history_sessions(
    sessions: list[HistorySession],
    since_date: datetime | None,
    until_date: datetime | None,
) -> list[HistorySession]:
    result: list[HistorySession] = []
    for session in sessions:
        session_date = parse_history_datetime(session.started_at)
        if since_date is not None and session_date is not None and session_date < since_date:
            continue
        if until_date is not None and session_date is not None and session_date > until_date:
            continue
        result.append(session)
    return result


def parse_history_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def compact_history_session(session: HistorySession) -> dict[str, Any]:
    snippets = redacted_history_snippets(session.messages)
    findings: list[dict[str, str]] = []
    redacted_prompt, _sensitivity, prompt_findings = redact_or_reject(first_user_prompt(session.messages))
    findings.extend(prompt_findings)
    return {
        "source": session.source,
        "sessionId": session.session_id,
        "startedAt": session.started_at,
        "title": redact_inline(session.title),
        "path": str(session.path),
        "messageCount": len(session.messages),
        "first_user_prompt": redacted_prompt[:300],
        "snippets": snippets,
        "keywords": history_keywords(session.messages),
        "contentHash": session.content_hash,
        "redactions": findings,
    }


def first_user_prompt(messages: list[HistoryMessage]) -> str:
    for message in messages:
        if message.role == "user":
            return message.content
    return messages[0].content if messages else ""


def redacted_history_snippets(messages: list[HistoryMessage]) -> list[str]:
    snippets: list[str] = []
    for message in messages:
        if message.role not in {"user", "assistant"}:
            continue
        snippet = redact_inline(message.content.replace("\n", " "))[:240]
        snippets.append(f"{message.role}: {snippet}")
        if len(snippets) == 3:
            break
    return snippets


def history_keywords(messages: list[HistoryMessage]) -> list[str]:
    text = " ".join(message.content for message in messages).lower()
    counts: dict[str, int] = {}
    for word in re.split(r"[\s,.;:!?()\[\]{}<>\"'`/\\|]+", text):
        cleaned = word.strip("-_")
        if len(cleaned) < 4 or cleaned in STOP_WORDS:
            continue
        counts[cleaned] = counts.get(cleaned, 0) + 1
    return [word for word, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:8]]


def write_history_to_wiki(root: Path, sessions: list[HistorySession]) -> list[WriteResult]:
    init_wiki(root)
    writes: list[WriteResult] = []
    by_source: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        item = compact_history_session(session)
        source_text = "\n".join(item["snippets"])
        safe_text, sensitivity, _findings = redact_or_reject(source_text)
        raw_source = write_raw(
            root,
            f"{session.source}_history_session",
            "conversations",
            str(item["title"]),
            str(session.path),
            safe_text,
            sensitivity,
            ["history", session.source],
        )
        item["rawSourceId"] = raw_source["rawSourceId"]
        by_source.setdefault(session.source, []).append(item)
    for source, items in sorted(by_source.items()):
        body = frontmatter(
            {
                "type": "history_analysis",
                "status": "ready",
                "source_raw_ids": [str(item.get("rawSourceId") or "") for item in items],
                "captured_date": now_iso(),
                "sensitivity": "safe",
                "tags": ["history", source],
            }
        )
        body += f"\n# {source} 历史会话分析\n\n"
        first_prompts = [str(item.get("first_user_prompt") or "") for item in items]
        summary_prompt = "；".join(prompt for prompt in first_prompts if prompt)[:500]
        body += f"摘要：共分析 {len(items)} 个历史会话。{summary_prompt}\n\n"
        for item in items:
            body += f"## {item['title']}\n"
            body += f"- Source: {item['source']}\n"
            body += f"- Started: {item['startedAt'] or 'unknown'}\n"
            body += f"- Session: {item['sessionId']}\n"
            body += f"- First user prompt: {item['first_user_prompt'] or '暂无'}\n"
            body += f"- Keywords: {', '.join(item['keywords']) or '暂无'}\n"
            body += "\n"
        write = write_wiki_page(root, f"wiki/history/{source}-history.md", body, [str(item.get("rawSourceId") or "") for item in items])
        writes.append(write)
    rebuild_index(root)
    return writes


def compact_result(item: dict[str, Any], score: int) -> dict[str, Any]:
    return {
        "title": item.get("title"),
        "path": item.get("path"),
        "type": item.get("type"),
        "summary": item.get("summary"),
        "tags": item.get("tags") or [],
        "sourceRawIds": item.get("sourceRawIds") or [],
        "score": score,
    }


def highlights(content: str, query: str) -> list[str]:
    terms = [term.lower() for term in re.split(r"\s+", query) if term.strip()]
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    matches = []
    for line in lines:
        lowered = line.lower()
        if any(term in lowered for term in terms):
            matches.append(line[:300])
        if len(matches) == 3:
            break
    return matches


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    current_key = ""
    list_values: dict[str, list[str]] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            list_values.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            metadata[current_key] = value.strip()
    for key, values in list_values.items():
        metadata[key] = "\n".join(values)
    return metadata


def parse_list_value(value: str) -> list[str]:
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    return parts[2].strip()


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""


def summarize_page(text: str) -> str:
    body = strip_frontmatter(text)
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "- 暂无":
            return stripped.removeprefix("- ").strip()[:280]
    return ""


def write_to_dict(result: WriteResult) -> dict[str, Any]:
    return {
        "targetPath": result.target_path,
        "path": str(result.path),
        "operation": result.operation,
        "sourceRawIds": result.source_raw_ids,
        "contentHash": result.content_hash,
    }


def is_sensitive(text: str) -> bool:
    return bool(PRIVATE_KEY_RE.search(text))


def slug(value: str) -> str:
    result = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "knowledge"


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(part) for part in parts)
    return f"{prefix}_{sha256_text(raw)[:16]}"


def sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# scan-iterations
# ---------------------------------------------------------------------------

CONVENTIONAL_RE = re.compile(r"^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+")
FIXUP_RE = re.compile(r"^(fixup|revert)[!:]?\s", re.IGNORECASE)
STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "can", "could", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "and", "but", "or", "nor",
    "not", "so", "very", "just", "about", "up", "this", "that", "these",
    "those", "it", "its", "add", "update", "remove", "new", "fix",
    "fixes", "updated", "added", "removed", "merged", "branch",
})


@dataclass(frozen=True)
class AuthorStats:
    name: str
    commits: int
    additions: int
    deletions: int


@dataclass(frozen=True)
class IterationRecord:
    branch: str
    date_label: str
    main_topics: str
    author_count: int
    additions: int
    deletions: int
    changed_files: int
    avg_files_per_commit: float
    stability: str
    conventionality: str
    authors: tuple[AuthorStats, ...]


def scan_iterations_command(
    repo: Path | None,
    scan_dir: Path | None,
    branch_prefix: str,
    output: str,
    wiki_root: Path,
) -> dict[str, Any]:
    if repo is None and scan_dir is None:
        raise ValueError("provide --repo or --dir")
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    repos = collect_repos(repo, scan_dir, warnings)
    for repo_path in repos:
        project_name = repo_path.name
        try:
            records = scan_single_repo(repo_path, branch_prefix, warnings)
        except Exception as exc:
            warnings.append(f"{project_name}: {exc}")
            continue
        if output == "wiki" and records:
            write_iterations_to_wiki(wiki_root, project_name, records)
        results.append({
            "project": project_name,
            "repo": str(repo_path),
            "iterations": [iteration_to_dict(r) for r in records],
        })
    return {"status": "ok", "projects": results, "warnings": warnings}


def collect_repos(repo: Path | None, scan_dir: Path | None, warnings: list[str]) -> list[Path]:
    if repo is not None:
        if not is_git_repo(repo):
            raise ValueError(f"not a git repository: {repo}")
        return [repo.resolve()]
    assert scan_dir is not None
    scan_dir = scan_dir.resolve()
    if not scan_dir.is_dir():
        raise ValueError(f"not a directory: {scan_dir}")
    repos = []
    for child in sorted(scan_dir.iterdir()):
        if child.is_dir() and is_git_repo(child):
            repos.append(child)
        elif child.is_dir():
            warnings.append(f"{child.name}: not a git repository, skipped")
    if not repos:
        raise ValueError(f"no git repositories found in {scan_dir}")
    return repos


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def scan_single_repo(repo_path: Path, prefix: str, warnings: list[str]) -> list[IterationRecord]:
    branches = discover_branches(repo_path, prefix, warnings)
    if not branches:
        warnings.append(f"{repo_path.name}: no {prefix}/* branches found")
        return []
    default_branch = find_default_branch(repo_path)
    records: list[IterationRecord] = []
    for i, branch in enumerate(branches):
        base = default_branch if i == 0 else branches[i - 1]
        record = build_iteration_record(repo_path, base, branch, prefix)
        records.append(record)
    return records


def discover_branches(repo_path: Path, prefix: str, warnings: list[str]) -> list[str]:
    # Return full ref as git expects it (e.g. "origin/release/20250601" or "release/20250601").
    # Try remote first, fall back to local.
    remote_output = git_cmd(repo_path, ["branch", "-r", "--list", f"origin/{prefix}/*"], check=False)
    raw_branches: list[str] = []
    for line in remote_output.splitlines():
        name = line.strip()
        if not name or "->" in name:
            continue
        raw_branches.append(name)
    if not raw_branches:
        local_output = git_cmd(repo_path, ["branch", "--list", f"{prefix}/*"], check=False)
        for line in local_output.splitlines():
            name = line.strip().lstrip("* ")
            if name:
                raw_branches.append(name)
    branches: list[str] = []
    for full_ref in raw_branches:
        short_name = full_ref.removeprefix("origin/")
        date_str = extract_date(short_name, prefix)
        if date_str is None:
            warnings.append(f"{repo_path.name}: branch '{short_name}' has no YYYYMMDD date, skipped")
            continue
        branches.append(full_ref)
    branches.sort(key=lambda b: extract_date(b.removeprefix("origin/"), prefix) or "")
    return branches


def extract_date(branch_name: str, prefix: str) -> str | None:
    suffix = branch_name.removeprefix(f"{prefix}/")
    match = re.search(r"(\d{8})", suffix)
    return match.group(1) if match else None


def find_default_branch(repo_path: Path) -> str:
    for candidate in ("main", "master"):
        result = git_cmd(repo_path, ["rev-parse", "--verify", candidate], check=False)
        if result:
            return candidate
    raise ValueError("no main or master branch found")


def build_iteration_record(repo_path: Path, base: str, branch: str, prefix: str) -> IterationRecord:
    short_branch = branch.removeprefix("origin/")
    date_str = extract_date(short_branch, prefix) or ""
    date_label = f"{date_str[4:6]}.{date_str[6:8]}" if len(date_str) == 8 else date_str
    diff_range = f"{base}..{branch}"
    stats = get_diff_stats(repo_path, diff_range)
    authors = get_author_stats(repo_path, diff_range)
    messages = get_commit_messages(repo_path, diff_range)
    changed_files_list = get_changed_files(repo_path, diff_range)
    main_topics = extract_topics(messages, changed_files_list)
    total_commits = sum(a.commits for a in authors)
    avg_files = round(stats["files"] / total_commits, 1) if total_commits > 0 else 0.0
    stability = rate_stability(messages)
    conventionality = rate_conventionality(messages)
    return IterationRecord(
        branch=short_branch,
        date_label=date_label,
        main_topics=main_topics,
        author_count=len(authors),
        additions=stats["additions"],
        deletions=stats["deletions"],
        changed_files=stats["files"],
        avg_files_per_commit=avg_files,
        stability=stability,
        conventionality=conventionality,
        authors=tuple(authors),
    )


def get_diff_stats(repo_path: Path, diff_range: str) -> dict[str, int]:
    output = git_cmd(repo_path, ["diff", "--shortstat", diff_range])
    additions = 0
    deletions = 0
    files = 0
    match = re.search(r"(\d+) files? changed", output)
    if match:
        files = int(match.group(1))
    match = re.search(r"(\d+) insertions?", output)
    if match:
        additions = int(match.group(1))
    match = re.search(r"(\d+) deletions?", output)
    if match:
        deletions = int(match.group(1))
    return {"additions": additions, "deletions": deletions, "files": files}


def get_author_stats(repo_path: Path, diff_range: str) -> list[AuthorStats]:
    output = git_cmd(repo_path, ["shortlog", "-sn", "--no-merges", diff_range])
    authors: list[AuthorStats] = []
    for line in output.splitlines():
        line = line.strip()
        match = re.match(r"(\d+)\s+(.+)", line)
        if match:
            commits = int(match.group(1))
            name = match.group(2).strip()
            authors.append(AuthorStats(name=name, commits=commits, additions=0, deletions=0))
    numstat = git_cmd(repo_path, ["log", "--numstat", "--format=Author: %an", "--no-merges", diff_range])
    author_lines: dict[str, tuple[int, int]] = {}
    current_author = ""
    for line in numstat.splitlines():
        if not line.strip():
            continue
        if line.startswith("Author:"):
            current_author = line.removeprefix("Author:").strip()
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            add = int(parts[0]) if parts[0] != "-" else 0
            dele = int(parts[1]) if parts[1] != "-" else 0
            prev = author_lines.get(current_author, (0, 0))
            author_lines[current_author] = (prev[0] + add, prev[1] + dele)
    result: list[AuthorStats] = []
    for author in authors:
        add, dele = author_lines.get(author.name, (0, 0))
        result.append(AuthorStats(name=author.name, commits=author.commits, additions=add, deletions=dele))
    return result


def get_commit_messages(repo_path: Path, diff_range: str) -> list[str]:
    output = git_cmd(repo_path, ["log", "--format=%s", "--no-merges", diff_range])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_changed_files(repo_path: Path, diff_range: str) -> list[str]:
    output = git_cmd(repo_path, ["diff", "--name-only", diff_range])
    return [line.strip() for line in output.splitlines() if line.strip()]


def extract_topics(messages: list[str], files: list[str]) -> str:
    word_freq: dict[str, int] = {}
    for msg in messages:
        for word in re.split(r"[\s\-_/]+", msg):
            w = word.lower().strip(".,;:!?()[]{}\"'")
            if len(w) >= 2 and w not in STOP_WORDS:
                word_freq[w] = word_freq.get(w, 0) + 1
    keywords = sorted(word_freq.items(), key=lambda x: -x[1])[:3]
    keyword_str = ", ".join(k for k, _ in keywords)
    dir_freq: dict[str, int] = {}
    for f in files:
        parts = Path(f).parts
        if len(parts) >= 2:
            dir_name = parts[0]
            dir_freq[dir_name] = dir_freq.get(dir_name, 0) + 1
    hot_dirs = sorted(dir_freq.items(), key=lambda x: -x[1])[:2]
    hot_str = ", ".join(d for d, _ in hot_dirs)
    parts = []
    if keyword_str:
        parts.append(keyword_str)
    if hot_str:
        parts.append(f"[{hot_str}]")
    return "; ".join(parts) or "-"


def rate_stability(messages: list[str]) -> str:
    if not messages:
        return "★★★"
    fixup_count = sum(1 for m in messages if FIXUP_RE.match(m))
    ratio = fixup_count / len(messages)
    if ratio < 0.05:
        return "★★★★★"
    if ratio < 0.10:
        return "★★★★"
    if ratio < 0.20:
        return "★★★"
    if ratio < 0.30:
        return "★★"
    return "★"


def rate_conventionality(messages: list[str]) -> str:
    if not messages:
        return "★★★"
    conv_count = sum(1 for m in messages if CONVENTIONAL_RE.match(m))
    ratio = conv_count / len(messages)
    if ratio >= 0.80:
        return "★★★★★"
    if ratio >= 0.60:
        return "★★★★"
    if ratio >= 0.40:
        return "★★★"
    if ratio >= 0.20:
        return "★★"
    return "★"


def iteration_to_dict(record: IterationRecord) -> dict[str, Any]:
    return {
        "branch": record.branch,
        "date_label": record.date_label,
        "main_topics": record.main_topics,
        "author_count": record.author_count,
        "additions": record.additions,
        "deletions": record.deletions,
        "changed_files": record.changed_files,
        "avg_files_per_commit": record.avg_files_per_commit,
        "stability": record.stability,
        "conventionality": record.conventionality,
        "authors": [{"name": a.name, "commits": a.commits, "additions": a.additions, "deletions": a.deletions} for a in record.authors],
    }


def write_iterations_to_wiki(wiki_root: Path, project_name: str, records: list[IterationRecord]) -> None:
    init_wiki(wiki_root)
    md = format_iterations_markdown(project_name, records)
    project_slug = slug(project_name)
    path = wiki_root / "wiki" / "projects" / project_slug / f"{project_slug}-迭代记录.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    append_json_list(
        wiki_root / "data" / "wiki-write-log.json",
        {
            "id": stable_id("wiki_write", str(path), sha256_text(md)),
            "targetPath": str(path.relative_to(wiki_root)),
            "path": str(path),
            "operation": "update" if path.exists() else "create",
            "sourceRawIds": [],
            "sourceEvidenceIds": [],
            "compiler": "growth-knowledge-hub",
            "provider": "host_cli",
            "model": "",
            "contentHash": sha256_text(md),
            "writtenAt": now_iso(),
        },
    )


def format_iterations_markdown(project_name: str, records: list[IterationRecord]) -> str:
    lines = [f"# {project_name} 迭代记录", ""]
    lines.append("| 迭代分支 | 时段 | 主要事项 | 提交人数 | 新增行 | 删除行 | 改动文件 | 平均文件/提交 | 稳定性 | 规范性 |")
    lines.append("|---------|------|---------|---------|-------|-------|---------|-------------|-------|-------|")
    for r in records:
        lines.append(
            f"| {r.branch} | {r.date_label} | {r.main_topics} | {r.author_count} "
            f"| +{r.additions:,} | -{r.deletions:,} | {r.changed_files} "
            f"| {r.avg_files_per_commit} | {r.stability} | {r.conventionality} |"
        )
    lines.append("")
    for r in records:
        if not r.authors:
            continue
        lines.append(f"## {r.branch} 提交明细")
        lines.append("")
        lines.append("| 作者 | 提交数 | 新增行 | 删除行 |")
        lines.append("|------|-------|-------|-------|")
        for a in r.authors:
            lines.append(f"| {a.name} | {a.commits} | +{a.additions:,} | -{a.deletions:,} |")
        lines.append("")
    return "\n".join(lines)


def git_cmd(repo_path: Path, args: list[str], check: bool = True) -> str:
    import subprocess

    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        if check:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return ""
    return result.stdout


if __name__ == "__main__":
    raise SystemExit(main())
