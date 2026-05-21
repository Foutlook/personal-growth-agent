import json
import shutil
import tempfile
import unittest
from pathlib import Path

from personal_growth_agent.assets import generate_action_assets
from personal_growth_agent.audit import create_outbound_preview, redact_text
from personal_growth_agent.data import discover_sources, generate_source_inventory, parse_sources
from personal_growth_agent.evidence import aggregate_signals, extract_evidence
from personal_growth_agent.growth import generate_growth_cycle
from personal_growth_agent.models import GrowthMemoryMetadata
from personal_growth_agent.pipeline import run_growth_cycle
from personal_growth_agent.repository import analyze_repository
from personal_growth_agent.wiki import (
    create_growth_memory_proposals,
    create_growth_run_snapshot,
    init_llm_wiki,
    ingest_raw_source,
    lint_wiki,
    load_growth_memory_context,
    read_growth_memory_state,
    read_wiki_write_log,
    validate_growth_memory_metadata,
)


FIXTURES = Path(__file__).parent / "fixtures"


class PersonalGrowthAgentMvpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sources_root = self.tmp / "sources"
        shutil.copytree(FIXTURES / "conversations", self.sources_root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_conversation_sources_are_discovered_and_parsed_with_failures(self):
        sources = discover_sources({"codex": [self.sources_root / "codex"], "missing": [self.tmp / "missing"], "opencode": [self.sources_root / "opencode"]})
        inventory = generate_source_inventory(sources)
        sessions, failures = parse_sources(sources)

        self.assertEqual(inventory["sources"][0]["name"], "codex")
        self.assertNotIn("messagePreview", json.dumps(inventory), "inventory must not expose raw message previews")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].source, "codex")
        self.assertTrue(sessions[0].source_ref.endswith("session-debug.json"))
        self.assertEqual(len(failures), 1)

    def test_privacy_redaction_and_outbound_preview(self):
        redacted, findings = redact_text("token=sk-secret email test@example.com https://internal.local/db")
        preview = create_outbound_preview("llm", "diagnosis", ["ev_1"], findings, redacted)

        self.assertNotIn("sk-secret", redacted)
        self.assertNotIn("test@example.com", redacted)
        self.assertFalse(preview.contains_original_messages)
        self.assertGreaterEqual(preview.redacted_items_count, 2)

    def test_evidence_signals_growth_tasks_and_action_assets_are_generated(self):
        sessions, _ = parse_sources(discover_sources({"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"]}))
        evidence = extract_evidence(sessions)
        signals = aggregate_signals(evidence)
        cycle = generate_growth_cycle(signals, {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"})
        assets = generate_action_assets(cycle.tasks, cycle.diagnoses, evidence)

        signal_names = {signal.name for signal in signals}
        self.assertIn("requires_verification", signal_names)
        self.assertIn("asks_business_goal", signal_names)
        self.assertEqual(len(cycle.tasks), 3)
        self.assertTrue(all(task.done_definition for task in cycle.tasks))
        self.assertTrue(all(task.review_questions for task in cycle.tasks))
        self.assertTrue(all(task.start_here for task in cycle.tasks))
        self.assertTrue(all(task.output_path for task in cycle.tasks))
        self.assertTrue(all(task.output_example for task in cycle.tasks))
        self.assertTrue(all(task.glossary for task in cycle.tasks))
        self.assertGreaterEqual(len(assets), 3)
        self.assertTrue(all(asset.source_task_ids or asset.source_diagnosis_ids for asset in assets))

    def test_llm_wiki_uses_raw_sources_and_lint_without_default_diff(self):
        wiki_root = self.tmp / "llm-wiki"
        init_llm_wiki(wiki_root)
        raw = ingest_raw_source(wiki_root, "growth_artifact", "pga", "safe summary", "local/growth-artifact.md")
        raw_path = Path(raw.path)
        before = raw_path.read_text(encoding="utf-8")
        raw_again = ingest_raw_source(wiki_root, "growth_artifact", "pga", "changed summary", "local/growth-artifact.md")
        issues = lint_wiki(wiki_root)

        self.assertEqual(before, raw_path.read_text(encoding="utf-8"))
        self.assertNotEqual(raw.id, raw_again.id)
        self.assertFalse((wiki_root / "diff" / "proposed-updates").exists())
        self.assertIsInstance(issues, list)

    def test_repository_analysis_requires_confirmation_and_detects_agent_files(self):
        repo = self.tmp / "repo"
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "docs").mkdir()
        (repo / "AGENTS.md").write_text("rules", encoding="utf-8")
        (repo / "README.md").write_text("readme", encoding="utf-8")
        (repo / "tests" / "test_app.py").write_text("def test_x(): pass", encoding="utf-8")

        with self.assertRaises(PermissionError):
            analyze_repository(repo, confirmed=False)

        pack = analyze_repository(repo, confirmed=True)
        self.assertTrue(pack.signals["has_tests"])
        self.assertTrue(pack.signals["has_docs"])
        self.assertTrue(pack.signals["has_agent_rules"])

    def test_full_pipeline_writes_runs_report_and_llm_wiki(self):
        output = self.tmp / "out"
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )

        report = Path(result["run_dir"]) / "report.md"
        report_json = Path(result["run_dir"]) / "report.json"
        self.assertTrue(report.exists())
        self.assertTrue(report.read_text(encoding="utf-8").startswith("# 本轮成长任务包"))
        self.assertTrue(report_json.exists())
        self.assertTrue((output / "llm-wiki" / "AGENTS.md").exists())
        self.assertTrue((Path(result["run_dir"]) / "wiki-updates" / "accepted-updates.json").exists())
        conversation_raw_files = list((output / "llm-wiki" / "raw" / "conversations").glob("*.md"))
        proposal_files = list((output / "llm-wiki" / "diff" / "proposed-updates").glob("*.md"))
        growth_pages = list((output / "llm-wiki" / "wiki" / "growth").rglob("*.md"))
        growth_text = "\n".join(path.read_text(encoding="utf-8") for path in growth_pages)

        self.assertEqual(conversation_raw_files, [])
        self.assertEqual(proposal_files, [])
        self.assertIn("source_run_id:", growth_text)
        self.assertIn("source_evidence_ids:", growth_text)
        self.assertNotIn("source_raw_ids:", growth_text)
        report_text = report.read_text(encoding="utf-8")

        self.assertIn("从哪里开始", report_text)
        self.assertIn("结果写到哪里", report_text)
        self.assertIn("结果长什么样", report_text)
        self.assertIn("术语解释", report_text)

    def test_pipeline_does_not_write_task_templates_into_capability_directories(self):
        output = self.tmp / "out"
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        wiki_root = Path(result["wiki_root"])
        growth_task_pages = list((wiki_root / "wiki" / "growth" / "tasks").glob("*.md"))
        capability_pages = []
        for relative_path in ("agent-engineering", "ai-system-management", "business-depth"):
            capability_pages.extend((wiki_root / "wiki" / relative_path).rglob("*.md"))
        wiki_pages = json.loads((Path(result["run_dir"]) / "wiki-updates" / "wiki-pages.json").read_text(encoding="utf-8"))

        self.assertTrue(growth_task_pages)
        self.assertEqual(capability_pages, [])
        self.assertEqual(wiki_pages, [])

    def test_growth_task_page_names_are_readable(self):
        output = self.tmp / "out"
        run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        task_pages = sorted((output / "llm-wiki" / "wiki" / "growth" / "tasks").glob("*.md"))
        names = [path.stem for path in task_pages]

        self.assertTrue(task_pages)
        self.assertTrue(all(not name.startswith("task_") for name in names))
        self.assertTrue(any("agent-flow-analysis" in name for name in names))
        self.assertTrue(any("business-goal-card" in name for name in names))
        self.assertTrue(any("ai-output-rubric" in name for name in names))

    def test_legacy_hashed_growth_task_pages_are_migrated_to_readable_names(self):
        output = self.tmp / "out"
        wiki_root = output / "llm-wiki"
        legacy_task = wiki_root / "wiki" / "growth" / "tasks" / "task_abc123.md"
        legacy_task.parent.mkdir(parents=True)
        legacy_task.write_text(
            "\n".join(
                [
                    "---",
                    "type: growth_task",
                    "lifecycle_status: active",
                    "source_run_id: run_old",
                    "source_evidence_ids:",
                    "  - ev_old",
                    "evidence_status: Inferred",
                    "confidence: 0.65",
                    "human_confirmed: false",
                    "valid_until: 2099-01-01T00:00:00+00:00",
                    "review_state: pending",
                    "tracks:",
                    "  - ai_system_management",
                    "related: []",
                    "---",
                    "",
                    "# 为该会话定义 AI 输出验收 Rubric",
                    "",
                    "## Task",
                    "为该会话定义 AI 输出验收 Rubric",
                ]
            ),
            encoding="utf-8",
        )

        run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )

        self.assertFalse(legacy_task.exists())
        self.assertTrue((wiki_root / "wiki" / "growth" / "tasks" / "ai-output-rubric.md").exists())

    def test_legacy_hash_task_with_existing_readable_target_is_removed(self):
        output = self.tmp / "out"
        wiki_root = output / "llm-wiki"
        legacy_task = wiki_root / "wiki" / "growth" / "tasks" / "task_abc123.md"
        readable_task = wiki_root / "wiki" / "growth" / "tasks" / "ai-output-rubric.md"
        readable_task.parent.mkdir(parents=True)
        legacy_task.write_text(
            "\n".join(
                [
                    "---",
                    "type: growth_task",
                    "lifecycle_status: active",
                    "source_run_id: run_old",
                    "source_evidence_ids:",
                    "  - ev_old",
                    "evidence_status: Inferred",
                    "confidence: 0.65",
                    "human_confirmed: false",
                    "valid_until: 2099-01-01T00:00:00+00:00",
                    "review_state: pending",
                    "tracks:",
                    "  - ai_system_management",
                    "related: []",
                    "---",
                    "",
                    "# 为该会话定义 AI 输出验收 Rubric",
                ]
            ),
            encoding="utf-8",
        )
        readable_task.write_text("already migrated", encoding="utf-8")

        run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )

        self.assertFalse(legacy_task.exists())
        self.assertEqual(readable_task.read_text(encoding="utf-8"), "already migrated")

    def test_growth_tasks_are_persistent_and_completed_tasks_are_archived(self):
        output = self.tmp / "out"
        first = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        active_path = output / "llm-wiki" / "data" / "growth-tasks" / "active.json"
        archive_path = output / "llm-wiki" / "data" / "growth-tasks" / "archive.json"
        first_active = json.loads(active_path.read_text(encoding="utf-8"))
        first_ids = [task["id"] for task in first_active]
        first_active[0]["status"] = "completed"
        first_active[0]["completion_note"] = "手动标注完成"
        active_path.write_text(json.dumps(first_active, ensure_ascii=False, indent=2), encoding="utf-8")

        second = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        second_active = json.loads(active_path.read_text(encoding="utf-8"))
        archived = json.loads(archive_path.read_text(encoding="utf-8"))
        second_ids = [task["id"] for task in second_active]

        self.assertEqual(first["wiki_root"], second["wiki_root"])
        self.assertNotIn(first_ids[0], second_ids)
        self.assertTrue(any(task["id"] == first_ids[0] and task["status"] == "completed" for task in archived))
        self.assertEqual(len(second_ids), len(set(second_ids)))

    def test_growth_memory_models_validate_required_traceability(self):
        metadata = GrowthMemoryMetadata(
            type="diagnosis",
            lifecycle_status="active",
            source_run_id="run_1",
            source_evidence_ids=["ev_1"],
            source_raw_ids=[],
            evidence_status="Inferred",
            confidence=0.6,
            human_confirmed=False,
            valid_until="2099-01-01T00:00:00+00:00",
            review_state="pending",
            tracks=["business_depth"],
            related=[],
        )

        validate_growth_memory_metadata(metadata)

        metadata.source_evidence_ids = []
        with self.assertRaises(ValueError):
            validate_growth_memory_metadata(metadata)

    def test_growth_run_snapshot_is_immutable_and_manifested(self):
        wiki_root = self.tmp / "llm-wiki"
        init_llm_wiki(wiki_root)
        first = create_growth_run_snapshot(
            wiki_root,
            "run_1",
            {"report": "first", "diagnoses": ["diag_1"], "tasks": ["task_1"]},
            ["ev_1"],
            [],
        )
        snapshot_path = Path(first.path)
        before = snapshot_path.read_text(encoding="utf-8")
        second = create_growth_run_snapshot(
            wiki_root,
            "run_1",
            {"report": "changed", "diagnoses": ["diag_2"], "tasks": ["task_2"]},
            ["ev_2"],
            [],
        )
        manifest = json.loads((wiki_root / "data" / "source-manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(first.id, second.id)
        self.assertEqual(before, snapshot_path.read_text(encoding="utf-8"))
        self.assertTrue(any(item["sourceType"] == "growth_run" and item["rawSourceId"] == first.id for item in manifest))

    def test_growth_memory_writes_machine_state_and_direct_summaries(self):
        wiki_root = self.tmp / "llm-wiki"
        sessions, _ = parse_sources(discover_sources({"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"]}))
        evidence = extract_evidence(sessions)
        signals = aggregate_signals(evidence)
        cycle = generate_growth_cycle(signals, {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"})
        snapshot = create_growth_run_snapshot(wiki_root, cycle.id, {"report": "summary"}, [item.id for item in evidence[:3]], [])
        writes = create_growth_memory_proposals(wiki_root, cycle, snapshot, [item.id for item in evidence[:3]])
        growth_state = read_growth_memory_state(wiki_root)
        write_log = read_wiki_write_log(wiki_root)

        update_text = Path(writes[0].path).read_text(encoding="utf-8")
        unsupported_page = wiki_root / "wiki" / "growth" / "diagnoses" / "unsupported.md"
        unsupported_page.parent.mkdir(parents=True, exist_ok=True)
        unsupported_page.write_text("---\ntype: diagnosis\nlifecycle_status: active\n---\n# Unsupported\n", encoding="utf-8")
        issues = lint_wiki(wiki_root)

        self.assertGreaterEqual(len(writes), 2 + len(cycle.tasks))
        self.assertEqual(len(growth_state["diagnoses"]), len(cycle.diagnoses))
        self.assertEqual(len(growth_state["maturitySnapshots"]), len(cycle.maturity_estimates))
        self.assertFalse((wiki_root / "wiki" / "growth" / "maturity-snapshots").exists())
        self.assertTrue((wiki_root / "wiki" / "growth" / "overview.md").exists())
        self.assertTrue(any(entry["targetPath"] == writes[0].target_path for entry in write_log))
        self.assertFalse((wiki_root / "diff" / "proposed-updates").exists())
        self.assertIn("source_run_id:", update_text)
        self.assertIn("evidence_status:", update_text)
        self.assertTrue(any(issue.type == "growth_missing_source" for issue in issues))

    def test_growth_memory_context_influences_next_cycle_without_confidence_amplification(self):
        wiki_root = self.tmp / "llm-wiki"
        sessions, _ = parse_sources(discover_sources({"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"]}))
        evidence = extract_evidence(sessions)
        signals = aggregate_signals(evidence)
        prior_cycle = generate_growth_cycle(signals, {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"})
        snapshot = create_growth_run_snapshot(wiki_root, prior_cycle.id, {"report": "summary"}, [item.id for item in evidence[:3]], [])
        create_growth_memory_proposals(wiki_root, prior_cycle, snapshot, [item.id for item in evidence[:3]])
        active_task = wiki_root / "wiki" / "growth" / "tasks" / "active-task.md"
        active_task.parent.mkdir(parents=True, exist_ok=True)
        active_task.write_text(
            "\n".join(
                [
                    "---",
                    "type: growth_task",
                    "lifecycle_status: active",
                    "source_run_id: run_prior",
                    "source_evidence_ids:",
                    "  - ev_1",
                    "evidence_status: Inferred",
                    "confidence: 0.4",
                    "human_confirmed: false",
                    "valid_until: 2099-01-01T00:00:00+00:00",
                    "review_state: pending",
                    "tracks:",
                    "  - agent_engineering",
                    "related: []",
                    "---",
                    "# 历史任务",
                    "",
                    "## 完成定义",
                    "- 补充复盘",
                ]
            ),
            encoding="utf-8",
        )

        context = load_growth_memory_context(wiki_root)
        next_cycle = generate_growth_cycle(signals, {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"}, context)

        self.assertTrue(context.active_tasks)
        self.assertTrue(any(task.task_type == "carried_forward" for task in next_cycle.tasks))
        self.assertLessEqual(max(item.confidence for item in next_cycle.maturity_estimates), 0.75)

    def test_full_pipeline_writes_growth_memory_outputs(self):
        output = self.tmp / "growth-memory-out"
        result = run_growth_cycle(
            source_paths={"codex": [self.sources_root / "codex"], "claude_code": [self.sources_root / "claude"], "opencode": [self.sources_root / "opencode"]},
            output_root=output,
            constraints={"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        run_dir = Path(result["run_dir"])
        audit = json.loads((run_dir / "privacy-audit.json").read_text(encoding="utf-8"))

        self.assertTrue((output / "llm-wiki" / "raw" / "growth-runs").exists())
        self.assertTrue((output / "llm-wiki" / "data" / "growth-memory" / "diagnoses.json").exists())
        self.assertTrue((output / "llm-wiki" / "wiki" / "growth" / "overview.md").exists())
        self.assertTrue((output / "llm-wiki" / "wiki" / "growth" / "tasks").exists())
        self.assertTrue((run_dir / "wiki-updates" / "growth-memory-updates.json").exists())
        self.assertFalse((output / "llm-wiki" / "wiki" / "growth" / "maturity-snapshots").exists())
        self.assertIn("growthRunSnapshots", audit)
        self.assertIn("wikiWrites", audit)
        self.assertIn("## 成长记忆更新", (run_dir / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
