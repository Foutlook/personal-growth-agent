from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit import assert_no_sensitive_content
from .models import GrowthMemoryContext, GrowthMemoryMetadata, GrowthRunSnapshot, RawSource, WikiLintIssue, WikiPage, WikiUpdateProposal
from .utils import sha256_text, stable_id, to_jsonable, utc_now_iso, write_json


def init_llm_wiki(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _write_agents_rules(root / "AGENTS.md")
    _write_if_missing(root / "SCHEMA.md", "# LLM Wiki Schema\n\n所有 WikiPage 必须包含 frontmatter 和来源引用。\n")


def validate_growth_memory_metadata(metadata: GrowthMemoryMetadata) -> None:
    valid_lifecycle = {"proposed", "active", "completed", "carried_forward", "stale", "superseded", "rejected"}
    valid_evidence = {"Observed", "Inferred", "Unknown", "HumanConfirmed"}
    if metadata.lifecycle_status not in valid_lifecycle:
        raise ValueError(f"invalid lifecycle status: {metadata.lifecycle_status}")
    if metadata.evidence_status not in valid_evidence:
        raise ValueError(f"invalid evidence status: {metadata.evidence_status}")
    if not metadata.source_run_id:
        raise ValueError("growth memory metadata requires source_run_id")
    if not metadata.source_evidence_ids:
        raise ValueError("growth memory metadata requires source evidence references")
    if metadata.confidence < 0 or metadata.confidence > 1:
        raise ValueError("growth memory confidence must be between 0 and 1")
    if not metadata.valid_until:
        raise ValueError("growth memory metadata requires valid_until")


def create_growth_run_snapshot(root: Path, run_id: str, snapshot: dict[str, Any], source_evidence_ids: list[str], source_raw_ids: list[str]) -> GrowthRunSnapshot:
    init_llm_wiki(root)
    content = json.dumps(to_jsonable(snapshot), ensure_ascii=False, indent=2)
    assert_no_sensitive_content(content)
    digest = sha256_text(f"{run_id}|{content}")
    snapshot_id = stable_id("growth_run", run_id)
    path = root / "raw" / "growth-runs" / f"{snapshot_id}.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    created_at = utc_now_iso()
    _append_manifest(
        root,
        {
            "sourceId": stable_id("src", snapshot_id, run_id),
            "rawSourceId": snapshot_id,
            "originalLocation": f"runs/{run_id}",
            "ingestedAt": created_at,
            "sourceType": "growth_run",
            "tool": "personal_growth_agent",
            "redactionStatus": "redacted",
            "hash": digest,
            "sourceEvidenceIds": source_evidence_ids,
            "sourceRawIds": source_raw_ids,
            "runId": run_id,
        },
    )
    return GrowthRunSnapshot(
        id=snapshot_id,
        run_id=run_id,
        path=str(path),
        source_evidence_ids=source_evidence_ids,
        source_raw_ids=source_raw_ids,
        created_at=created_at,
        hash=digest,
    )


def create_growth_memory_proposals(root: Path, cycle, snapshot: GrowthRunSnapshot, source_evidence_ids: list[str]) -> list[WikiUpdateProposal]:
    init_llm_wiki(root)
    _migrate_legacy_growth_task_files(root)
    proposals: list[WikiUpdateProposal] = []
    proposals.append(
        _create_growth_memory_proposal(
            root,
            "Growth cycle summary",
            "llm-wiki/wiki/growth/cycles/latest.md",
            GrowthMemoryMetadata(
                type="growth_cycle",
                lifecycle_status="active",
                source_run_id=snapshot.run_id,
                source_evidence_ids=source_evidence_ids,
                source_raw_ids=[],
                evidence_status="Inferred",
                confidence=0.7,
                human_confirmed=False,
                valid_until=_default_valid_until(),
                review_state="accepted",
                tracks=[estimate.track for estimate in cycle.maturity_estimates],
                related=[],
            ),
            ["## Summary", cycle.theme],
        )
    )
    for diagnosis in cycle.diagnoses:
        proposals.append(
            _create_growth_memory_proposal(
                root,
                diagnosis.title,
                f"llm-wiki/wiki/growth/diagnoses/{diagnosis.id}.md",
                GrowthMemoryMetadata(
                    type="diagnosis",
                    lifecycle_status="active",
                    source_run_id=snapshot.run_id,
                    source_evidence_ids=diagnosis.supporting_evidence_ids or source_evidence_ids,
                    source_raw_ids=[],
                    evidence_status="Inferred",
                    confidence=diagnosis.confidence,
                    human_confirmed=False,
                    valid_until=_default_valid_until(),
                    review_state="pending",
                    tracks=diagnosis.target_tracks,
                    related=[],
                ),
                ["## Diagnosis", diagnosis.summary, "", "## Recommended Focus", diagnosis.recommended_focus],
            )
        )
    for task in cycle.tasks:
        lifecycle_status = "carried_forward" if task.task_type == "carried_forward" else "active"
        task_path = _growth_task_target_path(task)
        proposals.append(
            _create_growth_memory_proposal(
                root,
                task.title,
                task_path,
                GrowthMemoryMetadata(
                    type="growth_task",
                    lifecycle_status=lifecycle_status,
                    source_run_id=snapshot.run_id,
                    source_evidence_ids=source_evidence_ids,
                    source_raw_ids=[],
                    evidence_status="Inferred",
                    confidence=0.65,
                    human_confirmed=False,
                    valid_until=_default_valid_until(),
                    review_state="pending",
                    tracks=[task.primary_track, *task.secondary_tracks],
                    related=task.expected_artifacts,
                ),
                ["## Task", task.title, "", "## Steps", *[f"- {step}" for step in task.steps], "", "## Done Definition", *[f"- {item}" for item in task.done_definition]],
            )
        )
    for estimate in cycle.maturity_estimates:
        proposals.append(
            _create_growth_memory_proposal(
                root,
                f"{estimate.track} maturity snapshot",
                f"llm-wiki/wiki/growth/maturity-snapshots/{snapshot.run_id}-{estimate.track}.md",
                GrowthMemoryMetadata(
                    type="maturity_snapshot",
                    lifecycle_status="active",
                    source_run_id=snapshot.run_id,
                    source_evidence_ids=source_evidence_ids,
                    source_raw_ids=[],
                    evidence_status=estimate.status,
                    confidence=estimate.confidence,
                    human_confirmed=False,
                    valid_until=_default_valid_until(),
                    review_state="pending",
                    tracks=[estimate.track],
                    related=[],
                ),
                ["## Maturity", f"Level: {estimate.estimated_level}", f"Status: {estimate.status}"],
            )
        )
    proposals.append(
        _create_growth_memory_proposal(
            root,
            "Growth report summary",
            f"llm-wiki/wiki/growth/cycles/{snapshot.run_id}-report-summary.md",
            GrowthMemoryMetadata(
                type="report_summary",
                lifecycle_status="active",
                source_run_id=snapshot.run_id,
                source_evidence_ids=source_evidence_ids,
                source_raw_ids=[],
                evidence_status="Inferred",
                confidence=0.7,
                human_confirmed=False,
                valid_until=_default_valid_until(),
                review_state="accepted",
                tracks=[estimate.track for estimate in cycle.maturity_estimates],
                related=[snapshot.path],
            ),
            ["## Report Summary", f"Raw snapshot: {snapshot.path}"],
        )
    )
    return proposals


def ingest_raw_source(root: Path, source_type: str, origin: str, content: str, original_location: str) -> RawSource:
    assert_no_sensitive_content(content)
    init_llm_wiki(root)
    digest = sha256_text(f"{source_type}|{origin}|{original_location}|{content}")
    raw_id = stable_id("raw", digest)
    path = root / "raw" / _folder_for(source_type) / f"{raw_id}.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    manifest_path = root / "data" / "source-manifest.json"
    entry = {
        "sourceId": stable_id("src", raw_id, original_location),
        "rawSourceId": raw_id,
        "originalLocation": original_location,
        "ingestedAt": utc_now_iso(),
        "sourceType": source_type,
        "tool": origin,
        "redactionStatus": "redacted",
        "hash": digest,
    }
    _append_manifest(root, entry)
    return RawSource(id=raw_id, type=source_type, path=str(path), origin=origin, created_at=entry["ingestedAt"], hash=digest, sensitivity="redacted", mutable=False)


def create_wiki_update_proposal(root: Path, title: str, target_path: str, source_evidence_ids: list[str], source_raw_ids: list[str], body: str) -> WikiUpdateProposal:
    init_llm_wiki(root)
    assert_no_sensitive_content(body)
    proposal_id = stable_id("wiki_update", target_path, ",".join(source_evidence_ids), body)
    update_path = root / target_path.removeprefix("llm-wiki/")
    update_path.parent.mkdir(parents=True, exist_ok=True)
    update_path.write_text(body if body.endswith("\n") else f"{body}\n", encoding="utf-8")
    return WikiUpdateProposal(
        id=proposal_id,
        type="create",
        target_path=target_path,
        reason=f"{title} was accepted into the LLM Wiki.",
        source_evidence_ids=source_evidence_ids,
        source_raw_ids=source_raw_ids,
        diff_path=str(update_path),
        risk="low",
        requires_human_review=False,
        status="accepted",
    )


def create_wiki_page_draft(root: Path, title: str, page_type: str, target_path: str, source_evidence_ids: list[str], tracks: list[str], body: str, source_raw_ids: list[str] | None = None) -> WikiPage:
    init_llm_wiki(root)
    assert_no_sensitive_content(body)
    raw_source_ids = source_raw_ids or []
    path = root / target_path.removeprefix("llm-wiki/")
    frontmatter = [
        "---",
        f"title: {title}",
        f"type: {page_type}",
        "status: draft",
        f"source_count: {len(source_evidence_ids) + len(raw_source_ids)}",
        "source_evidence_ids:",
        *[f"  - {item}" for item in source_evidence_ids],
    ]
    if raw_source_ids:
        frontmatter.extend(["source_raw_ids:", *[f"  - {item}" for item in raw_source_ids]])
    frontmatter.extend(
        [
            f"last_reviewed: {utc_now_iso()}",
            "sensitivity: internal",
            "confidence: 0.7",
            "tracks:",
            *[f"  - {track}" for track in tracks],
            "related: []",
            "---",
            "",
            body,
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(frontmatter), encoding="utf-8")
    return WikiPage(
        id=stable_id("wiki", target_path),
        title=title,
        path=str(path),
        type=page_type,
        status="draft",
        source_evidence_ids=source_evidence_ids,
        source_raw_ids=raw_source_ids,
        linked_pages=[],
        tracks=tracks,
        confidence=0.7,
        last_reviewed_at=utc_now_iso(),
    )


def lint_wiki(root: Path) -> list[WikiLintIssue]:
    init_llm_wiki(root)
    issues: list[WikiLintIssue] = []
    for page in (root / "wiki").rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        if not text.startswith("---"):
            issues.append(
                WikiLintIssue(
                    id=stable_id("lint", page, "invalid_frontmatter"),
                    severity="warning",
                    page_path=str(page),
                    type="invalid_frontmatter",
                    message="WikiPage missing frontmatter.",
                    suggested_fix="Add required frontmatter fields.",
                )
            )
        metadata = _parse_frontmatter(text)
        if metadata.get("type", "").startswith("growth") or metadata.get("type") in {"diagnosis", "maturity_snapshot", "profile_snapshot", "report_summary"}:
            issues.extend(_lint_growth_memory_page(page, metadata))
        if str(metadata.get("type") or "").startswith("knowledge"):
            issues.extend(_lint_knowledge_page(page, metadata))
    report_path = root / "report" / "lint-reports" / "wiki-lint-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(f"- {issue.severity}: {issue.type} {issue.page_path}" for issue in issues) or "No lint issues.", encoding="utf-8")
    return issues


def load_growth_memory_context(root: Path) -> GrowthMemoryContext:
    init_llm_wiki(root)
    context = GrowthMemoryContext()
    for page in (root / "wiki").rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        if not metadata:
            continue
        lifecycle_status = str(metadata.get("lifecycle_status") or "")
        if lifecycle_status in {"stale", "rejected", "superseded"}:
            continue
        if _is_expired(str(metadata.get("valid_until") or "")):
            continue
        record = {
            "path": str(page),
            "title": _first_heading(text),
            "type": metadata.get("type"),
            "lifecycle_status": lifecycle_status,
            "evidence_status": metadata.get("evidence_status"),
            "human_confirmed": metadata.get("human_confirmed") is True or str(metadata.get("human_confirmed")).lower() == "true",
            "confidence": metadata.get("confidence"),
            "source_run_id": metadata.get("source_run_id"),
            "tracks": metadata.get("tracks") or [],
        }
        if record["type"] == "diagnosis":
            context.active_diagnoses.append(record)
        elif record["type"] == "growth_task":
            context.active_tasks.append(record)
        elif record["type"] == "growth_review":
            context.recent_reviews.append(record)
        elif record["type"] == "maturity_snapshot":
            context.maturity_snapshots.append(record)
        elif record["type"] == "north_star":
            context.north_star_pages.append(str(page))
        elif record["type"] in {"knowledge_page", "knowledge_source"}:
            context.knowledge_summaries.append(record)
        elif record["type"] == "knowledge_gap":
            context.knowledge_gaps.append(record)
        if record["evidence_status"] == "HumanConfirmed" or record["human_confirmed"]:
            context.human_confirmed_memory.append(record)
        elif record["evidence_status"] == "Inferred":
            context.inferred_memory.append(record)
    return context


def _folder_for(source_type: str) -> str:
    if source_type == "repository_snapshot":
        return "repositories"
    if source_type == "growth_artifact":
        return "growth-artifacts"
    if source_type == "growth_run":
        return "growth-runs"
    if source_type == "growth_review":
        return "growth-reviews"
    if source_type == "action_asset":
        return "action-assets"
    if source_type in {"web_article", "public_account_article"}:
        return "knowledge/web"
    if source_type == "user_note":
        return "knowledge/notes"
    if source_type == "local_document":
        return "knowledge/files"
    if source_type in {"copied_excerpt", "reference_material"}:
        return "knowledge/excerpts"
    return "conversations"


def _write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _write_agents_rules(path: Path) -> None:
    content = "# LLM Wiki 操作规则\n\n- raw/knowledge/ 只读，禁止覆盖。\n- AI 对话证据链保存在 runs/，不要写入 raw/conversations/。\n- Wiki 更新默认自动写入 wiki/ 正式页面。\n"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return
    existing = path.read_text(encoding="utf-8")
    migrated = existing.replace("Wiki 更新默认生成 diff。", "Wiki 更新默认自动写入 wiki/ 正式页面。")
    if migrated != existing:
        path.write_text(migrated, encoding="utf-8")


def _append_manifest(root: Path, entry: dict[str, Any]) -> None:
    manifest_path = root / "data" / "source-manifest.json"
    existing = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing.append(entry)
    write_json(manifest_path, existing)


def _create_growth_memory_proposal(root: Path, title: str, target_path: str, metadata: GrowthMemoryMetadata, body_lines: list[str]) -> WikiUpdateProposal:
    validate_growth_memory_metadata(metadata)
    body = "\n".join([*_frontmatter_lines(metadata), "", f"# {title}", "", *body_lines, ""])
    if metadata.type == "growth_task":
        _remove_legacy_growth_task_file(root, target_path, title)
    return create_wiki_update_proposal(root, title, target_path, metadata.source_evidence_ids, metadata.source_raw_ids, body)


def _growth_task_target_path(task: Any) -> str:
    task_slug = _growth_task_slug(task)
    return f"llm-wiki/wiki/growth/tasks/{task_slug}.md"


def _growth_task_slug(task: Any) -> str:
    task_type = str(getattr(task, "task_type", "") or "")
    known_task_types = {
        "case_analysis": "agent-flow-analysis",
        "business_modeling": "business-goal-card",
        "evaluation_design": "ai-output-rubric",
        "carried_forward": "carried-forward-review",
        "knowledge_gap": "knowledge-gap-application",
    }
    if task_type in known_task_types:
        return known_task_types[task_type]
    title = str(getattr(task, "title", "") or getattr(task, "id", "") or "growth-task")
    title_slug = _known_growth_task_slug_from_title(title)
    if title_slug:
        return title_slug
    return _slugify_task_title(title)


def _known_growth_task_slug_from_title(title: str) -> str:
    if "Agent 流程图" in title or "Agent 流程" in title:
        return "agent-flow-analysis"
    if "业务目标卡" in title:
        return "business-goal-card"
    if "AI 输出验收 Rubric" in title or "Rubric" in title:
        return "ai-output-rubric"
    if "知识缺口" in title:
        return "knowledge-gap-application"
    if "延续并复盘" in title:
        return "carried-forward-review"
    return ""


def _slugify_task_title(title: str) -> str:
    normalized = []
    previous_dash = False
    for char in title.lower():
        if char.isascii() and char.isalnum():
            normalized.append(char)
            previous_dash = False
            continue
        if char in {" ", "-", "_"} and not previous_dash:
            normalized.append("-")
            previous_dash = True
    slug = "".join(normalized).strip("-")
    return slug or "growth-task"


def _remove_legacy_growth_task_file(root: Path, target_path: str, title: str) -> None:
    target = root / target_path.removeprefix("llm-wiki/")
    legacy_root = root / "wiki" / "growth" / "tasks"
    if not legacy_root.exists():
        return
    for page in legacy_root.glob("task_*.md"):
        if page == target:
            continue
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        if metadata.get("type") != "growth_task":
            continue
        if _first_heading(text) != title:
            continue
        page.unlink()


def _migrate_legacy_growth_task_files(root: Path) -> None:
    legacy_root = root / "wiki" / "growth" / "tasks"
    if not legacy_root.exists():
        return
    for page in list(legacy_root.glob("task_*.md")):
        text = page.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(text)
        if metadata.get("type") != "growth_task":
            continue
        title = _first_heading(text)
        slug = _known_growth_task_slug_from_title(title)
        if not slug:
            slug = _slugify_task_title(title)
        target = legacy_root / f"{slug}.md"
        if target.exists():
            page.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        page.rename(target)


def _frontmatter_lines(metadata: GrowthMemoryMetadata) -> list[str]:
    return [
        "---",
        f"type: {metadata.type}",
        f"lifecycle_status: {metadata.lifecycle_status}",
        f"source_run_id: {metadata.source_run_id}",
        "source_evidence_ids:",
        *[f"  - {item}" for item in metadata.source_evidence_ids],
        f"evidence_status: {metadata.evidence_status}",
        f"confidence: {metadata.confidence}",
        f"human_confirmed: {str(metadata.human_confirmed).lower()}",
        f"valid_until: {metadata.valid_until}",
        f"review_state: {metadata.review_state}",
        "tracks:",
        *[f"  - {track}" for track in metadata.tracks],
        "related:",
        *[f"  - {item}" for item in metadata.related],
        "---",
    ]


def _default_valid_until() -> str:
    return "2099-01-01T00:00:00+00:00"


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
        elif value.lower() in {"true", "false"}:
            metadata[key] = value.lower() == "true"
        elif key == "confidence":
            try:
                metadata[key] = float(value)
            except ValueError:
                metadata[key] = value
        else:
            metadata[key] = value
    return metadata


def _lint_growth_memory_page(page: Path, metadata: dict[str, Any]) -> list[WikiLintIssue]:
    issues: list[WikiLintIssue] = []
    missing_trace = not metadata.get("source_run_id") or not metadata.get("source_evidence_ids")
    if missing_trace:
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_missing_source"),
                severity="error",
                page_path=str(page),
                type="growth_missing_source",
                message="Growth memory page missing source evidence or run metadata.",
                suggested_fix="Add source_run_id and source_evidence_ids frontmatter.",
            )
        )
    lifecycle_status = str(metadata.get("lifecycle_status") or "")
    if lifecycle_status and lifecycle_status not in {"proposed", "active", "completed", "carried_forward", "stale", "superseded", "rejected"}:
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_invalid_lifecycle"),
                severity="error",
                page_path=str(page),
                type="growth_invalid_lifecycle",
                message="Growth memory page has invalid lifecycle status.",
                suggested_fix="Use a supported lifecycle status.",
            )
        )
    page_type = str(metadata.get("type") or "")
    if page_type == "diagnosis" and _is_expired(str(metadata.get("valid_until") or "")):
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_stale_diagnosis"),
                severity="warning",
                page_path=str(page),
                type="growth_stale_diagnosis",
                message="Diagnosis is past its validity window.",
                suggested_fix="Refresh evidence or mark the diagnosis stale.",
            )
        )
    if page_type == "maturity_snapshot" and _is_expired(str(metadata.get("valid_until") or "")):
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_expired_maturity"),
                severity="warning",
                page_path=str(page),
                type="growth_expired_maturity",
                message="Maturity snapshot is expired.",
                suggested_fix="Generate a new maturity snapshot.",
            )
        )
    if page_type == "growth_task" and metadata.get("lifecycle_status") == "completed" and metadata.get("review_state") != "reviewed":
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_unreviewed_task"),
                severity="warning",
                page_path=str(page),
                type="growth_unreviewed_task",
                message="Completed growth task has no completed review.",
                suggested_fix="Add or link a GrowthReview.",
            )
        )
    if page_type == "profile_snapshot" and not metadata.get("source_evidence_ids") and not metadata.get("human_confirmed"):
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "growth_unsupported_profile_claim"),
                severity="error",
                page_path=str(page),
                type="growth_unsupported_profile_claim",
                message="Profile claim has no evidence and is not human confirmed.",
                suggested_fix="Link source evidence or mark human_confirmed only after review.",
            )
        )
    return issues


def _lint_knowledge_page(page: Path, metadata: dict[str, Any]) -> list[WikiLintIssue]:
    issues: list[WikiLintIssue] = []
    has_source = bool(metadata.get("source_raw_ids") or metadata.get("source_paths") or metadata.get("original_url"))
    if not has_source:
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "knowledge_missing_provenance"),
                severity="error",
                page_path=str(page),
                type="knowledge_missing_provenance",
                message="Knowledge page missing raw source references or original source metadata.",
                suggested_fix="Add source_raw_ids, source_paths, or original_url frontmatter.",
            )
        )
    if metadata.get("sensitivity") == "local_only" and metadata.get("dashboard_visible") == "true":
        issues.append(
            WikiLintIssue(
                id=stable_id("lint", page, "knowledge_unsafe_dashboard_visibility"),
                severity="error",
                page_path=str(page),
                type="knowledge_unsafe_dashboard_visibility",
                message="Local-only knowledge page is marked dashboard visible.",
                suggested_fix="Remove dashboard visibility or redact the page.",
            )
        )
    return issues


def _is_expired(value: str) -> bool:
    if not value:
        return False
    return value < utc_now_iso()


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""
