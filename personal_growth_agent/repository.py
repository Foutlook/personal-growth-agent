from __future__ import annotations

import subprocess
from pathlib import Path

from .models import RepositoryEvidencePack


def analyze_repository(path: Path, confirmed: bool) -> RepositoryEvidencePack:
    if not confirmed:
        raise PermissionError("repository analysis requires user confirmation")
    root = Path(path)
    files = [item for item in root.rglob("*") if item.is_file()]
    signals = {
        "has_tests": any("test" in item.name.lower() or "tests" in [part.lower() for part in item.parts] for item in files),
        "has_ci": any(".github" in [part.lower() for part in item.parts] or "ci" in item.name.lower() for item in files),
        "has_docs": any(item.name.lower().startswith("readme") or "docs" in [part.lower() for part in item.parts] for item in files),
        "has_scripts": any("scripts" in [part.lower() for part in item.parts] for item in files),
        "has_agent_rules": any(item.name.lower() in {"agents.md", "claude.md"} or "opencode" in item.name.lower() for item in files),
    }
    return RepositoryEvidencePack(
        path=str(root),
        git_summary=_git_summary(root),
        structure_summary={
            "fileCount": len(files),
            "topLevel": sorted(item.name for item in root.iterdir()) if root.exists() else [],
            "fileTypes": _file_types(files),
            "languages": _languages(files),
        },
        signals=signals,
        sensitivity_notes=[],
        skipped_paths=[],
        source_references=[str(root)],
    )


def _git_summary(root: Path) -> dict[str, object]:
    try:
        result = subprocess.run(["git", "-C", str(root), "log", "--oneline", "-5"], capture_output=True, text=True, timeout=5)
        commits = [line for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        commits = []
    return {"recentCommitCount": len(commits), "recentCommits": commits}


def _file_types(files: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        suffix = item.suffix.lower() or "[no-extension]"
        counts[suffix] = counts.get(suffix, 0) + 1
    return counts


def _languages(files: list[Path]) -> dict[str, int]:
    mapping = {".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".md": "markdown", ".json": "json", ".java": "java", ".go": "go"}
    counts: dict[str, int] = {}
    for item in files:
        language = mapping.get(item.suffix.lower())
        if language:
            counts[language] = counts.get(language, 0) + 1
    return counts
