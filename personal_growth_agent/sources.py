from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .data import ParseFailure, SourceCandidate, discover_source_files, parse_source_file, should_ignore_source_file
from .models import ConversationSession
from .utils import read_json, sha256_text, write_json


@dataclass
class SourceFileRecord:
    adapter: str
    path: str
    exists: bool
    size: int
    mtime: float
    hash: str
    parse_status: str
    parse_error: str = ""
    unchanged: bool = False


@dataclass
class IgnoreDecision:
    ignored: bool
    reason: str = ""


class SourceAdapter:
    name = "source"

    def __init__(self, paths: Iterable[Path] | None = None):
        self.paths = [Path(path).expanduser() for path in paths] if paths is not None else self.default_paths()

    def default_paths(self) -> list[Path]:
        return []

    def discover(self) -> list[Path]:
        files: list[Path] = []
        for path in self.paths:
            if path.exists():
                files.extend(discover_source_files(self.name, path))
        return files

    def discover_all_candidates(self) -> list[Path]:
        files: list[Path] = []
        for path in self.paths:
            if path.exists():
                files.extend(discover_source_files(self.name, path))
        return files

    def should_ignore(self, path: Path) -> IgnoreDecision:
        ignored = should_ignore_source_file(self.name, path)
        return IgnoreDecision(ignored, "known_non_conversation" if ignored else "")

    def fingerprint(self, path: Path) -> dict[str, object]:
        stat = path.stat()
        text = path.read_text(encoding="utf-8", errors="replace")
        return {"size": stat.st_size, "mtime": stat.st_mtime, "hash": sha256_text(text)}

    def parse(self, path: Path) -> ConversationSession:
        sessions = parse_source_file(self.name, path)
        if not sessions:
            raise ValueError("no conversation sessions parsed")
        return sessions[0]

    def to_candidate(self) -> SourceCandidate:
        files = self.discover()
        exists = any(path.exists() for path in self.paths)
        candidate_path = self.paths[0] if self.paths else Path("")
        return SourceCandidate(name=self.name, path=candidate_path, exists=exists, files=files)


class CodexAdapter(SourceAdapter):
    name = "codex"

    def default_paths(self) -> list[Path]:
        return [Path.home() / ".codex"]

    def should_ignore(self, path: Path) -> IgnoreDecision:
        if not should_ignore_source_file(self.name, path):
            return IgnoreDecision(False)
        parts = set(path.parts)
        if "skills" in parts and path.name == "test-prompts.json":
            return IgnoreDecision(True, "codex_skill_eval")
        if ".sandbox" in parts or ".sandbox-secrets" in parts:
            return IgnoreDecision(True, "codex_sandbox_metadata")
        return IgnoreDecision(True, "known_non_conversation")


class ClaudeCodeAdapter(SourceAdapter):
    name = "claude_code"

    def default_paths(self) -> list[Path]:
        return [Path.home() / ".claude"]

    def should_ignore(self, path: Path) -> IgnoreDecision:
        if not should_ignore_source_file(self.name, path):
            return IgnoreDecision(False)
        parts = set(path.parts)
        if "telemetry" in parts:
            return IgnoreDecision(True, "claude_telemetry")
        if "todos" in parts:
            return IgnoreDecision(True, "claude_todos")
        if "node_modules" in parts:
            return IgnoreDecision(True, "node_modules_metadata")
        if "plugins" in parts and ("evals" in parts or "node_modules" in parts):
            return IgnoreDecision(True, "claude_plugin_metadata")
        return IgnoreDecision(True, "known_non_conversation")


class OpenCodeAdapter(SourceAdapter):
    name = "opencode"

    def default_paths(self) -> list[Path]:
        return [Path.home() / ".local" / "share" / "opencode"]

    def should_ignore(self, path: Path) -> IgnoreDecision:
        if not should_ignore_source_file(self.name, path):
            return IgnoreDecision(False)
        parts = set(path.parts)
        if path.name == "auth.json":
            return IgnoreDecision(True, "opencode_auth_config")
        if "node_modules" in parts:
            return IgnoreDecision(True, "node_modules_metadata")
        if "session_diff" in parts:
            return IgnoreDecision(True, "opencode_session_diff_cache")
        return IgnoreDecision(True, "known_non_conversation")


def default_adapters(configured_paths: dict[str, list[Path]] | None = None) -> list[SourceAdapter]:
    if configured_paths:
        adapters: list[SourceAdapter] = []
        if "codex" in configured_paths:
            adapters.append(CodexAdapter(configured_paths["codex"]))
        if "claude_code" in configured_paths:
            adapters.append(ClaudeCodeAdapter(configured_paths["claude_code"]))
        if "opencode" in configured_paths:
            adapters.append(OpenCodeAdapter(configured_paths["opencode"]))
        return adapters
    configured_paths = {}
    return [
        CodexAdapter(configured_paths.get("codex")),
        ClaudeCodeAdapter(configured_paths.get("claude_code")),
        OpenCodeAdapter(configured_paths.get("opencode")),
    ]


def scan_sources(adapters: list[SourceAdapter], manifest_path: Path) -> dict[str, object]:
    previous = _load_manifest(manifest_path)
    previous_by_key = {(item.get("adapter"), item.get("path")): item for item in previous.get("files", [])}
    files: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    sessions: list[ConversationSession] = []
    unchanged_count = 0
    for adapter in adapters:
        for file_path in adapter.discover_all_candidates():
            fingerprint = adapter.fingerprint(file_path)
            previous_item = previous_by_key.get((adapter.name, str(file_path)))
            unchanged = bool(previous_item and previous_item.get("hash") == fingerprint["hash"])
            if unchanged:
                unchanged_count += 1
            parse_status = "unchanged" if unchanged else "parsed"
            parse_error = ""
            ignore_decision = adapter.should_ignore(file_path)
            if ignore_decision.ignored:
                parse_status = "ignored"
                parse_error = ignore_decision.reason
            elif not unchanged:
                try:
                    sessions.extend(parse_source_file(adapter.name, file_path))
                except Exception as exc:
                    parse_status = "failed"
                    parse_error = str(exc)
                    failures.append({"adapter": adapter.name, "path": str(file_path), "reason": parse_error})
            files.append(
                {
                    "adapter": adapter.name,
                    "path": str(file_path),
                    "exists": file_path.exists(),
                    "size": fingerprint["size"],
                    "mtime": fingerprint["mtime"],
                    "hash": fingerprint["hash"],
                    "parseStatus": parse_status,
                    "parseError": parse_error,
                    "unchanged": unchanged,
                }
            )
    inventory = {
        "summary": {
            "adapters": [adapter.name for adapter in adapters],
            "discoveredFiles": len(files),
            "unchangedFiles": unchanged_count,
            "parseFailures": len(failures),
            "ignoredFiles": len([item for item in files if item["parseStatus"] == "ignored"]),
        },
        "files": files,
        "failures": failures,
        "sessions": [session.id for session in sessions],
    }
    write_json(manifest_path, inventory)
    return inventory


def adapters_to_candidates(adapters: list[SourceAdapter]) -> list[SourceCandidate]:
    return [adapter.to_candidate() for adapter in adapters]


def parse_with_adapters(adapters: list[SourceAdapter]) -> tuple[list[ConversationSession], list[ParseFailure]]:
    sessions: list[ConversationSession] = []
    failures: list[ParseFailure] = []
    for adapter in adapters:
        for file_path in adapter.discover():
            try:
                sessions.extend(parse_source_file(adapter.name, file_path))
            except Exception as exc:
                failures.append(ParseFailure(source=adapter.name, path=str(file_path), reason=str(exc)))
    return sessions, failures


def _load_manifest(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"files": []}
    return read_json(path)
