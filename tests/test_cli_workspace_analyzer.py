import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from personal_growth_agent.analyzer import (
    AnalyzerConfig,
    AnalyzerRequest,
    LocalAnalyzerProvider,
    build_analyzer_payload,
    reconcile_signals,
    validate_llm_analysis,
)
from personal_growth_agent.cli import main
from personal_growth_agent.config import DEFAULT_WORKSPACE, load_config, resolve_paths, write_default_config
from personal_growth_agent.data import discover_sources, parse_sources
from personal_growth_agent.pipeline import run_growth_cycle
from personal_growth_agent.sources import ClaudeCodeAdapter, CodexAdapter, OpenCodeAdapter, scan_sources


FIXTURES = Path(__file__).parent / "fixtures"


class CliWorkspaceAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sources_root = self.tmp / "sources"
        shutil.copytree(FIXTURES / "conversations", self.sources_root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_workspace_config_roundtrip_and_resolution_order(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        config = load_config(config_path)
        paths = resolve_paths(config=config, workspace_arg=self.tmp / "override", wiki_arg=None, config_arg=config_path, env={})
        env_paths = resolve_paths(config=config, workspace_arg=None, wiki_arg=None, config_arg=config_path, env={"PGA_WORKSPACE": str(self.tmp / "env")})

        self.assertEqual(config.workspace, workspace)
        self.assertEqual(paths.workspace, self.tmp / "override")
        self.assertEqual(paths.wiki, self.tmp / "override" / "llm-wiki")
        self.assertEqual(env_paths.workspace, self.tmp / "env")

    def test_default_workspace_is_user_visible_pga_workspace(self):
        self.assertEqual(DEFAULT_WORKSPACE, Path.home() / "pga-workspace")

    def test_cli_without_workspace_reads_default_workspace_config(self):
        workspace = self.tmp / "default-workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        config_text = config_path.read_text(encoding="utf-8")
        config_text = config_text.replace('default_model = "deepseek-v4-flash"', 'default_model = "model-from-default-workspace"', 1)
        config_path.write_text(config_text, encoding="utf-8")

        old_workspace = os.environ.get("PGA_WORKSPACE")
        os.environ["PGA_WORKSPACE"] = str(workspace)
        try:
            code = main(["run", "--source", f"codex={self.sources_root / 'codex'}", "--dry-run"])
        finally:
            if old_workspace is None:
                os.environ.pop("PGA_WORKSPACE", None)
            else:
                os.environ["PGA_WORKSPACE"] = old_workspace

        self.assertEqual(code, 0)
        audit_paths = sorted((workspace / "runs").glob("*/privacy-audit.json"))
        self.assertTrue(audit_paths)
        audit = json.loads(audit_paths[-1].read_text(encoding="utf-8"))
        self.assertEqual(audit["analyzer"]["model"], "model-from-default-workspace")

    def test_run_reuses_single_daily_report_directory(self):
        workspace = self.tmp / "workspace"
        source_arg = f"codex={self.sources_root / 'codex'}"
        first_code = main(["--workspace", str(workspace), "run", "--source", source_arg, "--dry-run"])
        first_report = main(["--workspace", str(workspace), "report", "latest"])
        second_code = main(["--workspace", str(workspace), "run", "--source", source_arg, "--dry-run"])
        daily_report = workspace / "runs" / "2026-05-18" / "report.md"
        daily_reports = list((workspace / "runs").glob("*/report.md"))

        self.assertEqual(first_code, 0)
        self.assertEqual(first_report, 0)
        self.assertEqual(second_code, 0)
        self.assertEqual(daily_reports, [daily_report])
        self.assertTrue(daily_report.exists())

    def test_cli_init_wiki_path_report_latest_and_sources_scan(self):
        workspace = self.tmp / "workspace"
        init_code = main(["--workspace", str(workspace), "init"])
        init_wiki_root = workspace / "llm-wiki"
        self.assertTrue((init_wiki_root / "AGENTS.md").exists())
        self.assertTrue((init_wiki_root / "SCHEMA.md").exists())
        self.assertFalse((init_wiki_root / "raw").exists())
        self.assertFalse((init_wiki_root / "wiki").exists())
        self.assertFalse((workspace / "runs").exists())
        self.assertFalse((workspace / "cache").exists())
        self.assertFalse((workspace / "source-manifests").exists())
        wiki_code = main(["--workspace", str(workspace), "wiki", "path"])
        scan_code = main(["--workspace", str(workspace), "sources", "scan", "--source", f"codex={self.sources_root / 'codex'}"])
        run_code = main(["--workspace", str(workspace), "run", "--source", f"codex={self.sources_root / 'codex'}"])
        latest_code = main(["--workspace", str(workspace), "report", "latest"])

        self.assertEqual(init_code, 0)
        self.assertEqual(wiki_code, 0)
        self.assertEqual(scan_code, 0)
        self.assertEqual(run_code, 0)
        self.assertEqual(latest_code, 0)
        self.assertTrue((workspace / "config.toml").exists())
        self.assertTrue((workspace / "llm-wiki").exists())
        self.assertTrue((workspace / "llm-wiki" / "AGENTS.md").exists())
        self.assertTrue((workspace / "llm-wiki" / "SCHEMA.md").exists())
        self.assertTrue((workspace / "source-manifests" / "source-scan.json").exists())
        config_text = (workspace / "config.toml").read_text(encoding="utf-8")
        self.assertIn('default_model = "deepseek-v4-flash"', config_text)
        self.assertIn('api_key = ""', config_text)
        self.assertIn('[llm.providers.deepseek.models]', config_text)
        self.assertIn('flash = "deepseek-v4-flash"', config_text)

    def test_cli_can_complete_and_archive_growth_task(self):
        workspace = self.tmp / "workspace"
        source_arg = f"codex={self.sources_root / 'codex'}"
        run_code = main(["--workspace", str(workspace), "run", "--source", source_arg, "--dry-run"])
        active_path = workspace / "llm-wiki" / "data" / "growth-tasks" / "active.json"
        archive_path = workspace / "llm-wiki" / "data" / "growth-tasks" / "archive.json"
        active_tasks = json.loads(active_path.read_text(encoding="utf-8"))
        task_id = active_tasks[0]["id"]
        complete_code = main(["--workspace", str(workspace), "tasks", "complete", task_id])
        remaining_active = json.loads(active_path.read_text(encoding="utf-8"))
        archived = json.loads(archive_path.read_text(encoding="utf-8"))

        self.assertEqual(run_code, 0)
        self.assertEqual(complete_code, 0)
        self.assertFalse(any(task["id"] == task_id for task in remaining_active))
        self.assertTrue(any(task["id"] == task_id and task["status"] == "completed" for task in archived))

    def test_source_adapter_scan_is_incremental_and_raw_content_free(self):
        adapter = CodexAdapter([self.sources_root / "codex"])
        manifest_path = self.tmp / "source-scan.json"
        first = scan_sources([adapter], manifest_path)
        second = scan_sources([adapter], manifest_path)
        inventory_text = json.dumps(second, ensure_ascii=False)

        self.assertGreaterEqual(first["summary"]["discoveredFiles"], 1)
        self.assertGreaterEqual(second["summary"]["unchangedFiles"], 1)
        self.assertNotIn("请先分析", inventory_text)
        self.assertTrue(manifest_path.exists())

    def test_source_scan_ignores_known_non_conversation_json(self):
        source_root = self.tmp / "mixed-sources"
        codex_root = source_root / ".codex"
        claude_root = source_root / ".claude"
        opencode_root = source_root / "opencode"
        (codex_root / "skills" / "sample").mkdir(parents=True)
        (claude_root / "telemetry").mkdir(parents=True)
        (claude_root / "todos").mkdir(parents=True)
        (opencode_root / "bin" / "node_modules" / "pkg").mkdir(parents=True)
        (opencode_root / "storage" / "session_diff").mkdir(parents=True)
        (codex_root / "session.json").write_text((FIXTURES / "conversations" / "codex" / "session-debug.json").read_text(encoding="utf-8"), encoding="utf-8")
        (codex_root / "skills" / "sample" / "test-prompts.json").write_text('[{"prompt": "not a conversation"}]', encoding="utf-8")
        (claude_root / "telemetry" / "events.json").write_text('{"event_type": "x"}\n{"event_type": "y"}\n', encoding="utf-8")
        (claude_root / "todos" / "todo.json").write_text("[]", encoding="utf-8")
        (opencode_root / "auth.json").write_text('{"deepseek": {"key": "secret"}}', encoding="utf-8")
        (opencode_root / "bin" / "node_modules" / "pkg" / "tsdoc-metadata.json").write_text("// comment\n{}", encoding="utf-8")
        (opencode_root / "storage" / "session_diff" / "ses_1.json").write_text("[]", encoding="utf-8")
        manifest_path = self.tmp / "mixed-source-scan.json"

        inventory = scan_sources(
            [
                CodexAdapter([codex_root]),
                ClaudeCodeAdapter([claude_root]),
                OpenCodeAdapter([opencode_root]),
            ],
            manifest_path,
        )
        scanned_paths = "\n".join(str(item["path"]) for item in inventory["files"])

        self.assertEqual(inventory["summary"]["parseFailures"], 0)
        self.assertEqual(inventory["summary"]["ignoredFiles"], 0)
        self.assertNotIn("test-prompts.json", scanned_paths)
        self.assertNotIn("telemetry", scanned_paths)
        self.assertNotIn("auth.json", scanned_paths)
        self.assertNotIn("node_modules", scanned_paths)

    def test_pipeline_source_discovery_skips_known_non_conversation_json(self):
        source_root = self.tmp / "pipeline-sources"
        codex_root = source_root / ".codex"
        (codex_root / "skills" / "sample").mkdir(parents=True)
        (codex_root / "session.json").write_text((FIXTURES / "conversations" / "codex" / "session-debug.json").read_text(encoding="utf-8"), encoding="utf-8")
        (codex_root / "skills" / "sample" / "test-prompts.json").write_text('[{"prompt": "not a conversation"}]', encoding="utf-8")

        sources = discover_sources({"codex": [codex_root]})
        discovered_paths = [path.name for path in sources[0].files]

        self.assertEqual(discovered_paths, ["session.json"])

    def test_discovers_and_parses_real_cli_conversation_sources(self):
        source_root = self.tmp / "real-cli-sources"
        codex_root = source_root / ".codex"
        codex_session = codex_root / "sessions" / "2026" / "05" / "15" / "rollout-test.jsonl"
        claude_root = source_root / ".claude"
        claude_session = claude_root / "projects" / "repo" / "session-1.jsonl"
        opencode_root = source_root / "opencode"
        codex_session.parent.mkdir(parents=True)
        claude_session.parent.mkdir(parents=True)
        opencode_root.mkdir(parents=True)
        codex_session.write_text(
            "\n".join(
                [
                    json.dumps({"timestamp": "2026-05-15T01:00:00Z", "type": "session_meta", "payload": {"cwd": "C:/repo", "id": "codex_1"}}),
                    json.dumps({"timestamp": "2026-05-15T01:01:00Z", "type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "业务目标是什么？"}]}}),
                    json.dumps({"timestamp": "2026-05-15T01:02:00Z", "type": "response_item", "payload": {"type": "function_call", "name": "shell_command", "arguments": "{}"}}),
                ]
            ),
            encoding="utf-8",
        )
        claude_session.write_text(
            "\n".join(
                [
                    json.dumps({"type": "user", "timestamp": "2026-05-15T02:00:00Z", "sessionId": "claude_1", "cwd": "C:/repo", "message": {"role": "user", "content": "先分析再改代码"}}),
                    json.dumps({"type": "assistant", "timestamp": "2026-05-15T02:01:00Z", "sessionId": "claude_1", "message": {"role": "assistant", "content": [{"type": "text", "text": "我会先看上下文"}]}}),
                ]
            ),
            encoding="utf-8",
        )
        connection = sqlite3.connect(opencode_root / "opencode.db")
        connection.execute("create table session (id text, project_id text, parent_id text, slug text, directory text, title text, version text, share_url text, summary_additions integer, summary_deletions integer, summary_files integer, summary_diffs text, revert text, permission text, time_created integer, time_updated integer, time_compacting integer, time_archived integer, workspace_id text)")
        connection.execute("create table message (id text, session_id text, time_created integer, time_updated integer, data text)")
        connection.execute("create table part (id text, message_id text, session_id text, time_created integer, time_updated integer, data text)")
        connection.execute("insert into session values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ("op_1", "proj", None, "slug", "C:/repo", "Title", "1", None, 0, 0, 0, None, None, None, 1770000000000, 1770000001000, None, None, None))
        connection.execute("insert into message values (?,?,?,?,?)", ("msg_1", "op_1", 1770000000000, 1770000000000, json.dumps({"role": "user"})))
        connection.execute("insert into part values (?,?,?,?,?,?)", ("prt_1", "msg_1", "op_1", 1770000000000, 1770000000000, json.dumps({"type": "text", "text": "验收标准是什么？"})))
        connection.commit()
        connection.close()

        sources = discover_sources({"codex": [codex_root], "claude_code": [claude_root], "opencode": [opencode_root]})
        sessions, failures = parse_sources(sources)
        codex_files = [path.name for source in sources if source.name == "codex" for path in source.files]
        opencode_files = [path.name for source in sources if source.name == "opencode" for path in source.files]

        self.assertEqual(failures, [])
        self.assertIn("rollout-test.jsonl", codex_files)
        self.assertIn("opencode.db", opencode_files)
        self.assertEqual({session.source for session in sessions}, {"codex", "claude_code", "opencode"})
        self.assertTrue(any(message["content"] == "业务目标是什么？" for session in sessions for message in session.messages))
        self.assertTrue(any(tool["name"] == "shell_command" for session in sessions for tool in session.tool_calls))

    def test_claude_jsonl_parser_skips_malformed_lines(self):
        claude_root = self.tmp / "claude-malformed" / ".claude"
        transcript = claude_root / "transcripts" / "ses_bad.jsonl"
        transcript.parent.mkdir(parents=True)
        transcript.write_text(
            "\n".join(
                [
                    json.dumps({"type": "user", "timestamp": "2026-05-15T02:00:00Z", "content": "第一条正常消息"}),
                    '{"type":"tool_use","timestamp":"2026-05-15T02:01:00Z","tool_input":{"query":"unterminated',
                    json.dumps({"type": "assistant", "timestamp": "2026-05-15T02:02:00Z", "content": "第二条正常消息"}),
                ]
            ),
            encoding="utf-8",
        )

        sources = discover_sources({"claude_code": [claude_root]})
        sessions, failures = parse_sources(sources)

        self.assertEqual(failures, [])
        self.assertEqual(len(sessions), 1)
        self.assertEqual([message["content"] for message in sessions[0].messages], ["第一条正常消息", "第二条正常消息"])

    def test_analyzer_payload_validation_reconciliation_and_local_provider(self):
        request = AnalyzerRequest(
            provider="local",
            model="",
            analysis_mode="local",
            evidence=[{"id": "ev_1", "summary": "用户要求验证输出", "sensitivity": "safe"}],
            signals=[{"name": "requires_verification", "evidenceIds": ["ev_1"], "confidence": 0.82}],
            wiki_memory=[],
            approved=False,
            dry_run=False,
        )
        local_response = LocalAnalyzerProvider().analyze(request)
        payload, preview = build_analyzer_payload(request)
        valid = validate_llm_analysis(
            {
                "roleInference": {"currentRole": "AI Agent 工程师", "confidence": 0.7, "evidenceIds": ["ev_1"], "cautions": []},
                "strengths": [],
                "risks": [],
                "candidateSignals": [{"name": "requires_verification", "category": "ai_system_management", "evidenceIds": ["ev_1"], "confidence": 0.7}],
                "growthTasks": [],
                "wikiUpdates": [],
            },
            {"ev_1"},
        )
        reconciled = reconcile_signals(request.signals, valid["candidateSignals"])

        self.assertEqual(local_response.provider, "local")
        self.assertFalse(local_response.network_called)
        self.assertFalse(preview.contains_original_messages)
        self.assertNotIn("rawMessages", payload)
        self.assertEqual(reconciled[0]["status"], "agreed")
        with self.assertRaises(ValueError):
            validate_llm_analysis({"candidateSignals": [{"name": "x", "evidenceIds": ["missing"]}]}, {"ev_1"})

    def test_non_local_provider_requires_approval_or_dry_run(self):
        config = AnalyzerConfig(provider="openai-compatible", model="gpt-test", base_url="https://example.test", api_key_env="PGA_TEST_KEY")
        request = AnalyzerRequest(
            provider=config.provider,
            model=config.model,
            analysis_mode="assist",
            evidence=[{"id": "ev_1", "summary": "safe", "sensitivity": "safe"}],
            signals=[],
            wiki_memory=[],
            approved=False,
            dry_run=True,
        )
        payload, preview = build_analyzer_payload(request)

        self.assertEqual(preview.target, "openai-compatible")
        self.assertEqual(payload["analysisMode"], "assist")
        self.assertNotIn(config.api_key_env, os.environ)

    def test_dry_run_pipeline_records_analyzer_audit_without_network(self):
        output = self.tmp / "dry-run-out"
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"]},
            output_root=output,
            constraints={
                "weeklyTimeBudgetHours": 3,
                "currentFocus": "balanced",
                "provider": "openai-compatible",
                "model": "gpt-test",
                "analysisMode": "assist",
                "dryRun": True,
                "approveOutbound": False,
            },
        )
        run_dir = Path(result["run_dir"])
        audit = json.loads((run_dir / "privacy-audit.json").read_text(encoding="utf-8"))
        report = (run_dir / "report.md").read_text(encoding="utf-8")

        self.assertEqual(audit["analyzer"]["provider"], "openai-compatible")
        self.assertEqual(audit["analyzer"]["validationStatus"], "dry_run")
        self.assertFalse(audit["analyzer"]["networkCalled"])
        self.assertIn("Provider: openai-compatible", report)

    def test_pipeline_records_missing_deepseek_credential_without_secret_leak(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"]},
            output_root=workspace,
            constraints={
                "weeklyTimeBudgetHours": 3,
                "currentFocus": "balanced",
                "provider": "deepseek",
                "analysisMode": "llm_first",
                "dryRun": False,
                "approveOutbound": True,
                "llmConfig": load_config(config_path).llm,
            },
        )
        run_dir = Path(result["run_dir"])
        audit_text = (run_dir / "privacy-audit.json").read_text(encoding="utf-8")
        audit = json.loads(audit_text)

        self.assertEqual(audit["analyzer"]["credentialSource"], "missing")
        self.assertEqual(audit["analyzer"]["skipReason"], "missing_credentials")
        self.assertEqual(audit["analyzer"]["validationStatus"], "skipped_missing_credentials")
        self.assertIn("api_key", audit["analyzer"]["message"])
        self.assertNotIn("PGA_DEEPSEEK_API_KEY=", audit_text)

    def test_pipeline_calls_remote_provider_when_approved_and_credential_exists(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(
            "\n".join(
                [
                    f'workspace = "{workspace.as_posix()}"',
                    "",
                    "[llm]",
                    'default_provider = "deepseek"',
                    'default_model = "deepseek-v4-flash"',
                    'default_analysis_mode = "llm_first"',
                    "",
                    "[llm.providers.deepseek]",
                    'provider = "deepseek"',
                    'base_url = "https://api.deepseek.com"',
                    'api_key = "file-secret-value"',
                    'api_key_env = "PGA_DEEPSEEK_API_KEY"',
                    'default_model = "deepseek-v4-flash"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"]},
            output_root=workspace,
            constraints={
                "weeklyTimeBudgetHours": 3,
                "currentFocus": "balanced",
                "provider": "deepseek",
                "analysisMode": "llm_first",
                "dryRun": False,
                "approveOutbound": True,
                "llmConfig": load_config(config_path).llm,
                "providerTransport": lambda _url, _headers, _body, _timeout: {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "roleInference": {
                                            "currentRole": "AI Agent 工程师",
                                            "confidence": 0.7,
                                            "evidenceIds": ["ev_1"],
                                        }
                                    },
                                    ensure_ascii=False,
                                )
                            }
                        }
                    ]
                },
            },
        )
        run_dir = Path(result["run_dir"])
        audit_text = (run_dir / "privacy-audit.json").read_text(encoding="utf-8")
        audit = json.loads(audit_text)

        self.assertEqual(audit["analyzer"]["credentialSource"], "file")
        self.assertEqual(audit["analyzer"]["validationStatus"], "validation_error")
        self.assertTrue(audit["analyzer"]["networkCalled"])
        self.assertNotEqual(audit["analyzer"]["responseDigest"], "")
        self.assertNotIn("file-secret-value", audit_text)


if __name__ == "__main__":
    unittest.main()
