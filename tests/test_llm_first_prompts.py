import json
import shutil
import tempfile
import unittest
from pathlib import Path

from personal_growth_agent.analyzer import (
    AnalyzerRequest,
    build_analyzer_payload,
    build_provider_request,
    call_remote_provider,
    resolve_provider_route,
    resolve_provider_credential,
    validate_scenario_output,
)
from personal_growth_agent.config import load_config, write_default_config
from personal_growth_agent.pipeline import run_growth_cycle
from personal_growth_agent.prompts import PromptRegistry


FIXTURES = Path(__file__).parent / "fixtures"


class LlmFirstPromptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sources_root = self.tmp / "sources"
        shutil.copytree(FIXTURES / "conversations", self.sources_root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_default_config_loads_llm_provider_and_prompt_settings(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        config = load_config(config_path)

        self.assertEqual(config.llm.default_provider, "deepseek")
        self.assertEqual(config.llm.default_model, "deepseek-v4-flash")
        self.assertEqual(config.llm.default_analysis_mode, "llm_first")
        self.assertIn("deepseek", config.llm.providers)
        self.assertIn("openai", config.llm.providers)
        self.assertEqual(config.llm.providers["deepseek"].default_model, "deepseek-v4-flash")
        self.assertEqual(config.llm.providers["deepseek"].models["flash"], "deepseek-v4-flash")
        self.assertEqual(config.llm.providers["deepseek"].models["pro"], "deepseek-v4-pro")
        self.assertEqual(config.llm.providers["openai"].default_model, "gpt-5.4")
        self.assertEqual(config.llm.prompt_dir, workspace / "prompts")

    def test_deepseek_config_supports_file_api_key_and_env_fallback(self):
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
                    'default_model = "flash"',
                    "",
                    "[llm.providers.deepseek]",
                    'provider = "deepseek"',
                    'base_url = "https://api.deepseek.com"',
                    'api_key = "file-secret-value"',
                    'api_key_env = "PGA_TEST_DEEPSEEK_KEY"',
                    'default_model = "flash"',
                    "",
                    "[llm.providers.deepseek.models]",
                    'flash = "deepseek-v4-flash"',
                    'pro = "deepseek-v4-pro"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        config = load_config(config_path)
        route = resolve_provider_route(config.llm, scenario="role_profile")
        credential = resolve_provider_credential(route, env={"PGA_TEST_DEEPSEEK_KEY": "env-secret-value"})
        provider_request = build_provider_request(route, {"safe": True}, credential)
        request_text = json.dumps(provider_request, ensure_ascii=False)

        self.assertEqual(route.model, "deepseek-v4-flash")
        self.assertEqual(route.models["pro"], "deepseek-v4-pro")
        self.assertEqual(credential.source, "file")
        self.assertTrue(credential.available)
        self.assertEqual(provider_request["credentialSource"], "file")
        self.assertNotIn("file-secret-value", request_text)
        self.assertNotIn("env-secret-value", request_text)

    def test_provider_credential_falls_back_to_env_and_reports_missing(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        config = load_config(config_path)
        route = resolve_provider_route(config.llm, scenario="role_profile", model_override="pro")
        env_credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "env-secret-value"})
        missing_credential = resolve_provider_credential(route, env={})

        self.assertEqual(route.model, "deepseek-v4-pro")
        self.assertEqual(env_credential.source, "env")
        self.assertTrue(env_credential.available)
        self.assertEqual(missing_credential.source, "missing")
        self.assertFalse(missing_credential.available)
        self.assertIn("api_key", missing_credential.message)
        self.assertIn("PGA_DEEPSEEK_API_KEY", missing_credential.message)

    def test_remote_provider_call_uses_credential_without_leaking_secret(self):
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
                    'default_model = "flash"',
                    "",
                    "[llm.providers.deepseek]",
                    'provider = "deepseek"',
                    'base_url = "https://api.deepseek.com"',
                    'api_key = "file-secret-value"',
                    'api_key_env = "PGA_TEST_DEEPSEEK_KEY"',
                    'default_model = "flash"',
                    "",
                    "[llm.providers.deepseek.models]",
                    'flash = "deepseek-v4-flash"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        captured = {}

        def fake_transport(url, headers, body, timeout):
            captured["url"] = url
            captured["headers"] = headers
            captured["body"] = body
            captured["timeout"] = timeout
            content = json.dumps({"roleInference": {"currentRole": "AI Agent 工程师", "confidence": 0.7, "evidenceIds": ["ev_1"]}}, ensure_ascii=False)
            return {"choices": [{"message": {"content": content}}]}

        config = load_config(config_path)
        route = resolve_provider_route(config.llm, scenario="role_profile")
        credential = resolve_provider_credential(route, env={})
        result = call_remote_provider(route, {"evidence": [{"id": "ev_1"}]}, credential, fake_transport)
        request_text = json.dumps(captured, ensure_ascii=False)

        self.assertTrue(result.network_called)
        self.assertEqual(result.output["roleInference"]["currentRole"], "AI Agent 工程师")
        self.assertEqual(captured["url"], "https://api.deepseek.com/chat/completions")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer file-secret-value")
        self.assertNotIn("file-secret-value", json.dumps(result.audit_metadata(), ensure_ascii=False))
        self.assertIn("deepseek-v4-flash", request_text)

    def test_provider_request_includes_prompt_and_schema_contract(self):
        route = resolve_provider_route(load_config(None).llm, scenario="role_profile")
        credential = resolve_provider_credential(route, env={"PGA_DEEPSEEK_API_KEY": "env-secret-value"})
        provider_request = build_provider_request(
            route,
            {
                "scenario": "role_profile",
                "outputSchema": "role_profile_v1",
                "prompt": {"content": "你是个人成长分析 Agent。"},
                "evidence": [{"id": "ev_1", "summary": "用户要求先分析"}],
            },
            credential,
        )
        system_content = provider_request["body"]["messages"][0]["content"]

        self.assertIn("个人成长分析", system_content)
        self.assertIn("roleInference", system_content)
        self.assertIn("evidenceIds", system_content)

    def test_prompt_registry_uses_workspace_override_and_tracks_digest(self):
        workspace = self.tmp / "workspace"
        prompt_dir = workspace / "prompts"
        prompt_dir.mkdir(parents=True)
        prompt_path = prompt_dir / "role_profile.zh.md"
        prompt_path.write_text("---\nid: role_profile\nversion: custom-v1\n---\n自定义角色分析提示", encoding="utf-8")
        registry = PromptRegistry(workspace, prompt_dir)
        prompt = registry.load("role_profile")

        self.assertEqual(prompt.id, "role_profile")
        self.assertEqual(prompt.version, "custom-v1")
        self.assertIn("自定义角色分析提示", prompt.content)
        self.assertEqual(len(prompt.digest), 64)

    def test_provider_route_prefers_cli_over_scenario_and_config(self):
        workspace = self.tmp / "workspace"
        config_path = workspace / "config.toml"
        write_default_config(config_path, workspace)
        config = load_config(config_path)
        route = resolve_provider_route(config.llm, scenario="role_profile", provider_override="openai", model_override="gpt-5.4")

        self.assertEqual(route.provider, "openai")
        self.assertEqual(route.model, "gpt-5.4")
        self.assertEqual(route.api_key_env, "PGA_OPENAI_API_KEY")

    def test_analyzer_payload_includes_scenario_prompt_and_excludes_local_only(self):
        request = AnalyzerRequest(
            provider="deepseek",
            model="deepseek-chat",
            analysis_mode="llm_first",
            evidence=[
                {"id": "ev_1", "summary": "用户要求验证输出", "sensitivity": "safe"},
                {"id": "ev_2", "summary": "private key material", "sensitivity": "local_only"},
            ],
            signals=[{"name": "requires_verification", "evidenceIds": ["ev_1"], "confidence": 0.8}],
            wiki_memory=[],
            approved=False,
            dry_run=True,
            scenario="role_profile",
            prompt={"id": "role_profile", "version": "v1", "digest": "abc", "content": "分析角色"},
            output_schema="role_profile_v1",
        )
        payload, preview = build_analyzer_payload(request)
        payload_text = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["scenario"], "role_profile")
        self.assertEqual(payload["prompt"]["id"], "role_profile")
        self.assertIn("分析角色", payload["prompt"]["content"])
        self.assertEqual(preview.target, "deepseek")
        self.assertNotIn("private key material", payload_text)

    def test_analyzer_payload_limits_remote_evidence_items(self):
        request = AnalyzerRequest(
            provider="deepseek",
            model="deepseek-v4-flash",
            analysis_mode="llm_first",
            evidence=[{"id": f"ev_{index}", "summary": f"safe summary {index}", "sensitivity": "safe"} for index in range(120)],
            signals=[],
            wiki_memory=[],
            approved=True,
            dry_run=False,
        )
        payload, preview = build_analyzer_payload(request, max_evidence_items=80)

        self.assertEqual(len(payload["evidence"]), 80)
        self.assertEqual(payload["omittedEvidenceCount"], 40)
        self.assertEqual(preview.included_evidence_count, 80)

    def test_scenario_validation_requires_evidence_references(self):
        valid = validate_scenario_output(
            "growth_planning",
            {
                "growthTasks": [
                    {
                        "title": "补充业务目标卡",
                        "track": "business_depth",
                        "steps": ["写目标"],
                        "doneDefinition": ["完成卡片"],
                        "reviewQuestions": ["指标是什么？"],
                        "evidenceIds": ["ev_1"],
                    }
                ]
            },
            {"ev_1"},
        )

        self.assertEqual(valid["growthTasks"][0]["title"], "补充业务目标卡")
        with self.assertRaises(ValueError):
            validate_scenario_output("growth_planning", {"growthTasks": [{"title": "bad"}]}, {"ev_1"})

    def test_llm_first_dry_run_pipeline_records_prompt_and_falls_back_locally(self):
        output = self.tmp / "llm-first-out"
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"]},
            output_root=output,
            constraints={
                "weeklyTimeBudgetHours": 3,
                "currentFocus": "balanced",
                "provider": "deepseek",
                "model": "deepseek-chat",
                "analysisMode": "llm_first",
                "dryRun": True,
                "approveOutbound": False,
            },
        )
        run_dir = Path(result["run_dir"])
        audit = json.loads((run_dir / "privacy-audit.json").read_text(encoding="utf-8"))

        self.assertEqual(audit["analyzer"]["provider"], "deepseek")
        self.assertEqual(audit["analyzer"]["analysisMode"], "llm_first")
        self.assertEqual(audit["analyzer"]["validationStatus"], "dry_run")
        self.assertEqual(audit["analyzer"]["fallbackMode"], "local_rules")
        self.assertTrue(audit["analyzer"]["prompts"])


if __name__ == "__main__":
    unittest.main()
