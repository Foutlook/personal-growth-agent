import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from personal_growth_agent.cli import main
from personal_growth_agent.config import write_default_config
from personal_growth_agent.interactive import (
    ConversationLog,
    InteractiveContext,
    dispatch_slash_command,
    run_interactive,
)
from personal_growth_agent.interactive_tools import ToolContext, execute_tool, list_tool_names
from personal_growth_agent.wiki import init_llm_wiki


class InteractiveReplTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.workspace = self.tmp / "workspace"
        self.wiki_root = self.workspace / "llm-wiki"
        self.config_path = self.workspace / "config.toml"
        write_default_config(self.config_path, self.workspace)
        init_llm_wiki(self.wiki_root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cli_without_subcommand_uses_injected_interactive_runner(self):
        captured = {}

        def fake_runner(context):
            captured["workspace"] = context.paths.workspace
            captured["wiki"] = context.paths.wiki
            return 17

        code = main(["--workspace", str(self.workspace)], interactive_runner=fake_runner)

        self.assertEqual(code, 17)
        self.assertEqual(captured["workspace"], self.workspace)
        self.assertEqual(captured["wiki"], self.wiki_root)

    def test_existing_subcommands_still_work_with_interactive_runner_available(self):
        called = {"value": False}

        def fake_runner(context):
            called["value"] = True
            return 99

        code = main(["--workspace", str(self.workspace), "wiki", "path"], interactive_runner=fake_runner)

        self.assertEqual(code, 0)
        self.assertFalse(called["value"])

    def test_run_interactive_routes_slash_commands_and_exits_without_chat(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path)
        outputs = []
        inputs = iter(["/help"])

        def input_reader():
            return next(inputs)

        code = run_interactive(context, input_reader=input_reader, output_writer=outputs.append)

        self.assertEqual(code, 0)
        joined = "\n".join(outputs)
        self.assertIn("/tasks - 查看当前 active 成长任务", joined)
        self.assertIn("/exit - 退出交互模式", joined)

    def test_conversation_log_writes_jsonl_outside_wiki_without_manifest_side_effect(self):
        log = ConversationLog(self.workspace, session_id="session-test")
        log.append("user", {"content": "hello"})
        log.append("tool_call", {"name": "list_growth_tasks", "arguments": {"api_key": "secret-value"}})
        records = [json.loads(line) for line in log.path.read_text(encoding="utf-8").splitlines()]
        manifest_path = self.wiki_root / "data" / "source-manifest.json"
        raw_bytes = log.path.read_bytes()

        self.assertTrue(str(log.path).startswith(str(self.workspace / "conversations")))
        self.assertNotIn("llm-wiki", str(log.path))
        self.assertEqual(records[0]["type"], "user")
        self.assertEqual(records[1]["payload"]["arguments"]["api_key"], "[REDACTED]")
        self.assertFalse(manifest_path.exists())
        self.assertFalse(raw_bytes.startswith(b"\xef\xbb\xbf"))

    def test_slash_commands_read_tasks_complete_task_and_indexes_local_data(self):
        tasks_root = self.wiki_root / "data" / "growth-tasks"
        tasks_root.mkdir(parents=True)
        active_path = tasks_root / "active.json"
        active_path.write_text(
            json.dumps([{"id": "task_1", "title": "补齐验收标准", "status": "active"}], ensure_ascii=False),
            encoding="utf-8",
        )
        wiki_page = self.wiki_root / "wiki" / "knowledge" / "concepts" / "agent.md"
        wiki_page.parent.mkdir(parents=True)
        wiki_page.write_text("---\ntype: knowledge_page\nstatus: ready\n---\n# Agent Knowledge\n", encoding="utf-8")
        gap_page = self.wiki_root / "wiki" / "knowledge" / "gaps" / "gap.md"
        gap_page.parent.mkdir(parents=True)
        gap_page.write_text("---\ntype: knowledge_gap\nstatus: draft\n---\n# Gap\n", encoding="utf-8")
        report_dir = self.workspace / "runs" / "2026-05-18"
        report_dir.mkdir(parents=True)
        (report_dir / "report.md").write_text("# 今日报告\n\n这是摘要内容。", encoding="utf-8")
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path)

        tasks_result = dispatch_slash_command("/tasks", context)
        complete_result = dispatch_slash_command("/task complete task_1", context)
        wiki_result = dispatch_slash_command("/wiki", context)
        gaps_result = dispatch_slash_command("/gaps", context)
        summary_result = dispatch_slash_command("/summary", context)

        archived = json.loads((tasks_root / "archive.json").read_text(encoding="utf-8"))
        self.assertIn("补齐验收标准", tasks_result.output)
        self.assertIn("task_1", complete_result.output)
        self.assertIn("Agent Knowledge", wiki_result.output)
        self.assertIn("Gap", gaps_result.output)
        self.assertIn("今日报告", summary_result.output)
        self.assertEqual(archived[0]["status"], "completed")

    def test_tool_registry_allows_only_whitelisted_tools_and_sanitizes_results(self):
        names = list_tool_names()
        context = ToolContext(self.workspace, self.wiki_root, self.config_path)
        report_dir = self.workspace / "runs" / "2026-05-18"
        report_dir.mkdir(parents=True)
        (report_dir / "report.md").write_text("# Report\n\nprivate key should not leak", encoding="utf-8")

        allowed = execute_tool("get_latest_report", {}, context)
        rejected = execute_tool("shell", {"command": "dir"}, context)

        self.assertIn("get_latest_report", names)
        self.assertIn("build_open_dashboard", names)
        self.assertEqual(allowed.status, "ok")
        self.assertNotIn("private key", json.dumps(allowed.result, ensure_ascii=False))
        self.assertEqual(rejected.status, "rejected")

    def test_run_tool_uses_context_source_paths_and_constraints(self):
        captured = {}

        def fake_runner(source_paths, output_root, constraints):
            captured["source_paths"] = source_paths
            captured["output_root"] = output_root
            captured["constraints"] = constraints
            return {"run_dir": str(output_root / "runs" / "fake"), "wiki_root": str(output_root / "llm-wiki")}

        context = ToolContext(
            self.workspace,
            self.wiki_root,
            self.config_path,
            source_paths={"codex": [self.tmp / "codex"]},
            run_constraints={"weeklyTimeBudgetHours": 5, "currentFocus": "balanced"},
            growth_runner=fake_runner,
        )
        result = execute_tool("run_growth_cycle", {}, context)

        self.assertEqual(result.status, "ok")
        self.assertEqual(captured["source_paths"], {"codex": [self.tmp / "codex"]})
        self.assertEqual(captured["constraints"]["weeklyTimeBudgetHours"], 5)

    def test_free_form_chat_streams_tool_call_and_records_session(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="chat-session")
        tasks_root = self.wiki_root / "data" / "growth-tasks"
        tasks_root.mkdir(parents=True)
        (tasks_root / "active.json").write_text(
            json.dumps([{"id": "task_1", "title": "写验收标准", "status": "active"}], ensure_ascii=False),
            encoding="utf-8",
        )
        outputs = []

        def fake_transport(url, headers, body, timeout):
            return [
                {"choices": [{"delta": {"content": "我先查看任务。"}}]},
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
                {"choices": [{"delta": {"content": "建议先做验收标准。"}}]},
            ]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            code = run_interactive(
                context,
                input_reader=_one_input("我应该先做什么？"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key
        log_path = self.workspace / "conversations" / "2026-05-18" / "chat-session.jsonl"
        records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(code, 0)
        self.assertIn("我先查看任务。", "".join(outputs))
        self.assertTrue(any(record["type"] == "tool_call" for record in records))
        self.assertTrue(any(record["type"] == "tool_result" for record in records))
        self.assertFalse((self.wiki_root / "data" / "source-manifest.json").exists())

    def test_chat_continues_after_tool_call_and_streams_final_answer(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="tool-followup")
        call_count = {"value": 0}
        outputs = []

        def fake_transport(url, headers, body, timeout):
            call_count["value"] += 1
            if call_count["value"] == 1:
                return [
                    {
                        "choices": [
                            {
                                "delta": {
                                    "tool_calls": [
                                        {
                                            "id": "call_1",
                                            "function": {
                                                "name": "get_latest_report",
                                                "arguments": "{}",
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            roles = [message["role"] for message in body["messages"]]
            assistant_index = roles.index("assistant")
            tool_index = roles.index("tool")
            self.assertLess(assistant_index, tool_index)
            assistant_message = body["messages"][assistant_index]
            self.assertIn("tool_calls", assistant_message)
            self.assertEqual(assistant_message["tool_calls"][0]["id"], "call_1")
            return [{"choices": [{"delta": {"content": "最终建议：先补验收标准。"}}]}]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=_one_input("我最近最应该补哪块能力？"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key

        self.assertEqual(call_count["value"], 2)
        self.assertIn("最终建议：先补验收标准。", "".join(outputs))

    def test_chat_passes_reasoning_content_back_after_tool_call(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="reasoning-tool-followup")
        call_count = {"value": 0}
        outputs = []

        def fake_transport(url, headers, body, timeout):
            call_count["value"] += 1
            if call_count["value"] == 1:
                return [
                    {"choices": [{"delta": {"reasoning_content": "我需要先查知识缺口。"}}]},
                    {
                        "choices": [
                            {
                                "delta": {
                                    "tool_calls": [
                                        {
                                            "id": "call_1",
                                            "function": {
                                                "name": "list_knowledge_gaps",
                                                "arguments": "{}",
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                ]
            assistant_messages = [message for message in body["messages"] if message["role"] == "assistant"]
            self.assertTrue(assistant_messages)
            self.assertEqual(assistant_messages[-1]["reasoning_content"], "我需要先查知识缺口。")
            return [{"choices": [{"delta": {"content": "最终建议：先补知识缺口。"}}]}]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=_one_input("我最近最应该补哪块能力？"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key

        self.assertEqual(call_count["value"], 2)
        self.assertIn("最终建议：先补知识缺口。", "".join(outputs))

    def test_streamed_empty_tool_call_delta_is_not_executed_as_rejected_tool(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="empty-tool-delta")
        outputs = []

        def fake_transport(url, headers, body, timeout):
            return [
                {
                    "choices": [
                        {
                            "delta": {
                                "tool_calls": [
                                    {
                                        "id": "call_1",
                                        "function": {
                                            "name": "get_latest_report",
                                            "arguments": "{}",
                                        },
                                    }
                                ]
                            }
                        }
                    ]
                },
                {"choices": [{"delta": {"tool_calls": [{"function": {"arguments": ""}}]}}]},
                {"choices": [{"delta": {"tool_calls": [{"function": {}}]}}]},
            ]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=_one_input("看看我的报告"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key
        joined = "\n".join(outputs)
        log_path = self.workspace / "conversations" / "2026-05-18" / "empty-tool-delta.jsonl"
        records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]

        self.assertIn("[tool:get_latest_report] ok", joined)
        self.assertNotIn("[tool:] rejected", joined)
        self.assertFalse(any(record["type"] == "tool_call" and not record["payload"]["name"] for record in records))

    def test_interactive_session_preserves_chat_history_across_user_turns(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="continuous-session")
        prompts = iter(["第一轮问题", "第二轮追问", "/exit"])
        request_messages = []

        def fake_transport(url, headers, body, timeout):
            request_messages.append(body["messages"])
            if len(request_messages) == 1:
                return [{"choices": [{"delta": {"content": "第一轮回答"}}]}]
            return [{"choices": [{"delta": {"content": "第二轮回答"}}]}]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=lambda: next(prompts),
                output_writer=lambda text: None,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key

        second_request_text = json.dumps(request_messages[1], ensure_ascii=False)
        self.assertIn("第一轮问题", second_request_text)
        self.assertIn("第一轮回答", second_request_text)
        self.assertIn("第二轮追问", second_request_text)

    def test_chat_forces_final_answer_without_tools_after_tool_round_limit(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="tool-limit-final")
        call_count = {"value": 0}
        outputs = []

        def fake_transport(url, headers, body, timeout):
            call_count["value"] += 1
            if call_count["value"] <= 6:
                self.assertIn("tools", body)
                return [
                    {
                        "choices": [
                            {
                                "delta": {
                                    "tool_calls": [
                                        {
                                            "id": f"call_{call_count['value']}",
                                            "function": {
                                                "name": "get_latest_report",
                                                "arguments": "{}",
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            self.assertNotIn("tools", body)
            return [{"choices": [{"delta": {"content": "最终回答：先补验收标准。"}}]}]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=_one_input("我最近最应该补哪块能力？"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key

        self.assertEqual(call_count["value"], 7)
        self.assertIn("最终回答：先补验收标准。", "".join(outputs))

    def test_chat_sends_system_prompt_and_suppresses_duplicate_tool_execution(self):
        context = InteractiveContext.from_workspace(self.workspace, self.wiki_root, self.config_path, session_id="duplicate-tool")
        call_count = {"value": 0}
        outputs = []

        def fake_transport(url, headers, body, timeout):
            call_count["value"] += 1
            self.assertEqual(body["messages"][0]["role"], "system")
            self.assertIn("不要在同一个用户问题中重复调用同名同参工具", body["messages"][0]["content"])
            if call_count["value"] <= 2:
                return [
                    {
                        "choices": [
                            {
                                "delta": {
                                    "tool_calls": [
                                        {
                                            "id": f"call_{call_count['value']}",
                                            "function": {
                                                "name": "get_latest_report",
                                                "arguments": "{}",
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            return [{"choices": [{"delta": {"content": "最终回答：已有报告结果，下一步补验收标准。"}}]}]

        old_key = os.environ.get("PGA_DEEPSEEK_API_KEY")
        os.environ["PGA_DEEPSEEK_API_KEY"] = "test-key"
        try:
            run_interactive(
                context,
                input_reader=_one_input("看看我的报告并给建议"),
                output_writer=outputs.append,
                chat_transport=fake_transport,
            )
        finally:
            if old_key is None:
                os.environ.pop("PGA_DEEPSEEK_API_KEY", None)
            else:
                os.environ["PGA_DEEPSEEK_API_KEY"] = old_key
        log_path = self.workspace / "conversations" / "2026-05-18" / "duplicate-tool.jsonl"
        records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        tool_results = [record for record in records if record["type"] == "tool_result"]

        self.assertEqual(call_count["value"], 3)
        self.assertEqual(tool_results[0]["payload"]["status"], "ok")
        self.assertEqual(tool_results[1]["payload"]["status"], "cached")
        self.assertIn("[tool:get_latest_report] cached", "\n".join(outputs))
        self.assertIn("最终回答：已有报告结果", "".join(outputs))


if __name__ == "__main__":
    unittest.main()


def _one_input(value):
    values = iter([value])
    return lambda: next(values)
