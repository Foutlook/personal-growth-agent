from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Iterable as IterableABC
from dataclasses import dataclass, field
from typing import Any, Iterable

from .analyzer import ProviderCredential, ProviderRoute


@dataclass
class ChatMessage:
    role: str
    content: str
    name: str = ""
    tool_call_id: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call: dict[str, Any] = field(default_factory=dict)
    reasoning_content: str = ""


@dataclass
class ChatRequest:
    messages: list[ChatMessage]
    tools: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatChunk:
    type: str
    content: str = ""
    tool_call: dict[str, Any] = field(default_factory=dict)
    reasoning_content: str = ""


def build_chat_provider_request(route: ProviderRoute, request: ChatRequest, credential: ProviderCredential, stream: bool = True) -> dict[str, Any]:
    body = {
        "model": route.model,
        "messages": [_message_to_payload(message) for message in request.messages],
        "stream": stream,
    }
    if request.tools:
        body["tools"] = [_tool_to_provider_payload(tool) for tool in request.tools]
    if request.context:
        body["metadata"] = {"contextKeys": sorted(str(key) for key in request.context)}
    return {
        "provider": route.provider,
        "baseUrl": route.base_url,
        "apiKeyEnv": route.api_key_env,
        "credentialSource": credential.source,
        "timeoutSeconds": route.timeout_seconds,
        "body": body,
    }


def stream_chat_provider(
    route: ProviderRoute,
    request: ChatRequest,
    credential: ProviderCredential,
    transport: Any | None = None,
    stream: bool = True,
) -> Iterable[ChatChunk]:
    if not credential.available:
        yield ChatChunk(type="error", content=credential.message)
        return
    if route.provider not in {"deepseek", "openai", "openai-compatible"}:
        yield ChatChunk(type="error", content=f"unsupported provider: {route.provider}")
        return
    provider_request = build_chat_provider_request(route, request, credential, stream=stream)
    url = _chat_completions_url(route.base_url)
    headers = {"Authorization": f"Bearer {credential.value}", "Content-Type": "application/json"}
    body = provider_request["body"]
    try:
        response = transport(url, headers, body, route.timeout_seconds) if transport else _urlopen_chat(url, headers, body, route.timeout_seconds, stream)
    except Exception as exc:
        yield ChatChunk(type="error", content=str(exc))
        return
    if stream and _is_stream_response(response):
        for item in response:
            chunk = _chunk_from_stream_item(item)
            if chunk is not None:
                yield chunk
        return
    yield _chunk_from_final_response(response)


def _message_to_payload(message: ChatMessage) -> dict[str, Any]:
    payload = {"role": message.role, "content": message.content}
    if message.name:
        payload["name"] = message.name
    if message.tool_call_id:
        payload["tool_call_id"] = message.tool_call_id
    if message.tool_calls:
        payload["tool_calls"] = [_tool_call_to_payload(tool_call) for tool_call in message.tool_calls]
    if message.reasoning_content:
        payload["reasoning_content"] = message.reasoning_content
    return payload


def _tool_call_to_payload(tool_call: dict[str, Any]) -> dict[str, Any]:
    arguments = tool_call.get("arguments") if isinstance(tool_call.get("arguments"), dict) else {}
    return {
        "id": tool_call.get("id") or tool_call.get("name") or "",
        "type": "function",
        "function": {
            "name": tool_call.get("name") or "",
            "arguments": json.dumps(arguments, ensure_ascii=False),
        },
    }


def _tool_to_provider_payload(tool: dict[str, Any]) -> dict[str, Any]:
    name = str(tool.get("name") or "")
    description = str(tool.get("description") or name)
    parameters = tool.get("parameters")
    if not isinstance(parameters, dict):
        parameters = {"type": "object", "properties": {}}
    return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}


def _chunk_from_stream_item(item: dict[str, Any]) -> ChatChunk | None:
    choices = item.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None
    delta = first_choice.get("delta") or {}
    if not isinstance(delta, dict):
        return None
    content = delta.get("content")
    if isinstance(content, str) and content:
        return ChatChunk(type="text", content=content)
    reasoning_content = delta.get("reasoning_content")
    if isinstance(reasoning_content, str) and reasoning_content:
        return ChatChunk(type="reasoning", reasoning_content=reasoning_content)
    tool_calls = delta.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        first_call = tool_calls[0]
        if isinstance(first_call, dict):
            tool_call = _normalize_tool_call(first_call)
            if tool_call["name"]:
                return ChatChunk(type="tool_call", tool_call=tool_call)
    return None


def _chunk_from_final_response(response: Any) -> ChatChunk:
    if not isinstance(response, dict):
        return ChatChunk(type="error", content="provider response must be an object")
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ChatChunk(type="error", content="provider response missing choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ChatChunk(type="error", content="provider choice must be an object")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        return ChatChunk(type="error", content="provider response missing message")
    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        first_call = tool_calls[0]
        if isinstance(first_call, dict):
            return ChatChunk(type="tool_call", tool_call=_normalize_tool_call(first_call))
    content = message.get("content")
    return ChatChunk(type="text", content=str(content or ""))


def _is_stream_response(response: Any) -> bool:
    if isinstance(response, (str, bytes, dict)):
        return False
    return isinstance(response, IterableABC)


def _normalize_tool_call(raw_call: dict[str, Any]) -> dict[str, Any]:
    function = raw_call.get("function")
    if not isinstance(function, dict):
        function = {}
    arguments_text = str(function.get("arguments") or "{}")
    try:
        arguments = json.loads(arguments_text)
    except json.JSONDecodeError:
        arguments = {}
    if not isinstance(arguments, dict):
        arguments = {}
    return {"id": raw_call.get("id") or "", "name": function.get("name") or "", "arguments": arguments}


def _chat_completions_url(base_url: str) -> str:
    normalized = (base_url or "").rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _urlopen_chat(url: str, headers: dict[str, str], body: dict[str, Any], timeout_seconds: int, stream: bool) -> Any:
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
    if stream:
        return _open_sse_json(request, timeout_seconds)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_text = response.read().decode("utf-8")
            return json.loads(response_text)
    except urllib.error.HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"provider HTTP {exc.code}: {error_text}") from exc


def _open_sse_json(request: urllib.request.Request, timeout_seconds: int) -> Iterable[dict[str, Any]]:
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data: "):
                    continue
                data = line.removeprefix("data: ").strip()
                if data == "[DONE]":
                    break
                value = json.loads(data)
                if isinstance(value, dict):
                    yield value
    except urllib.error.HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"provider HTTP {exc.code}: {error_text}") from exc
