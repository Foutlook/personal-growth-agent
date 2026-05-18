from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import ConversationSession
from .utils import read_json, stable_id


SUPPORTED_SOURCES = ("codex", "claude_code", "opencode")
DEFAULT_SOURCE_PATHS = {
    "codex": [Path.home() / ".codex"],
    "claude_code": [Path.home() / ".claude"],
    "opencode": [Path.home() / ".local" / "share" / "opencode"],
}


@dataclass
class SourceCandidate:
    name: str
    path: Path
    exists: bool
    files: list[Path]


@dataclass
class ParseFailure:
    source: str
    path: str
    reason: str


def discover_sources(configured_paths: dict[str, Iterable[Path]] | None = None) -> list[SourceCandidate]:
    paths = configured_paths or DEFAULT_SOURCE_PATHS
    candidates: list[SourceCandidate] = []
    for name, source_paths in paths.items():
        for source_path in source_paths:
            resolved_path = Path(source_path)
            exists = resolved_path.exists()
            files = discover_source_files(name, resolved_path) if exists else []
            candidates.append(SourceCandidate(name=name, path=resolved_path, exists=exists, files=files))
    return candidates


def generate_source_inventory(sources: list[SourceCandidate]) -> dict[str, object]:
    inventory = []
    for source in sources:
        sizes = [item.stat().st_size for item in source.files if item.exists()]
        inventory.append(
            {
                "name": source.name,
                "path": str(source.path),
                "exists": source.exists,
                "fileCount": len(source.files),
                "sizeBytes": sum(sizes),
                "parseReady": source.exists and bool(source.files),
                "sensitivityHints": ["conversation_records"] if source.exists else [],
            }
        )
    return {"sources": inventory}


def parse_sources(sources: list[SourceCandidate]) -> tuple[list[ConversationSession], list[ParseFailure]]:
    sessions: list[ConversationSession] = []
    failures: list[ParseFailure] = []
    for source in sources:
        for file_path in source.files:
            try:
                sessions.extend(parse_source_file(source.name, file_path))
            except Exception as exc:
                failures.append(ParseFailure(source=source.name, path=str(file_path), reason=str(exc)))
    return sessions, failures


def discover_source_files(source_name: str, source_path: Path) -> list[Path]:
    if source_name == "codex":
        session_root = source_path / "sessions"
        if session_root.exists():
            return sorted(session_root.rglob("*.jsonl"))
    if source_name == "claude_code":
        files: list[Path] = []
        project_root = source_path / "projects"
        transcript_root = source_path / "transcripts"
        if project_root.exists():
            files.extend(sorted(project_root.rglob("*.jsonl")))
        if transcript_root.exists():
            files.extend(sorted(transcript_root.glob("*.jsonl")))
        if files:
            return files
    if source_name == "opencode":
        database = source_path / "opencode.db"
        if database.exists():
            return [database]
        storage_files = []
        for child in ("session", "message", "part"):
            storage_root = source_path / "storage" / child
            if storage_root.exists():
                storage_files.extend(sorted(storage_root.rglob("*.json")))
        if storage_files:
            return storage_files
    return sorted(item for item in source_path.rglob("*.json") if not should_ignore_source_file(source_name, item))


def parse_source_file(source_name: str, file_path: Path) -> list[ConversationSession]:
    if source_name == "codex" and file_path.suffix == ".jsonl":
        return [_parse_codex_jsonl(file_path)]
    if source_name == "claude_code" and file_path.suffix == ".jsonl":
        return [_parse_claude_jsonl(file_path)]
    if source_name == "opencode" and file_path.name == "opencode.db":
        return _parse_opencode_sqlite(file_path)
    record = read_json(file_path)
    return [_parse_record(source_name, file_path, record)]


def _parse_record(source_name: str, file_path: Path, record: dict[str, object]) -> ConversationSession:
    source = str(record.get("source") or source_name)
    messages = list(record.get("messages") or [])
    tool_calls = list(record.get("toolCalls") or [])
    referenced_files = list(record.get("referencedFiles") or [])
    project_paths = list(record.get("projectPaths") or [])
    started_at = str(record.get("startedAt") or "")
    ended_at = str(record.get("endedAt") or "")
    task_type = str(record.get("taskType") or "unknown")
    outcome = str(record.get("outcome") or "unknown")
    session_id = stable_id("sess", source, file_path, started_at, ended_at)
    return ConversationSession(
        id=session_id,
        source=source,
        started_at=started_at,
        ended_at=ended_at,
        messages=[item for item in messages if isinstance(item, dict)],
        tool_calls=[item for item in tool_calls if isinstance(item, dict)],
        referenced_files=[str(item) for item in referenced_files],
        project_paths=[str(item) for item in project_paths],
        task_type=task_type,
        outcome=outcome,
        source_ref=str(file_path),
    )


def _parse_codex_jsonl(file_path: Path) -> ConversationSession:
    messages: list[dict[str, str]] = []
    tool_calls: list[dict[str, str]] = []
    project_paths: list[str] = []
    started_at = ""
    ended_at = ""
    for item in _read_jsonl(file_path):
        timestamp = str(item.get("timestamp") or "")
        if timestamp and not started_at:
            started_at = timestamp
        if timestamp:
            ended_at = timestamp
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        if item.get("type") == "session_meta" and isinstance(payload, dict):
            cwd = payload.get("cwd")
            if cwd:
                project_paths.append(str(cwd))
        if not isinstance(payload, dict):
            continue
        payload_type = str(payload.get("type") or "")
        if payload_type == "message":
            role = str(payload.get("role") or "")
            content = _content_to_text(payload.get("content"))
            if role and content:
                messages.append({"role": role, "content": content})
        if payload_type in {"function_call", "tool_call"}:
            tool_calls.append({"name": str(payload.get("name") or payload.get("tool") or ""), "summary": _content_to_text(payload.get("arguments"))})
    session_id = stable_id("sess", "codex", file_path, started_at, ended_at)
    return ConversationSession(
        id=session_id,
        source="codex",
        started_at=started_at,
        ended_at=ended_at,
        messages=messages,
        tool_calls=tool_calls,
        referenced_files=[],
        project_paths=project_paths,
        task_type="unknown",
        outcome="unknown",
        source_ref=str(file_path),
    )


def _parse_claude_jsonl(file_path: Path) -> ConversationSession:
    messages: list[dict[str, str]] = []
    tool_calls: list[dict[str, str]] = []
    project_paths: list[str] = []
    started_at = ""
    ended_at = ""
    session_id_value = ""
    for item in _read_jsonl(file_path):
        timestamp = str(item.get("timestamp") or "")
        if timestamp and not started_at:
            started_at = timestamp
        if timestamp:
            ended_at = timestamp
        session_id_value = str(item.get("sessionId") or session_id_value)
        cwd = item.get("cwd")
        if cwd:
            project_paths.append(str(cwd))
        item_type = str(item.get("type") or "")
        message = item.get("message") if isinstance(item.get("message"), dict) else {}
        if item_type in {"user", "assistant"}:
            role = str(message.get("role") or item_type)
            content = _content_to_text(message.get("content") if message else item.get("content"))
            if content:
                messages.append({"role": role, "content": content})
        if item_type in {"tool_use", "tool_result"}:
            tool_calls.append({"name": str(item.get("tool_name") or item.get("name") or item_type), "summary": _content_to_text(item.get("tool_input") or item.get("tool_output"))})
    session_id = stable_id("sess", "claude_code", session_id_value or file_path, started_at, ended_at)
    return ConversationSession(
        id=session_id,
        source="claude_code",
        started_at=started_at,
        ended_at=ended_at,
        messages=messages,
        tool_calls=tool_calls,
        referenced_files=[],
        project_paths=sorted(set(project_paths)),
        task_type="unknown",
        outcome="unknown",
        source_ref=str(file_path),
    )


def _parse_opencode_sqlite(file_path: Path) -> list[ConversationSession]:
    connection = sqlite3.connect(f"file:{file_path}?mode=ro", uri=True)
    try:
        session_rows = connection.execute("select id, directory, title, time_created, time_updated from session").fetchall()
        message_rows = connection.execute("select id, session_id, time_created, data from message").fetchall()
        part_rows = connection.execute("select message_id, session_id, data from part").fetchall()
    finally:
        connection.close()
    messages_by_session: dict[str, list[dict[str, str]]] = {}
    role_by_message: dict[str, str] = {}
    for message_id, session_id, _time_created, data_text in message_rows:
        data = _loads_json_object(data_text)
        role_by_message[str(message_id)] = str(data.get("role") or "")
        messages_by_session.setdefault(str(session_id), [])
    for message_id, session_id, data_text in part_rows:
        data = _loads_json_object(data_text)
        text = _content_to_text(data.get("text"))
        if not text:
            continue
        role = role_by_message.get(str(message_id)) or "unknown"
        messages_by_session.setdefault(str(session_id), []).append({"role": role, "content": text})
    sessions = []
    for session_id, directory, title, time_created, time_updated in session_rows:
        session_messages = messages_by_session.get(str(session_id), [])
        if not session_messages:
            continue
        sessions.append(
            ConversationSession(
                id=stable_id("sess", "opencode", session_id),
                source="opencode",
                started_at=str(time_created or ""),
                ended_at=str(time_updated or ""),
                messages=session_messages,
                tool_calls=[],
                referenced_files=[],
                project_paths=[str(directory)] if directory else [],
                task_type="unknown",
                outcome=str(title or "unknown"),
                source_ref=f"{file_path}#{session_id}",
            )
        )
    return sessions


def should_ignore_source_file(source_name: str, path: Path) -> bool:
    parts = set(path.parts)
    if source_name == "codex":
        if "skills" in parts and path.name == "test-prompts.json":
            return True
        return ".sandbox" in parts or ".sandbox-secrets" in parts
    if source_name == "claude_code":
        if "telemetry" in parts or "todos" in parts or "node_modules" in parts:
            return True
        return "plugins" in parts and "evals" in parts
    if source_name == "opencode":
        if path.name == "auth.json":
            return True
        return "node_modules" in parts or "session_diff" in parts
    return False


def _read_jsonl(file_path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line in file_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _content_to_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        chunks = []
        for item in value:
            if isinstance(item, dict):
                chunks.append(str(item.get("text") or item.get("content") or ""))
            else:
                chunks.append(str(item))
        return "\n".join(chunk for chunk in chunks if chunk)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _loads_json_object(text: object) -> dict[str, object]:
    if not isinstance(text, str):
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
