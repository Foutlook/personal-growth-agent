# Scan Iterations

Use this workflow when the user asks to scan project repositories, generate iteration records, review release branch history, or analyze team development patterns.

The host CLI calls the bundled script to scan git repositories. No remote API is needed — all data comes from local git history.

## When to Use

- "扫描项目迭代记录"
- "看看各项目的迭代情况"
- "生成迭代报告"
- "查看 release 分支历史"
- "分析团队提交情况"

## Input

```bash
python scripts/gkh.py scan-iterations --dir /path/to/projects --branch-prefix release --output wiki
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--repo` | No | - | Single project path |
| `--dir` | No | - | Directory with multiple projects |
| `--branch-prefix` | No | `release` | Branch name prefix |
| `--output` | No | `stdout` | `stdout` or `wiki` |

Use `--repo` for one project or `--dir` for multiple projects. They are mutually exclusive.

## Output

### stdout (default)

Returns JSON with iteration records per project:

```json
{
  "status": "ok",
  "projects": [
    {
      "project": "my-app",
      "repo": "/path/to/my-app",
      "iterations": [
        {
          "branch": "release/20250621",
          "date_label": "06.21",
          "main_topics": "login, auth; [src, api]",
          "author_count": 3,
          "additions": 1200,
          "deletions": 350,
          "changed_files": 28,
          "avg_files_per_commit": 9.3,
          "stability": "★★★★",
          "conventionality": "★★★",
          "authors": [
            {"name": "Alice", "commits": 8, "additions": 800, "deletions": 200}
          ]
        }
      ]
    }
  ],
  "warnings": []
}
```

### wiki

Writes `wiki/projects/<project>/iterations.md` with Markdown tables.

## Interpretation

### Main Topics

Combines commit message keywords with hot directories:
- `login, auth; [src, api]` = keywords "login", "auth" from commits + most changed dirs "src", "api"

### Stability Rating

Based on `fixup!` / `revert:` commit ratio:

| Ratio | Rating |
|-------|--------|
| <5% | ★★★★★ |
| <10% | ★★★★ |
| <20% | ★★★ |
| <30% | ★★ |
| ≥30% | ★ |

### Conventionality Rating

Based on conventional commit (`type: message`) adherence:

| Ratio | Rating |
|-------|--------|
| ≥80% | ★★★★★ |
| ≥60% | ★★★★ |
| ≥40% | ★★★ |
| ≥20% | ★★ |
| <20% | ★ |

## Edge Cases

- Branches without YYYYMMDD date are skipped with a warning.
- First branch is compared against main/master; subsequent branches against the previous.
- Non-git directories are skipped.
- Repos without main/master are reported as errors.

## Host CLI Guidance

- If the user wants deeper code quality analysis (N+1 queries, abstraction quality), the host CLI should read the changed files and use its own judgment — the script only provides git-level statistics.
- After a successful scan, suggest the user search for the project name to recall the iteration records later.
- If `--output wiki` is used, report the page paths written.
