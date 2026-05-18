from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Any

from .audit import classify_sensitivity, redact_text
from .models import KnowledgeGap, KnowledgeIngestResult, KnowledgeSourceInput, RawSource, WikiUpdateProposal
from .utils import sha256_text, stable_id, utc_now_iso, write_json
from .wiki import create_wiki_update_proposal, init_llm_wiki


def ingest_note(root: Path, title: str, content: str, tags: list[str] | None = None) -> KnowledgeIngestResult:
    source_input = KnowledgeSourceInput(
        source_type="user_note",
        title=title,
        content=content,
        original_location=f"note:{title}",
        tags=tags or [],
    )
    return ingest_knowledge(root, source_input)


def ingest_file(root: Path, source_path: Path, tags: list[str] | None = None) -> KnowledgeIngestResult:
    text = source_path.read_text(encoding="utf-8")
    source_input = KnowledgeSourceInput(
        source_type="local_document",
        title=source_path.stem,
        content=text,
        original_location=str(source_path),
        tags=tags or [],
    )
    return ingest_knowledge(root, source_input)


def ingest_article_text(root: Path, title: str, content: str, origin_url: str = "", publisher: str = "", author: str = "", tags: list[str] | None = None) -> KnowledgeIngestResult:
    source_input = KnowledgeSourceInput(
        source_type="web_article" if origin_url else "copied_excerpt",
        title=title,
        content=content,
        original_location=origin_url or f"article:{title}",
        origin_url=origin_url,
        publisher=publisher,
        author=author,
        tags=tags or [],
    )
    return ingest_knowledge(root, source_input)


def ingest_url(root: Path, url: str, title: str = "", fetch: bool = False, tags: list[str] | None = None) -> KnowledgeIngestResult:
    if not fetch:
        source_input = KnowledgeSourceInput(
            source_type="web_article",
            title=title or url,
            content=f"URL metadata only: {url}",
            original_location=url,
            origin_url=url,
            tags=tags or [],
            fetch_requested=False,
            fetch_status="not_requested",
        )
        return ingest_knowledge(root, source_input)
    request = urllib.request.Request(url, headers={"User-Agent": "personal-growth-agent/0.1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read()
        final_url = response.geturl()
    text = payload.decode("utf-8", errors="replace")
    source_input = KnowledgeSourceInput(
        source_type="web_article",
        title=title or final_url,
        content=text,
        original_location=url,
        origin_url=url,
        tags=tags or [],
        fetch_requested=True,
        final_url=final_url,
        fetch_status="ok",
    )
    return ingest_knowledge(root, source_input)


def ingest_knowledge(root: Path, source_input: KnowledgeSourceInput) -> KnowledgeIngestResult:
    init_llm_wiki(root)
    redacted_content, findings = redact_text(source_input.content)
    sensitivity = classify_sensitivity(source_input.content)
    safe_content = "" if sensitivity == "local_only" else redacted_content
    digest = sha256_text(f"{source_input.source_type}|{source_input.original_location}|{source_input.title}|{source_input.content}")
    raw_id = stable_id("raw", digest)
    raw_path = root / "raw" / _knowledge_folder(source_input.source_type) / f"{raw_id}.md"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if not raw_path.exists():
        raw_path.write_text(_raw_document(source_input, redacted_content), encoding="utf-8")
    created_at = utc_now_iso()
    manifest_entry = _manifest_entry(source_input, raw_id, digest, sensitivity, len(findings), created_at)
    _append_manifest(root, manifest_entry)
    raw_source = RawSource(
        id=raw_id,
        type=source_input.source_type,
        path=str(raw_path),
        origin="knowledge_ingest",
        created_at=created_at,
        hash=digest,
        sensitivity=sensitivity,
        mutable=False,
    )
    gaps = _extract_knowledge_gaps(source_input, raw_id)
    proposal = _create_knowledge_proposal(root, source_input, raw_source, safe_content, gaps)
    _write_knowledge_gap_pages(root, source_input, gaps)
    return KnowledgeIngestResult(raw_source=raw_source, proposal=proposal, gaps=gaps, manifest_entry=manifest_entry)


def _knowledge_folder(source_type: str) -> str:
    if source_type in {"web_article", "public_account_article"}:
        return "knowledge/web"
    if source_type == "user_note":
        return "knowledge/notes"
    if source_type == "local_document":
        return "knowledge/files"
    return "knowledge/excerpts"


def _raw_document(source_input: KnowledgeSourceInput, content: str) -> str:
    lines = [
        "---",
        f"title: {source_input.title}",
        f"source_type: {source_input.source_type}",
        f"original_location: {source_input.original_location}",
        f"origin_url: {source_input.origin_url}",
        f"publisher: {source_input.publisher}",
        f"author: {source_input.author}",
        f"captured_at: {utc_now_iso()}",
        "tags:",
        *[f"  - {tag}" for tag in source_input.tags],
        "---",
        "",
        content,
        "",
    ]
    return "\n".join(lines)


def _manifest_entry(source_input: KnowledgeSourceInput, raw_id: str, digest: str, sensitivity: str, redaction_count: int, created_at: str) -> dict[str, Any]:
    return {
        "sourceId": stable_id("src", raw_id, source_input.original_location),
        "rawSourceId": raw_id,
        "originalLocation": source_input.original_location,
        "originalUrl": source_input.origin_url,
        "ingestedAt": created_at,
        "capturedAt": created_at,
        "sourceType": source_input.source_type,
        "tool": "knowledge_ingest",
        "redactionStatus": sensitivity,
        "sensitivity": sensitivity,
        "hash": digest,
        "publisher": source_input.publisher,
        "author": source_input.author,
        "tags": source_input.tags,
        "redactionCount": redaction_count,
        "fetchRequested": source_input.fetch_requested,
        "finalUrl": source_input.final_url,
        "fetchStatus": source_input.fetch_status,
    }


def _append_manifest(root: Path, entry: dict[str, Any]) -> None:
    manifest_path = root / "data" / "source-manifest.json"
    existing: list[dict[str, Any]] = []
    if manifest_path.exists():
        import json

        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing.append(entry)
    write_json(manifest_path, existing)


def _create_knowledge_proposal(root: Path, source_input: KnowledgeSourceInput, raw_source: RawSource, safe_content: str, gaps: list[KnowledgeGap]) -> WikiUpdateProposal:
    target_path = f"llm-wiki/wiki/knowledge/concepts/{_slug(source_input.title)}.md"
    safe_origin_url = "[URL_REDACTED]" if source_input.origin_url else ""
    body_lines = [
        "---",
        "type: knowledge_page",
        "status: ready",
        "source_raw_ids:",
        f"  - {raw_source.id}",
        f"original_url: {safe_origin_url}",
        f"captured_date: {raw_source.created_at}",
        f"sensitivity: {raw_source.sensitivity}",
        "confidence: 0.55",
        "review_state: accepted",
        "tags:",
        *[f"  - {tag}" for tag in source_input.tags],
        "related: []",
        "unresolved_questions:",
        *[f"  - {gap.summary}" for gap in gaps],
        "---",
        "",
        f"# {source_input.title}",
        "",
        "## 摘要",
        _summary_from(safe_content),
        "",
        "## 引用来源",
        f"- {raw_source.id}: {raw_source.path}",
    ]
    if gaps:
        body_lines.extend(["", "## 待补充/疑问", *[f"- {gap.summary}" for gap in gaps]])
    return create_wiki_update_proposal(root, source_input.title, target_path, [], [raw_source.id], "\n".join(body_lines))


def _extract_knowledge_gaps(source_input: KnowledgeSourceInput, raw_id: str) -> list[KnowledgeGap]:
    text = source_input.content.lower()
    if "question:" not in text and "？" not in source_input.content and "?" not in source_input.content:
        return []
    tracks = [tag for tag in source_input.tags if tag in {"agent_engineering", "business_depth", "ai_system_management"}]
    if not tracks:
        tracks = ["business_depth" if "business" in text or "业务" in source_input.content else "agent_engineering"]
    return [
        KnowledgeGap(
            id=stable_id("kgap", raw_id, source_input.title),
            title=source_input.title,
            source_raw_ids=[raw_id],
            tracks=tracks,
            summary=f"{source_input.title} contains unresolved learning or application questions.",
            confidence=0.5,
            review_state="pending",
        )
    ]


def _write_knowledge_gap_pages(root: Path, source_input: KnowledgeSourceInput, gaps: list[KnowledgeGap]) -> None:
    for gap in gaps:
        path = root / "wiki" / "knowledge" / "gaps" / f"{_slug(gap.title)}.md"
        if path.exists():
            continue
        lines = [
            "---",
            "type: knowledge_gap",
            "status: draft",
            "source_raw_ids:",
            *[f"  - {raw_id}" for raw_id in gap.source_raw_ids],
            "tracks:",
            *[f"  - {track}" for track in gap.tracks],
            f"confidence: {gap.confidence}",
            f"review_state: {gap.review_state}",
            "tags:",
            *[f"  - {tag}" for tag in source_input.tags],
            "---",
            "",
            f"# {gap.title}",
            "",
            gap.summary,
            "",
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")


def _summary_from(content: str) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return "This source is local-only or empty after privacy filtering."
    return lines[0][:240]


def _slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "knowledge"
