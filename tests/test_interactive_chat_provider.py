import json
import unittest

from personal_growth_agent.chat_provider import (
    ChatMessage,
    ChatRequest,
    build_chat_provider_request,
    stream_chat_provider,
)
from personal_growth_agent.config import load_config
from personal_growth_agent.analyzer import resolve_provider_credential, resolve_provider_route, validate_llm_analysis


class InteractiveChatProviderTests(unittest.TestCase):
    def test_build_chat_request_reuses_provider_route_without_leaking_secret(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat", model_override="flash")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "secret-value"})
        request = ChatRequest(messages=[ChatMessage(role="user", content="你好")], tools=[{"name": "list_growth_tasks"}])

        provider_request = build_chat_provider_request(route, request, credential, stream=True)
        request_text = json.dumps(provider_request, ensure_ascii=False)

        self.assertEqual(provider_request["body"]["model"], "deepseek-v4-flash")
        self.assertTrue(provider_request["body"]["stream"])
        self.assertIn("tools", provider_request["body"])
        self.assertNotIn("secret-value", request_text)

    def test_missing_credentials_return_user_message_without_network_call(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat")
        credential = resolve_provider_credential(route, env={})
        request = ChatRequest(messages=[ChatMessage(role="user", content="总结")])

        chunks = list(stream_chat_provider(route, request, credential, transport=None))

        self.assertEqual(chunks[0].type, "error")
        self.assertIn("Missing API key", chunks[0].content)

    def test_stream_chat_provider_yields_text_and_tool_call_chunks(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "secret-value"})
        request = ChatRequest(messages=[ChatMessage(role="user", content="查任务")])

        def fake_transport(url, headers, body, timeout):
            return [
                {"choices": [{"delta": {"content": "我先查"}}]},
                {
                    "choices": [
                        {
                            "delta": {
                                "tool_calls": [
                                    {
                                        "id": "call_1",
                                        "function": {
                                            "name": "list_growth_tasks",
                                            "arguments": "{}",
                                        },
                                    }
                                ]
                            }
                        }
                    ]
                },
                {"choices": [{"delta": {"content": "完成"}}]},
            ]

        chunks = list(stream_chat_provider(route, request, credential, transport=fake_transport))

        self.assertEqual([chunk.type for chunk in chunks], ["text", "tool_call", "text"])
        self.assertEqual(chunks[1].tool_call["name"], "list_growth_tasks")
        self.assertEqual(chunks[0].content, "我先查")

    def test_non_streaming_response_uses_same_chunk_interface(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "secret-value"})
        request = ChatRequest(messages=[ChatMessage(role="user", content="总结")])

        def fake_transport(url, headers, body, timeout):
            return {"choices": [{"message": {"content": "最终回答"}}]}

        chunks = list(stream_chat_provider(route, request, credential, transport=fake_transport, stream=False))

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].type, "text")
        self.assertEqual(chunks[0].content, "最终回答")

    def test_provider_errors_are_returned_as_error_chunks(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "secret-value"})
        request = ChatRequest(messages=[ChatMessage(role="user", content="总结")])

        def fake_transport(url, headers, body, timeout):
            raise RuntimeError("provider HTTP 400: bad request")

        chunks = list(stream_chat_provider(route, request, credential, transport=fake_transport))

        self.assertEqual(chunks[0].type, "error")
        self.assertIn("provider HTTP 400", chunks[0].content)

    def test_stream_chat_provider_yields_chunks_from_iterable_response_incrementally(self):
        route = resolve_provider_route(load_config(None).llm, scenario="interactive_chat")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "secret-value"})
        request = ChatRequest(messages=[ChatMessage(role="user", content="总结")])
        consumed = []

        def response_items():
            consumed.append("first")
            yield {"choices": [{"delta": {"content": "第一段"}}]}
            consumed.append("second")
            yield {"choices": [{"delta": {"content": "第二段"}}]}

        def fake_transport(url, headers, body, timeout):
            return response_items()

        chunks = stream_chat_provider(route, request, credential, transport=fake_transport)
        first_chunk = next(chunks)

        self.assertEqual(first_chunk.content, "第一段")
        self.assertEqual(consumed, ["first"])

    def test_existing_analyzer_validation_remains_strict_json_contract(self):
        with self.assertRaises(ValueError):
            validate_llm_analysis({"candidateSignals": [{"name": "missing evidence"}]}, {"ev_1"})


if __name__ == "__main__":
    unittest.main()
