import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GKH = ROOT / "growth-knowledge-hub" / "scripts" / "gkh.py"


class GrowthKnowledgeHubSkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_gkh(self, *args, check=True):
        result = subprocess.run(
            [sys.executable, str(GKH), "--home", str(self.tmp), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if check and result.returncode != 0:
            self.fail(result.stderr or result.stdout)
        stream = result.stdout if result.stdout.strip() else result.stderr
        payload = json.loads(stream)
        return result, payload

    def write_json(self, name, payload):
        path = self.tmp / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_skill_script_captures_ingests_reviews_recalls_and_dashboards_without_package_install(self):
        init_result, init_payload = self.run_gkh("init")
        self.assertEqual(init_result.returncode, 0)
        self.assertTrue(Path(init_payload["wiki"]).exists())

        capture_input = self.write_json(
            "capture.json",
            {
                "title": "重新定位为成长知识 Skill",
                "captured_from": "current_conversation",
                "summary": ["项目从 agent 应用转向 skill 化记忆层。"],
                "decisions": ["宿主 CLI 负责对话，skill 负责本地沉淀和召回。"],
                "insights": ["长期知识闭环才是核心价值。"],
                "open_questions": ["如何同时服务多个 CLI？"],
                "next_actions": ["实现 gkh.py。"],
                "growth_tracks": ["agent_engineering"],
                "tags": ["skill"],
            },
        )
        _capture_result, capture_payload = self.run_gkh("capture", "--input", str(capture_input))

        material_input = self.write_json(
            "material.json",
            {
                "title": "Harness Notes",
                "source_type": "external_material",
                "source_locator": "ima:media:opaque",
                "summary_points": ["Harness connects model and tools.", "Results need provenance."],
                "key_concepts": ["tool boundary"],
                "why_it_matters": "It turns agent experience into reusable knowledge.",
                "application_ideas": ["Use compact recall context."],
                "open_questions": ["What belongs in project memory?"],
                "tags": ["agent_engineering"],
            },
        )
        _material_result, material_payload = self.run_gkh("ingest", "--input", str(material_input))

        review_input = self.write_json(
            "review.json",
            {
                "title": "本周成长复盘",
                "period": "2026-W21",
                "observations": ["Scope drift was noticed."],
                "progress": ["The project was reframed."],
                "bottlenecks": ["Runtime scope control."],
                "knowledge_gaps": ["Skill packaging for host CLIs."],
                "next_tasks": ["Ship recall command."],
                "related_pages": [],
                "tags": ["review"],
            },
        )
        _review_result, review_payload = self.run_gkh("review", "--input", str(review_input))
        _search_result, search_payload = self.run_gkh("search", "--query", "skill")
        _context_result, context_payload = self.run_gkh("context", "--query", "skill", "--limit", "2")
        _dashboard_result, dashboard_payload = self.run_gkh("dashboard")

        self.assertEqual(capture_payload["status"], "ok")
        self.assertEqual(material_payload["status"], "ok")
        self.assertEqual(review_payload["status"], "ok")
        self.assertTrue(search_payload["items"])
        self.assertLessEqual(len(context_payload["items"]), 2)
        self.assertTrue(Path(dashboard_payload["entryPath"]).exists())
        self.assertTrue((self.tmp / "llm-wiki" / "data" / "source-manifest.json").exists())
        self.assertTrue((self.tmp / "llm-wiki" / "data" / "wiki-write-log.json").exists())
        self.assertTrue((self.tmp / "llm-wiki" / "data" / "index.json").exists())

    def test_skill_script_rejects_invalid_input_without_partial_write(self):
        invalid_input = self.write_json("invalid.json", {"summary": ["missing title"]})

        result, payload = self.run_gkh("capture", "--input", str(invalid_input), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "error")
        self.assertFalse((self.tmp / "llm-wiki" / "data" / "source-manifest.json").exists())

    def test_skill_script_redacts_secrets_and_hides_local_only_reads(self):
        capture_input = self.write_json(
            "secret.json",
            {
                "title": "Secret Handling",
                "captured_from": "current_conversation",
                "summary": ["api_key=secret-value should not be stored raw."],
                "decisions": ["Redact secrets before persistence."],
                "insights": ["Recall must be safe."],
                "open_questions": [],
                "next_actions": ["Verify redaction."],
                "growth_tracks": [],
                "tags": ["privacy"],
            },
        )
        _capture_result, capture_payload = self.run_gkh("capture", "--input", str(capture_input))
        written_path = Path(capture_payload["writes"][0]["path"])
        page_text = written_path.read_text(encoding="utf-8")

        self.assertIn("[SECRET_REDACTED]", page_text)
        self.assertNotIn("secret-value", page_text)


if __name__ == "__main__":
    unittest.main()
