import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GKH = ROOT / "growth-knowledge-hub" / "scripts" / "gkh.py"


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {args} failed: {result.stderr}")
    return result.stdout.strip()


def make_repo(path: Path, branches: list[dict]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init")
    git(path, "config", "user.email", "test@test.com")
    git(path, "config", "user.name", "Tester")
    (path / "init.txt").write_text("init", encoding="utf-8")
    git(path, "add", ".")
    git(path, "commit", "-m", "chore: initial commit")
    git(path, "checkout", "-b", "main")
    for branch_info in branches:
        git(path, "checkout", "-b", branch_info["name"])
        for commit in branch_info.get("commits", []):
            for fname, content in commit.get("files", {"f.txt": "data"}).items():
                fpath = path / fname
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")
            git(path, "add", ".")
            git(path, "commit", "-m", commit["msg"])
        git(path, "checkout", "main")


class ScanIterationsUnitTests(unittest.TestCase):
    """Unit tests run via subprocess to avoid module import issues."""

    def run_gkh_json(self, *args):
        result = subprocess.run(
            [sys.executable, str(GKH), *args],
            capture_output=True, text=True, encoding="utf-8",
        )
        return result, json.loads(result.stdout) if result.stdout.strip() else {}

    def test_extract_date_valid(self):
        # Tested indirectly through scan-iterations with valid/invalid branch names
        repo = Path(tempfile.mkdtemp())
        try:
            make_repo(repo, [
                {"name": "release/20250601", "commits": [{"msg": "feat: a", "files": {"a.txt": "x"}}]},
                {"name": "release/20250621", "commits": [{"msg": "feat: b", "files": {"b.txt": "y"}}]},
                {"name": "release/v1.0", "commits": [{"msg": "feat: c", "files": {"c.txt": "z"}}]},
            ])
            result, payload = self.run_gkh_json("scan-iterations", "--repo", str(repo))
            self.assertEqual(payload["status"], "ok")
            iters = payload["projects"][0]["iterations"]
            self.assertEqual(len(iters), 2)
            self.assertEqual(iters[0]["branch"], "release/20250601")
            self.assertEqual(iters[1]["branch"], "release/20250621")
            self.assertTrue(any("no YYYYMMDD date" in w for w in payload["warnings"]))
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_rate_stability(self):
        # Tested via integration: repos with fixup! commits should get lower stability
        repo = Path(tempfile.mkdtemp())
        try:
            make_repo(repo, [{
                "name": "release/20250601",
                "commits": [
                    {"msg": "feat: good", "files": {"a.txt": "1"}},
                    {"msg": "fixup! feat: good", "files": {"a.txt": "2"}},
                    {"msg": "fixup! feat: good", "files": {"a.txt": "3"}},
                    {"msg": "fixup! feat: good", "files": {"a.txt": "4"}},
                    {"msg": "fixup! feat: good", "files": {"a.txt": "5"}},
                    {"msg": "fixup! feat: good", "files": {"a.txt": "6"}},
                ],
            }])
            result, payload = self.run_gkh_json("scan-iterations", "--repo", str(repo))
            iter0 = payload["projects"][0]["iterations"][0]
            # 5 fixup out of 6 = 83% -> ★
            self.assertEqual(iter0["stability"], "★")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_rate_conventionality(self):
        repo = Path(tempfile.mkdtemp())
        try:
            make_repo(repo, [{
                "name": "release/20250601",
                "commits": [
                    {"msg": "feat: good message", "files": {"a.txt": "1"}},
                    {"msg": "random gibberish", "files": {"a.txt": "2"}},
                ],
            }])
            result, payload = self.run_gkh_json("scan-iterations", "--repo", str(repo))
            iter0 = payload["projects"][0]["iterations"][0]
            # 1/2 = 50% -> ★★★
            self.assertEqual(iter0["conventionality"], "★★★")
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_format_iterations_markdown(self):
        # Tested via wiki output
        repo = Path(tempfile.mkdtemp())
        home = Path(tempfile.mkdtemp())
        try:
            make_repo(repo, [{
                "name": "release/20250601",
                "commits": [
                    {"msg": "feat: add login", "files": {"src/login.py": "def login(): pass"}},
                ],
            }])
            result, payload = self.run_gkh_json(
                "--home", str(home),
                "scan-iterations", "--repo", str(repo), "--output", "wiki",
            )
            iterations_md = home / "llm-wiki" / "wiki" / "projects" / repo.name / "iterations.md"
            self.assertTrue(iterations_md.exists())
            content = iterations_md.read_text(encoding="utf-8")
            self.assertIn(f"# {repo.name} 迭代记录", content)
            self.assertIn("release/20250601", content)
            self.assertIn("| 迭代分支 |", content)
        finally:
            shutil.rmtree(repo, ignore_errors=True)
            shutil.rmtree(home, ignore_errors=True)


class ScanIterationsIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_gkh(self, *args, check=True):
        result = subprocess.run(
            [sys.executable, str(GKH), *args],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if check and result.returncode != 0:
            self.fail(result.stderr or result.stdout)
        stream = result.stdout if result.stdout.strip() else result.stderr
        payload = json.loads(stream)
        return result, payload

    def test_scan_single_repo(self):
        repo = self.tmp / "project-a"
        make_repo(repo, [
            {
                "name": "release/20250601",
                "commits": [
                    {"msg": "feat: add login module", "files": {"src/login.py": "def login(): pass"}},
                    {"msg": "fix: fix null check", "files": {"src/login.py": "def login(): return True"}},
                ],
            },
            {
                "name": "release/20250621",
                "commits": [
                    {"msg": "feat: add payment", "files": {"src/payment.py": "def pay(): pass"}},
                    {"msg": "chore: update deps", "files": {"requirements.txt": "flask==2.0"}},
                ],
            },
        ])
        _result, payload = self.run_gkh("scan-iterations", "--repo", str(repo))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["projects"]), 1)
        project = payload["projects"][0]
        self.assertEqual(project["project"], "project-a")
        self.assertEqual(len(project["iterations"]), 2)
        first = project["iterations"][0]
        self.assertEqual(first["branch"], "release/20250601")
        self.assertGreater(first["additions"], 0)
        second = project["iterations"][1]
        self.assertEqual(second["branch"], "release/20250621")

    def test_scan_dir_multiple_repos(self):
        for name in ["proj-a", "proj-b"]:
            repo = self.tmp / name
            make_repo(repo, [{
                "name": "release/20250601",
                "commits": [{"msg": "feat: init", "files": {"f.txt": "hello"}}],
            }])
        _result, payload = self.run_gkh("scan-iterations", "--dir", str(self.tmp))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["projects"]), 2)

    def test_scan_with_wiki_output(self):
        repo = self.tmp / "proj-wiki"
        home = self.tmp / "gkh-home"
        make_repo(repo, [{
            "name": "release/20250601",
            "commits": [{"msg": "feat: init", "files": {"f.txt": "hello"}}],
        }])
        _result, payload = self.run_gkh(
            "--home", str(home),
            "scan-iterations", "--repo", str(repo), "--output", "wiki",
        )
        self.assertEqual(payload["status"], "ok")
        iterations_md = home / "llm-wiki" / "wiki" / "projects" / "proj-wiki" / "iterations.md"
        self.assertTrue(iterations_md.exists())
        content = iterations_md.read_text(encoding="utf-8")
        self.assertIn("# proj-wiki 迭代记录", content)

    def test_scan_no_git_repo_skipped(self):
        # Need at least one valid repo alongside the non-repo dir
        valid_repo = self.tmp / "valid-repo"
        make_repo(valid_repo, [{
            "name": "release/20250601",
            "commits": [{"msg": "feat: init", "files": {"f.txt": "hello"}}],
        }])
        not_repo = self.tmp / "not-a-repo"
        not_repo.mkdir()
        _result, payload = self.run_gkh("scan-iterations", "--dir", str(self.tmp))
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(any("not a git repository" in w for w in payload["warnings"]))

    def test_scan_no_release_branches(self):
        repo = self.tmp / "empty-repo"
        repo.mkdir()
        git(repo, "init")
        git(repo, "config", "user.email", "test@test.com")
        git(repo, "config", "user.name", "Tester")
        (repo / "f.txt").write_text("x", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-m", "init")
        result = subprocess.run(
            [sys.executable, str(GKH), "scan-iterations", "--repo", str(repo)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["projects"][0]["iterations"]), 0)
        self.assertTrue(any("no release/* branches" in w for w in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
