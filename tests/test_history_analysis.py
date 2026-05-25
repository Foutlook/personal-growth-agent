import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GKH = ROOT / "growth-knowledge-hub" / "scripts" / "gkh.py"
FIXTURES = ROOT / "tests" / "fixtures" / "history"


class HistoryAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

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

    def test_analyze_single_sources_from_explicit_directories(self):
        cases = [
            ("codex", FIXTURES / "codex", "请帮我设计 analyze-history 命令。"),
            ("claude", FIXTURES / "claude", "Review my growth knowledge hub architecture."),
            ("opencode", FIXTURES / "opencode", "Add recall support for historical CLI context."),
        ]

        for source, source_dir, expected_prompt in cases:
            with self.subTest(source=source):
                _result, payload = self.run_gkh(
                    "analyze-history",
                    "--source",
                    source,
                    "--source-dir",
                    str(source_dir),
                    "--output",
                    "json",
                )

                self.assertEqual(payload["status"], "ok")
                self.assertEqual(payload["sources"][0]["source"], source)
                self.assertEqual(payload["sources"][0]["analyzed"], 1)
                self.assertIn(expected_prompt, payload["sessions"][0]["first_user_prompt"])

    def test_analyze_all_sources_with_source_map_writes_searchable_wiki(self):
        _result, payload = self.run_gkh(
            "analyze-history",
            "--source",
            "all",
            "--source-map",
            f"codex={FIXTURES / 'codex'}",
            "--source-map",
            f"claude={FIXTURES / 'claude'}",
            "--source-map",
            f"opencode={FIXTURES / 'opencode'}",
            "--output",
            "wiki",
        )

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["analyzed"], 3)
        history_dir = self.tmp / "llm-wiki" / "wiki" / "history"
        self.assertTrue((history_dir / "codex-history.md").exists())
        self.assertTrue((history_dir / "claude-history.md").exists())
        self.assertTrue((history_dir / "opencode-history.md").exists())

        _search_result, search_payload = self.run_gkh("search", "--query", "analyze-history")
        self.assertTrue(search_payload["items"])

    def test_rejects_ambiguous_source_dir_and_unknown_source_map(self):
        result, payload = self.run_gkh(
            "analyze-history",
            "--source",
            "all",
            "--source-dir",
            str(FIXTURES),
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "error")
        self.assertIn("--source-map", payload["error"])

        result, payload = self.run_gkh(
            "analyze-history",
            "--source",
            "all",
            "--source-map",
            f"cursor={FIXTURES}",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "error")
        self.assertIn("unknown source", payload["error"])

    def test_filters_limits_dry_run_and_stdout(self):
        _result, payload = self.run_gkh(
            "analyze-history",
            "--source",
            "all",
            "--source-map",
            f"codex={FIXTURES / 'codex'}",
            "--source-map",
            f"claude={FIXTURES / 'claude'}",
            "--source-map",
            f"opencode={FIXTURES / 'opencode'}",
            "--since",
            "2026-05-21",
            "--until",
            "2026-05-22",
            "--limit",
            "1",
            "--dry-run",
            "--output",
            "stdout",
        )

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["dryRun"])
        self.assertEqual(payload["analyzed"], 1)
        self.assertFalse((self.tmp / "llm-wiki" / "wiki" / "history").exists())

    def test_redacts_historical_secrets_and_skips_private_keys(self):
        source_dir = self.tmp / "codex-history"
        source_dir.mkdir()
        secret_session = source_dir / "secret.jsonl"
        secret_session.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "timestamp": "2026-05-23T10:00:00Z",
                            "role": "user",
                            "content": "token=abc123 should be hidden",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "timestamp": "2026-05-23T10:01:00Z",
                            "role": "assistant",
                            "content": "BEGIN PRIVATE KEY must not be saved",
                        },
                        ensure_ascii=False,
                    ),
                ]
            ),
            encoding="utf-8",
        )

        _result, payload = self.run_gkh(
            "analyze-history",
            "--source",
            "codex",
            "--source-dir",
            str(source_dir),
            "--output",
            "json",
        )

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["analyzed"], 0)
        self.assertTrue(any("private key" in warning.lower() for warning in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
