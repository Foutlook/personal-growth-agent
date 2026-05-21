from __future__ import annotations

from pathlib import Path
from typing import Any

from .analyzer import AnalyzerRequest, build_analyzer_payload, call_remote_provider, resolve_provider_credential, resolve_provider_route, validate_scenario_output
from .audit import assert_no_sensitive_content
from .prompts import PromptTemplate
from .utils import sha256_text
from .wiki import init_llm_wiki, write_wiki_page_direct


def compile_raw_to_wiki(root: Path, raw_path: Path, prompt: PromptTemplate, llm_config: Any | None = None, provider: str = "local", model: str = "", approved: bool = False, dry_run: bool = False, transport: Any | None = None) -> list:
    init_llm_wiki(root)
    paths = _raw_paths(raw_path)
    if provider and provider != "local" and llm_config:
        return _compile_raw_to_wiki_remote(root, paths, prompt, llm_config, provider, model, approved, dry_run, transport)
    results = []
    prompt_payload = {
        "id": prompt.id,
        "version": prompt.version,
        "path": prompt.path,
        "digest": prompt.digest,
    }
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert_no_sensitive_content(text)
        title = _first_heading(text) or path.stem
        target_path = f"llm-wiki/wiki/knowledge/concepts/{_slug(title)}.md"
        body = _compiled_body(title, text, path)
        result = write_wiki_page_direct(
            root,
            title,
            target_path,
            [],
            [sha256_text(str(path))[:12]],
            body,
            prompt=prompt_payload,
            compiler="local_rule",
        )
        results.append(result)
    return results


def _compile_raw_to_wiki_remote(root: Path, paths: list[Path], prompt: PromptTemplate, llm_config: Any, provider: str, model: str, approved: bool, dry_run: bool, transport: Any | None) -> list:
    if not approved or dry_run:
        return []
    route = resolve_provider_route(llm_config, "knowledge_ingest", provider, model or None)
    credential = resolve_provider_credential(route)
    if not credential.available:
        return []
    results = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert_no_sensitive_content(text)
        prompt_payload = {"id": prompt.id, "version": prompt.version, "scenario": prompt.scenario, "path": prompt.path, "digest": prompt.digest, "content": prompt.content}
        request = AnalyzerRequest(
            provider=route.provider,
            model=route.model,
            analysis_mode="wiki_compile",
            evidence=[{"id": "raw", "summary": text[:500], "sensitivity": "safe"}],
            signals=[],
            wiki_memory=[],
            approved=approved,
            dry_run=dry_run,
            scenario="knowledge_ingest",
            prompt=prompt_payload,
            output_schema="wiki_updates_v1",
        )
        payload, _preview = build_analyzer_payload(request, max_evidence_items=1)
        remote_result = call_remote_provider(route, payload, credential, transport)
        if not remote_result.output:
            continue
        validated = validate_scenario_output("knowledge_ingest", remote_result.output, {"raw"})
        for update in validated["wikiUpdates"]:
            title = str(update.get("title") or _first_heading(text) or path.stem)
            body = str(update.get("body") or update.get("content") or "")
            if not body:
                continue
            if not body.startswith("---"):
                body = _remote_body(title, body, path)
            target_path = f"llm-wiki/wiki/knowledge/concepts/{_slug(title)}.md"
            result = write_wiki_page_direct(
                root,
                title,
                target_path,
                ["raw"],
                [sha256_text(str(path))[:12]],
                body,
                prompt=prompt_payload,
                compiler="llm",
                provider=route.provider,
                model=route.model,
            )
            results.append(result)
    return results


def _raw_paths(raw_path: Path) -> list[Path]:
    if raw_path.is_file():
        return [raw_path]
    if raw_path.is_dir():
        return sorted(path for path in raw_path.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"})
    return []


def _compiled_body(title: str, text: str, source_path: Path) -> str:
    summary = _summary_from(text)
    return "\n".join(
        [
            "---",
            "type: knowledge_page",
            "status: ready",
            "source_paths:",
            f"  - {source_path}",
            "sensitivity: safe",
            "confidence: 0.5",
            "tags: []",
            "related: []",
            "---",
            "",
            f"# {title}",
            "",
            "## 摘要",
            summary,
            "",
            "## 引用来源",
            f"- {source_path}",
            "",
        ]
    )


def _remote_body(title: str, body: str, source_path: Path) -> str:
    return "\n".join(
        [
            "---",
            "type: knowledge_page",
            "status: ready",
            "source_paths:",
            f"  - {source_path}",
            "sensitivity: safe",
            "confidence: 0.65",
            "tags: []",
            "related: []",
            "---",
            "",
            body if body.startswith("# ") else f"# {title}\n\n{body}",
            "",
            "## 引用来源",
            f"- {source_path}",
            "",
        ]
    )


def _summary_from(text: str) -> str:
    lines = [line.strip("# ").strip() for line in text.splitlines() if line.strip() and not line.startswith("---")]
    if not lines:
        return "No readable content found in raw source."
    return lines[0][:240]


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""


def _slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "knowledge"
