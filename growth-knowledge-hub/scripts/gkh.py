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

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=10)

    read_parser = subparsers.add_parser("read")
    read_parser.add_argument("--path", required=True)

    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("--query", required=True)
    context_parser.add_argument("--limit", type=int, default=5)

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
    rebuild_index(root)
    return {"status": "ok", "kind": "capture", "rawSource": raw_source, "writes": [write_to_dict(write)], "redactions": findings}


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
        task_writes.append(write_task_page(root, task, title, tags, [raw_source["rawSourceId"]]))
    rebuild_index(root)
    writes = [write_to_dict(write), *[write_to_dict(item) for item in task_writes]]
    return {"status": "ok", "kind": "review", "rawSource": raw_source, "writes": writes, "redactions": findings}


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


def write_task_page(root: Path, task: str, review_title: str, tags: list[str], source_raw_ids: list[str]) -> WriteResult:
    task_title = task[:80]
    body = frontmatter(
        {
            "type": "growth_task",
            "status": "active",
            "source_raw_ids": source_raw_ids,
            "captured_date": now_iso(),
            "sensitivity": "safe",
            "tags": tags,
        }
    )
    body += f"\n# {task_title}\n\n"
    body += f"来源复盘：{review_title}\n\n"
    body += "## 任务\n"
    body += f"- {task}\n"
    return write_wiki_page(root, f"wiki/growth/tasks/{slug(task_title)}.md", body, source_raw_ids)


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


if __name__ == "__main__":
    raise SystemExit(main())
