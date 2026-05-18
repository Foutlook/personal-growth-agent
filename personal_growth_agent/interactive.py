from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .analyzer import resolve_provider_credential, resolve_provider_route
from .chat_provider import ChatMessage, ChatRequest, stream_chat_provider
from .config import AppConfig, ResolvedPaths, load_config, resolve_paths
from .interactive_tools import (
    ToolContext,
    execute_tool,
    format_pages,
    format_tasks,
    get_latest_report,
    list_growth_tasks,
    list_knowledge_gaps,
    list_wiki_pages,
    sanitize_arguments,
    summarize_tool_result,
)
from .utils import utc_now_iso


@dataclass
class InteractiveContext:
    paths: ResolvedPaths
    config: AppConfig
    session_id: str

    @classmethod
    def from_workspace(cls, workspace: Path, wiki_root: Path, config_path: Path, session_id: str = "") -> "InteractiveContext":
        config = load_config(config_path)
        paths = resolve_paths(config=config, workspace_arg=workspace, wiki_arg=wiki_root, config_arg=config_path)
        resolved_session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
        return cls(paths=paths, config=config, session_id=resolved_session_id)


@dataclass
class SlashCommandResult:
    output: str
    exit_requested: bool = False


class ConversationLog:
    def __init__(self, workspace: Path, session_id: str = "") -> None:
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
        self.path = workspace / "conversations" / utc_now_iso()[:10] / f"{self.session_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record_type: str, payload: dict[str, Any]) -> None:
        record = {"type": record_type, "timestamp": utc_now_iso(), "payload": self._sanitize_payload(payload)}
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "arguments" in payload and isinstance(payload["arguments"], dict):
            sanitized = dict(payload)
            sanitized["arguments"] = sanitize_arguments(payload["arguments"])
            return sanitized
        return summarize_tool_result(payload)


def run_interactive(
    context: InteractiveContext,
    input_reader: Callable[[], str] | None = None,
    output_writer: Callable[[str], None] | None = None,
    chat_transport: Any | None = None,
) -> int:
    writer = output_writer or _terminal_write
    log = ConversationLog(context.paths.workspace, context.session_id)
    session_messages: list[ChatMessage] = []
    if input_reader is not None:
        return _run_input_loop(context, input_reader, writer, log, chat_transport, session_messages)
    writer("Personal Growth Agent interactive mode. 输入 /help 查看命令，/exit 退出。")
    prompt = _prompt_reader()
    while True:
        try:
            user_input = prompt()
        except EOFError:
            return 0
        stripped = user_input.strip()
        if not stripped:
            continue
        result = _handle_input(context, stripped, writer, log, chat_transport, session_messages)
        if result.exit_requested:
            return 0


def dispatch_slash_command(command: str, context: InteractiveContext) -> SlashCommandResult:
    parts = command.strip().split()
    name = parts[0] if parts else ""
    if name == "/help":
        return SlashCommandResult(output=_help_text())
    if name in {"/exit", "/quit"}:
        return SlashCommandResult(output="bye", exit_requested=True)
    if name == "/tasks":
        tasks = list_growth_tasks(context.paths.wiki)
        return SlashCommandResult(output=format_tasks(tasks))
    if name == "/task" and len(parts) >= 3 and parts[1] == "complete":
        tool_context = _tool_context(context)
        tool_result = execute_tool("complete_growth_task", {"task_id": parts[2]}, tool_context)
        if tool_result.status != "ok":
            return SlashCommandResult(output=tool_result.error)
        return SlashCommandResult(output=str(tool_result.result.get("task_id") or ""))
    if name == "/wiki":
        pages = list_wiki_pages(context.paths.wiki)
        return SlashCommandResult(output=format_pages("Wiki 页面", pages))
    if name == "/gaps":
        gaps = list_knowledge_gaps(context.paths.wiki)
        return SlashCommandResult(output=format_pages("知识缺口", gaps))
    if name == "/summary":
        report = get_latest_report(context.paths.workspace)
        if not report.get("path"):
            return SlashCommandResult(output="暂无报告。")
        return SlashCommandResult(output=f"{report.get('title')}\n{report.get('summary')}\n{report.get('path')}")
    if name == "/run":
        tool_result = execute_tool("run_growth_cycle", {}, _tool_context(context))
        if tool_result.status != "ok":
            return SlashCommandResult(output=tool_result.error)
        return SlashCommandResult(output=json.dumps(tool_result.result, ensure_ascii=False))
    if name == "/dashboard":
        tool_result = execute_tool("build_open_dashboard", {}, _tool_context(context))
        if tool_result.status != "ok":
            return SlashCommandResult(output=tool_result.error)
        return SlashCommandResult(output=json.dumps(tool_result.result, ensure_ascii=False))
    return SlashCommandResult(output=f"未知命令：{name}")


def _run_input_loop(
    context: InteractiveContext,
    input_reader: Callable[[], str],
    writer: Callable[[str], None],
    log: ConversationLog,
    chat_transport: Any | None,
    session_messages: list[ChatMessage],
) -> int:
    while True:
        try:
            user_input = input_reader()
        except (EOFError, StopIteration):
            return 0
        stripped = user_input.strip()
        if not stripped:
            continue
        result = _handle_input(context, stripped, writer, log, chat_transport, session_messages)
        if result.exit_requested:
            return 0


def _handle_input(
    context: InteractiveContext,
    user_input: str,
    writer: Callable[[str], None],
    log: ConversationLog,
    chat_transport: Any | None,
    session_messages: list[ChatMessage],
) -> SlashCommandResult:
    log.append("user", {"content": user_input})
    if user_input.startswith("/"):
        result = dispatch_slash_command(user_input, context)
        writer(result.output)
        log.append("command", {"content": user_input, "result": result.output})
        return result
    assistant_text = _run_chat_turn(context, user_input, writer, log, chat_transport, session_messages)
    log.append("assistant", {"content": assistant_text})
    return SlashCommandResult(output=assistant_text)


def _run_chat_turn(
    context: InteractiveContext,
    user_input: str,
    writer: Callable[[str], None],
    log: ConversationLog,
    chat_transport: Any | None,
    session_messages: list[ChatMessage],
) -> str:
    route = resolve_provider_route(context.config.llm, "interactive_chat")
    credential = resolve_provider_credential(route)
    messages = list(session_messages)
    messages.append(ChatMessage(role="user", content=user_input))
    assistant_parts = []
    exhausted_tool_rounds = False
    tool_cache: dict[str, dict[str, Any]] = {}
    for round_index in range(6):
        request_messages = _provider_messages(context, messages)
        chat_request = ChatRequest(messages=request_messages, tools=_tool_specs(), context=_chat_context(context))
        tool_messages = []
        reasoning_parts = []
        for chunk in stream_chat_provider(route, chat_request, credential, transport=chat_transport):
            if chunk.type == "text":
                writer(chunk.content)
                assistant_parts.append(chunk.content)
                continue
            if chunk.type == "reasoning":
                reasoning_parts.append(chunk.reasoning_content)
                continue
            if chunk.type == "tool_call":
                tool_message = _handle_tool_call(context, chunk.tool_call, writer, log, tool_cache)
                if tool_message:
                    tool_messages.append(tool_message)
                continue
            writer(chunk.content)
            log.append("error", {"content": chunk.content})
        if not tool_messages:
            break
        messages.append(ChatMessage(role="assistant", content="", tool_calls=[message.tool_call for message in tool_messages], reasoning_content="".join(reasoning_parts)))
        messages.extend(tool_messages)
        exhausted_tool_rounds = round_index == 5
    if exhausted_tool_rounds and not assistant_parts:
        assistant_parts.extend(_force_final_answer(context, route, credential, messages, writer, log, chat_transport))
    assistant_text = "".join(assistant_parts)
    messages.append(ChatMessage(role="assistant", content=assistant_text))
    session_messages[:] = messages[-20:]
    return assistant_text


def _force_final_answer(
    context: InteractiveContext,
    route,
    credential,
    messages: list[ChatMessage],
    writer: Callable[[str], None],
    log: ConversationLog,
    chat_transport: Any | None,
) -> list[str]:
    messages.append(ChatMessage(role="user", content="请停止调用工具，直接基于以上工具结果给出最终回答。"))
    chat_request = ChatRequest(messages=_provider_messages(context, messages), tools=[], context={})
    parts = []
    for chunk in stream_chat_provider(route, chat_request, credential, transport=chat_transport):
        if chunk.type == "text":
            writer(chunk.content)
            parts.append(chunk.content)
            continue
        if chunk.type == "reasoning":
            continue
        if chunk.type == "tool_call":
            log.append("tool_call_rejected_after_limit", {"name": chunk.tool_call.get("name") or "", "arguments": chunk.tool_call.get("arguments") or {}})
            continue
        writer(chunk.content)
        log.append("error", {"content": chunk.content})
    return parts


def _handle_tool_call(
    context: InteractiveContext,
    tool_call: dict[str, Any],
    writer: Callable[[str], None],
    log: ConversationLog,
    tool_cache: dict[str, dict[str, Any]] | None = None,
) -> ChatMessage | None:
    tool_name = str(tool_call.get("name") or "")
    if not tool_name:
        return None
    arguments = tool_call.get("arguments") if isinstance(tool_call.get("arguments"), dict) else {}
    log.append("tool_call", {"name": tool_name, "arguments": arguments})
    cache_key = _tool_cache_key(tool_name, arguments)
    if tool_cache is not None and cache_key in tool_cache:
        cached_payload = tool_cache[cache_key]
        tool_payload = {
            "status": "cached",
            "result": cached_payload.get("result"),
            "error": "",
            "note": "同名同参工具已在本轮调用过，请直接基于已有结果回答。",
        }
        log.append("tool_result", {"name": tool_name, "status": "cached", "result": tool_payload["result"], "error": ""})
        writer(f"\n[tool:{tool_name}] cached\n")
        tool_call_id = str(tool_call.get("id") or tool_name)
        return ChatMessage(
            role="tool",
            content=json.dumps(tool_payload, ensure_ascii=False),
            name=tool_name,
            tool_call_id=tool_call_id,
            tool_call={"id": tool_call_id, "name": tool_name, "arguments": arguments},
        )
    tool_result = execute_tool(tool_name, arguments, _tool_context(context))
    result_summary = summarize_tool_result(tool_result.result)
    log.append("tool_result", {"name": tool_name, "status": tool_result.status, "result": result_summary, "error": tool_result.error})
    writer(f"\n[tool:{tool_name}] {tool_result.status}\n")
    tool_payload = {"status": tool_result.status, "result": result_summary, "error": tool_result.error}
    if tool_cache is not None:
        tool_cache[cache_key] = tool_payload
    tool_call_id = str(tool_call.get("id") or tool_name)
    return ChatMessage(
        role="tool",
        content=json.dumps(tool_payload, ensure_ascii=False),
        name=tool_name,
        tool_call_id=tool_call_id,
        tool_call={"id": tool_call_id, "name": tool_name, "arguments": arguments},
    )


def _provider_messages(context: InteractiveContext, messages: list[ChatMessage]) -> list[ChatMessage]:
    return [ChatMessage(role="system", content=_chat_system_prompt(context)), *messages]


def _chat_system_prompt(context: InteractiveContext) -> str:
    chat_context = _chat_context(context)
    context_text = json.dumps(chat_context, ensure_ascii=False)
    return "\n".join(
        [
            "你是 Personal Growth Agent 的交互式对话助手。",
            "自由对话时直接回答用户；只有缺少本地成长数据时才调用工具。",
            "不要在同一个用户问题中重复调用同名同参工具；如果工具结果已经返回，请基于已有结果总结和建议。",
            "工具结果足够回答时，必须停止调用工具并输出最终回答。",
            "对话记录只用于当前会话留存，不要要求写入 wiki。",
            f"当前本地上下文：{context_text}",
        ]
    )


def _tool_cache_key(tool_name: str, arguments: dict[str, Any]) -> str:
    arguments_text = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
    return f"{tool_name}:{arguments_text}"


def _tool_context(context: InteractiveContext) -> ToolContext:
    return ToolContext(context.paths.workspace, context.paths.wiki, context.paths.config, source_paths=_paths_from_config(context.config), run_constraints=_run_constraints(context))


def _chat_context(context: InteractiveContext) -> dict[str, Any]:
    return {
        "latestReport": get_latest_report(context.paths.workspace),
        "activeTasks": list_growth_tasks(context.paths.wiki),
        "wikiPages": list_wiki_pages(context.paths.wiki)[:30],
        "knowledgeGaps": list_knowledge_gaps(context.paths.wiki)[:30],
    }


def _tool_specs() -> list[dict[str, Any]]:
    names = [
        "get_latest_report",
        "list_growth_tasks",
        "complete_growth_task",
        "list_wiki_pages",
        "read_wiki_page",
        "list_knowledge_gaps",
        "run_growth_cycle",
        "build_open_dashboard",
    ]
    return [{"name": name, "description": name, "parameters": {"type": "object", "properties": {}}} for name in names]


def _paths_from_config(config: AppConfig) -> dict[str, list[Path]]:
    return {name: source.paths for name, source in config.sources.items() if source.enabled}


def _run_constraints(context: InteractiveContext) -> dict[str, object]:
    return {
        "weeklyTimeBudgetHours": 3,
        "currentFocus": "balanced",
        "provider": context.config.llm.default_provider or context.config.provider.provider,
        "model": context.config.llm.default_model or context.config.provider.model,
        "analysisMode": context.config.llm.default_analysis_mode or context.config.provider.analysis_mode,
        "promptDir": context.config.llm.prompt_dir,
        "llmConfig": context.config.llm,
        "dryRun": False,
        "approveOutbound": context.config.provider.approve_outbound or context.config.llm.approve_outbound,
    }


def _help_text() -> str:
    return "\n".join(
        [
            "可用命令：",
            "/help - 查看命令说明",
            "/tasks - 查看当前 active 成长任务",
            "/task complete <task-id> - 完成指定成长任务",
            "/wiki - 查看本地 Wiki 页面索引",
            "/gaps - 查看当前知识缺口",
            "/summary - 查看最新报告摘要",
            "/run - 运行一次成长分析周期",
            "/dashboard - 生成并打开个人成长仪表盘",
            "/exit - 退出交互模式",
            "/quit - 退出交互模式",
        ]
    )


def _prompt_reader() -> Callable[[], str]:
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory

        history_path = Path.home() / ".pga-history"
        session = PromptSession(history=FileHistory(str(history_path)))
        return lambda: session.prompt("pga> ")
    except Exception:
        return lambda: input("pga> ")


def _terminal_write(text: str) -> None:
    print(text, end="", flush=True)
