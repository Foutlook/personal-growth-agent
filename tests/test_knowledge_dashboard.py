import json
import shutil
import tempfile
import unittest
from pathlib import Path

from personal_growth_agent.cli import main
from personal_growth_agent.dashboard import build_dashboard_data, build_static_dashboard
from personal_growth_agent.growth import generate_growth_cycle
from personal_growth_agent.knowledge import ingest_article_text, ingest_file, ingest_note
from personal_growth_agent.models import GrowthMemoryContext
from personal_growth_agent.pipeline import run_growth_cycle
from personal_growth_agent.wiki import init_llm_wiki, lint_wiki, load_growth_memory_context


class KnowledgeDashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.workspace = self.tmp / "workspace"
        self.wiki_root = self.workspace / "llm-wiki"
        init_llm_wiki(self.wiki_root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_wiki_initialization_includes_knowledge_directories(self):
        self.assertTrue((self.wiki_root / "AGENTS.md").exists())
        self.assertTrue((self.wiki_root / "SCHEMA.md").exists())
        self.assertFalse((self.wiki_root / "raw").exists())
        self.assertFalse((self.wiki_root / "wiki").exists())

    def test_note_file_and_article_ingestion_create_raw_manifest_and_wiki_pages(self):
        source_file = self.tmp / "agent-notes.md"
        source_file.write_text("# Agent Notes\n\nUse evaluator loops.\n", encoding="utf-8")
        note = ingest_note(self.wiki_root, "Agent loop", "Track agent state and evaluator output.", tags=["agent"])
        file_result = ingest_file(self.wiki_root, source_file, tags=["file"])
        article = ingest_article_text(
            self.wiki_root,
            "LLM Wiki",
            "LLM Wiki compiles raw sources into reviewed knowledge.\nQuestion: how to improve review quality?",
            origin_url="https://example.com/wiki",
            publisher="Example",
            tags=["wiki"],
        )
        manifest = json.loads((self.wiki_root / "data" / "source-manifest.json").read_text(encoding="utf-8"))

        self.assertTrue(Path(note.raw_source.path).exists())
        self.assertTrue(Path(file_result.raw_source.path).exists())
        self.assertEqual(source_file.read_text(encoding="utf-8"), "# Agent Notes\n\nUse evaluator loops.\n")
        self.assertTrue(Path(article.proposal.diff_path).exists())
        self.assertIn("wiki\\knowledge\\concepts", article.proposal.diff_path)
        self.assertEqual(article.proposal.status, "accepted")
        self.assertFalse((self.wiki_root / "diff" / "proposed-updates").exists())
        self.assertTrue(any(item["sourceType"] == "user_note" for item in manifest))
        self.assertTrue(any(item["sourceType"] == "local_document" for item in manifest))
        self.assertTrue(any(item["originalUrl"] == "https://example.com/wiki" for item in manifest))

    def test_local_only_knowledge_is_omitted_from_dashboard_safe_data(self):
        ingest_note(self.wiki_root, "Sensitive", "private key should stay local", tags=["security"])
        dashboard = build_static_dashboard(self.workspace, self.wiki_root)
        data = json.loads((Path(dashboard.data_path)).read_text(encoding="utf-8"))

        self.assertEqual(data["privacy"]["omittedLocalOnlyCount"], 1)
        self.assertNotIn("private key", json.dumps(data, ensure_ascii=False))

    def test_dashboard_build_writes_static_files_and_indexes_growth_wiki_data(self):
        runs = self.workspace / "runs" / "20260513"
        runs.mkdir(parents=True)
        (runs / "report.md").write_text("# Report\n\nSummary", encoding="utf-8")
        ingest_article_text(self.wiki_root, "Agent Systems", "Agent systems need evaluation.", origin_url="https://example.com/agent")
        dashboard = build_static_dashboard(self.workspace, self.wiki_root)
        data = json.loads((Path(dashboard.data_path)).read_text(encoding="utf-8"))

        self.assertTrue(Path(dashboard.entry_path).exists())
        self.assertTrue(Path(dashboard.assets_path).exists())
        self.assertGreaterEqual(len(data["sources"]), 1)
        self.assertNotIn("proposals", data)
        self.assertTrue(data["reports"])

    def test_dashboard_reports_dedupe_repeated_task_package_reports(self):
        first_run = self.workspace / "runs" / "2026-05-15T084738Z0000"
        second_run = self.workspace / "runs" / "2026-05-15T085805Z0000"
        third_run = self.workspace / "runs" / "2026-05-15T090222Z0000"
        first_run.mkdir(parents=True)
        second_run.mkdir(parents=True)
        third_run.mkdir(parents=True)
        report_text = "# 本轮成长任务包\n\n## 本周只做这 3 件事\n\n1. 任务 A\n"
        first_report = first_run / "report.md"
        second_report = second_run / "report.md"
        third_report = third_run / "report.md"
        first_report.write_text(report_text, encoding="utf-8")
        second_report.write_text(report_text, encoding="utf-8")
        third_report.write_text("# 本轮成长任务包\n\n## 本周只做这 3 件事\n\n1. 任务 B\n", encoding="utf-8")

        data, _ = build_dashboard_data(self.workspace, self.wiki_root)

        self.assertEqual(len(data["reports"]), 1)
        self.assertEqual(data["reports"][0]["runCount"], 3)
        self.assertEqual(data["reports"][0]["title"], "本轮成长任务包")
        self.assertNotIn("任务 A", data["reports"][0]["summary"])
        self.assertNotIn("任务 B", data["reports"][0]["summary"])
        self.assertEqual(data["reports"][0]["path"], str(third_report))

    def test_dashboard_hides_internal_tabs_from_static_ui(self):
        dashboard = build_static_dashboard(self.workspace, self.wiki_root)
        dashboard_js = (Path(dashboard.assets_path) / "dashboard.js").read_text(encoding="utf-8")

        self.assertIn("任务", dashboard_js)
        self.assertNotIn("'sources'", dashboard_js)
        self.assertNotIn("'privacy'", dashboard_js)
        self.assertNotIn("'maturity'", dashboard_js)

    def test_dashboard_indexes_latest_executable_growth_tasks(self):
        source_root = Path(__file__).parent / "fixtures" / "conversations"
        run_growth_cycle(
            {"codex": [source_root / "codex"], "claude_code": [source_root / "claude"]},
            self.workspace,
            {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        dashboard = build_static_dashboard(self.workspace, self.wiki_root)
        data = json.loads(Path(dashboard.data_path).read_text(encoding="utf-8"))

        self.assertTrue(data["growth"]["tasks"])
        self.assertIn("startHere", data["growth"]["tasks"][0])
        self.assertIn("outputPath", data["growth"]["tasks"][0])
        self.assertIn("glossary", data["growth"]["tasks"][0])
        dashboard_js = (Path(dashboard.assets_path) / "dashboard.js").read_text(encoding="utf-8")
        self.assertIn("从哪里开始", dashboard_js)
        self.assertIn("结果写到哪里", dashboard_js)

    def test_dashboard_hides_archived_growth_tasks(self):
        source_root = Path(__file__).parent / "fixtures" / "conversations"
        run_growth_cycle(
            {"codex": [source_root / "codex"], "claude_code": [source_root / "claude"]},
            self.workspace,
            {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        active_path = self.wiki_root / "data" / "growth-tasks" / "active.json"
        first_active = json.loads(active_path.read_text(encoding="utf-8"))
        first_active[0]["status"] = "completed"
        active_path.write_text(json.dumps(first_active, ensure_ascii=False, indent=2), encoding="utf-8")
        run_growth_cycle(
            {"codex": [source_root / "codex"], "claude_code": [source_root / "claude"]},
            self.workspace,
            {"weeklyTimeBudgetHours": 3, "currentFocus": "balanced"},
        )
        dashboard = build_static_dashboard(self.workspace, self.wiki_root)
        data = json.loads(Path(dashboard.data_path).read_text(encoding="utf-8"))
        dashboard_task_ids = [task["id"] for task in data["growth"]["tasks"]]

        self.assertNotIn(first_active[0]["id"], dashboard_task_ids)

    def test_cli_ingest_dashboard_and_source_scan_are_separate(self):
        note_code = main(["--workspace", str(self.workspace), "ingest", "note", "--title", "CLI Note", "--content", "CLI content"])
        dashboard_code = main(["--workspace", str(self.workspace), "dashboard", "build"])
        scan_code = main(["--workspace", str(self.workspace), "sources", "scan"])
        manifest = json.loads((self.wiki_root / "data" / "source-manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(note_code, 0)
        self.assertEqual(dashboard_code, 0)
        self.assertEqual(scan_code, 0)
        self.assertTrue((self.workspace / "dashboard" / "index.html").exists())
        self.assertTrue(any(item["sourceType"] == "user_note" for item in manifest))

    def test_growth_context_uses_knowledge_gaps_without_maturity_amplification(self):
        result = ingest_article_text(
            self.wiki_root,
            "Business Agent",
            "Question: how should AI agent work map to business metrics?",
            origin_url="https://example.com/business-agent",
            tags=["business_depth"],
        )
        knowledge_gap = self.wiki_root / "wiki" / "knowledge" / "gaps" / "business-agent.md"
        knowledge_gap.write_text(
            "\n".join(
                [
                    "---",
                    "type: knowledge_gap",
                    "status: ready",
                    "source_raw_ids:",
                    f"  - {result.raw_source.id}",
                    "tracks:",
                    "  - business_depth",
                    "confidence: 0.5",
                    "review_state: pending",
                    "---",
                    "# Business metric gap",
                ]
            ),
            encoding="utf-8",
        )
        context = load_growth_memory_context(self.wiki_root)
        cycle = generate_growth_cycle([], {"weeklyTimeBudgetHours": 3}, context)

        self.assertTrue(context.knowledge_gaps)
        self.assertTrue(any(task.task_type == "knowledge_gap" for task in cycle.tasks))
        self.assertLessEqual(max(item.confidence for item in cycle.maturity_estimates), 0.48)

    def test_wiki_lint_reports_knowledge_provenance_issues(self):
        page = self.wiki_root / "wiki" / "knowledge" / "concepts" / "unsupported.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("---\ntype: knowledge_page\nstatus: ready\n---\n# Unsupported\n\nA claim without sources.\n", encoding="utf-8")
        issues = lint_wiki(self.wiki_root)

        self.assertTrue(any(issue.type == "knowledge_missing_provenance" for issue in issues))


if __name__ == "__main__":
    unittest.main()
