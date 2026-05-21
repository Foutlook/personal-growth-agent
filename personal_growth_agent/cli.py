from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .config import DEFAULT_WORKSPACE, AppConfig, ensure_workspace, load_config, resolve_paths, write_default_config
from .compiler import compile_raw_to_wiki
from .dashboard import build_static_dashboard, open_static_dashboard
from .knowledge import ingest_article_text, ingest_file, ingest_note, ingest_url
from .pipeline import run_growth_cycle
from .prompts import PromptRegistry
from .sources import adapters_to_candidates, default_adapters, scan_sources
from .utils import utc_now_iso


def main(argv: list[str] | None = None, interactive_runner=None) -> int:
    parser = argparse.ArgumentParser(description="Run a local Personal Growth Agent cycle")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--wiki", type=Path, default=None)
    parser.add_argument("--config", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--source", action="append", default=[], help="source mapping in name=path form")
    run_parser.add_argument("--weekly-hours", type=int, default=3)
    run_parser.add_argument("--provider", default=None)
    run_parser.add_argument("--model", default=None)
    run_parser.add_argument("--analysis-mode", default=None)
    run_parser.add_argument("--prompt-dir", type=Path, default=None)
    run_parser.add_argument("--dry-run", action="store_true")
    run_parser.add_argument("--approve-outbound", action="store_true")

    sources_parser = subparsers.add_parser("sources")
    source_subparsers = sources_parser.add_subparsers(dest="sources_command")
    scan_parser = source_subparsers.add_parser("scan")
    scan_parser.add_argument("--source", action="append", default=[], help="source mapping in name=path form")

    report_parser = subparsers.add_parser("report")
    report_subparsers = report_parser.add_subparsers(dest="report_command")
    report_subparsers.add_parser("latest")

    wiki_parser = subparsers.add_parser("wiki")
    wiki_subparsers = wiki_parser.add_subparsers(dest="wiki_command")
    wiki_subparsers.add_parser("path")
    wiki_compile_parser = wiki_subparsers.add_parser("compile")
    wiki_compile_parser.add_argument("--raw", required=True, type=Path)
    wiki_compile_parser.add_argument("--prompt", required=True, type=Path)

    prompts_parser = subparsers.add_parser("prompts")
    prompts_subparsers = prompts_parser.add_subparsers(dest="prompts_command")
    prompts_subparsers.add_parser("path")
    prompt_show_parser = prompts_subparsers.add_parser("show")
    prompt_show_parser.add_argument("scenario")

    ingest_parser = subparsers.add_parser("ingest")
    ingest_subparsers = ingest_parser.add_subparsers(dest="ingest_command")
    note_parser = ingest_subparsers.add_parser("note")
    note_parser.add_argument("--title", required=True)
    note_parser.add_argument("--content", default=None)
    note_parser.add_argument("--tag", action="append", default=[])
    file_parser = ingest_subparsers.add_parser("file")
    file_parser.add_argument("path", type=Path)
    file_parser.add_argument("--tag", action="append", default=[])
    web_parser = ingest_subparsers.add_parser("web")
    web_parser.add_argument("--title", required=True)
    web_parser.add_argument("--content", default=None)
    web_parser.add_argument("--url", default="")
    web_parser.add_argument("--publisher", default="")
    web_parser.add_argument("--author", default="")
    web_parser.add_argument("--fetch", action="store_true")
    web_parser.add_argument("--tag", action="append", default=[])

    dashboard_parser = subparsers.add_parser("dashboard")
    dashboard_subparsers = dashboard_parser.add_subparsers(dest="dashboard_command")
    dashboard_subparsers.add_parser("build")
    dashboard_subparsers.add_parser("open")

    tasks_parser = subparsers.add_parser("tasks")
    tasks_subparsers = tasks_parser.add_subparsers(dest="tasks_command")
    task_complete_parser = tasks_subparsers.add_parser("complete")
    task_complete_parser.add_argument("task_id")

    # Backward-compatible flat command used by the MVP tests and early users.
    parser.add_argument("--source", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--output", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--weekly-hours", type=int, default=3, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.command is None and (args.source or args.output):
        output_root = Path(args.output or ".")
        source_paths = _parse_source_args(args.source)
        result = run_growth_cycle(source_paths, output_root, {"weeklyTimeBudgetHours": args.weekly_hours, "currentFocus": "balanced"})
        print(result["run_dir"])
        return 0

    env_workspace = os.environ.get("PGA_WORKSPACE")
    env_config = os.environ.get("PGA_CONFIG")
    default_config_workspace_path = Path(env_workspace or DEFAULT_WORKSPACE)
    default_config_workspace = default_config_workspace_path.expanduser()
    config_workspace = args.workspace or default_config_workspace
    if env_config:
        default_config_path_value = Path(env_config)
    else:
        default_config_path_value = config_workspace / "config.toml"
    default_config_path = default_config_path_value.expanduser()
    config_path = args.config or default_config_path
    config = load_config(config_path)
    paths = resolve_paths(config=config, workspace_arg=args.workspace, wiki_arg=args.wiki, config_arg=args.config)
    ensure_workspace(paths)

    if args.command is None:
        from .interactive import InteractiveContext, run_interactive

        context = InteractiveContext(paths=paths, config=config, session_id="")
        runner = interactive_runner or run_interactive
        return runner(context)

    if args.command == "init":
        write_default_config(paths.config, paths.workspace)
        from .wiki import init_llm_wiki

        init_llm_wiki(paths.wiki)
        PromptRegistry(paths.workspace, config.llm.prompt_dir).ensure_workspace_prompts()
        print(paths.workspace)
        return 0
    if args.command == "wiki" and args.wiki_command == "path":
        print(paths.wiki)
        return 0
    if args.command == "wiki" and args.wiki_command == "compile":
        from .prompts import PromptTemplate
        from .utils import sha256_text

        prompt_content = args.prompt.read_text(encoding="utf-8")
        prompt = PromptTemplate(
            id=_prompt_metadata(prompt_content).get("id") or args.prompt.stem,
            version=_prompt_metadata(prompt_content).get("version") or "v1",
            scenario="wiki_compile",
            path=str(args.prompt),
            content=prompt_content,
            digest=sha256_text(prompt_content),
        )
        results = compile_raw_to_wiki(paths.wiki, args.raw, prompt)
        print(json.dumps([result.target_path for result in results], ensure_ascii=False))
        return 0
    if args.command == "prompts" and args.prompts_command == "path":
        print(config.llm.prompt_dir)
        return 0
    if args.command == "prompts" and args.prompts_command == "show":
        prompt = PromptRegistry(paths.workspace, config.llm.prompt_dir).load(args.scenario)
        print(prompt.path)
        return 0
    if args.command == "ingest":
        return _handle_ingest(args, paths.wiki)
    if args.command == "dashboard" and args.dashboard_command == "build":
        result = build_static_dashboard(paths.workspace, paths.wiki)
        print(result.entry_path)
        return 0
    if args.command == "dashboard" and args.dashboard_command == "open":
        result = build_static_dashboard(paths.workspace, paths.wiki)
        opened = open_static_dashboard(Path(result.entry_path))
        if not opened:
            print(result.entry_path)
        return 0
    if args.command == "tasks" and args.tasks_command == "complete":
        completed = _complete_task(paths.wiki, args.task_id)
        print(completed or "")
        return 0 if completed else 1
    if args.command == "report" and args.report_command == "latest":
        latest = _latest_report(paths.runs)
        print(latest or "")
        return 0
    if args.command == "sources" and args.sources_command == "scan":
        source_paths = _parse_source_args(args.source)
        adapters = default_adapters(source_paths)
        inventory = scan_sources(adapters, paths.source_manifests / "source-scan.json")
        print(json.dumps(inventory["summary"], ensure_ascii=False))
        return 0
    if args.command == "run":
        source_paths = _parse_source_args(args.source)
        if not source_paths:
            adapters = default_adapters(_paths_from_config(config))
            source_candidates = adapters_to_candidates(adapters)
            source_paths = {candidate.name: [candidate.path] for candidate in source_candidates}
        result = run_growth_cycle(
            source_paths,
            paths.workspace,
            {
                "weeklyTimeBudgetHours": args.weekly_hours,
                "currentFocus": "balanced",
                "provider": args.provider or config.llm.default_provider or config.provider.provider,
                "model": args.model or config.llm.default_model or config.provider.model,
                "analysisMode": args.analysis_mode or config.llm.default_analysis_mode or config.provider.analysis_mode,
                "promptDir": args.prompt_dir or config.llm.prompt_dir,
                "llmConfig": config.llm,
                "dryRun": args.dry_run,
                "approveOutbound": args.approve_outbound or config.provider.approve_outbound or config.llm.approve_outbound,
            },
        )
        print(result["run_dir"])
        print(f"wiki: {result['wiki_root']}")
        return 0
    parser.print_help()
    return 0


def _parse_source_args(items: list[str]) -> dict[str, list[Path]]:
    source_paths: dict[str, list[Path]] = {}
    for item in items:
        name, path = item.split("=", 1)
        source_paths.setdefault(name, []).append(Path(path))
    return source_paths


def _paths_from_config(config: AppConfig) -> dict[str, list[Path]]:
    return {name: source.paths for name, source in config.sources.items() if source.enabled}


def _handle_ingest(args: argparse.Namespace, wiki_root: Path) -> int:
    if args.ingest_command == "note":
        content = args.content
        if content is None:
            content = sys.stdin.read()
        result = ingest_note(wiki_root, args.title, content, tags=args.tag)
        print(_ingest_summary(result))
        return 0
    if args.ingest_command == "file":
        result = ingest_file(wiki_root, args.path, tags=args.tag)
        print(_ingest_summary(result))
        return 0
    if args.ingest_command == "web":
        if args.fetch:
            result = ingest_url(wiki_root, args.url, title=args.title, fetch=True, tags=args.tag)
        else:
            content = args.content
            if content is None:
                content = sys.stdin.read()
            result = ingest_article_text(wiki_root, args.title, content, origin_url=args.url, publisher=args.publisher, author=args.author, tags=args.tag)
        print(_ingest_summary(result))
        return 0
    return 1


def _latest_report(runs_path: Path) -> Path | None:
    today_report = runs_path / utc_now_iso()[:10] / "report.md"
    if today_report.exists():
        return today_report
    reports = sorted(runs_path.glob("*/report.md"))
    return reports[-1] if reports else None


def _complete_task(wiki_root: Path, task_id: str) -> str:
    tasks_root = wiki_root / "data" / "growth-tasks"
    active_path = tasks_root / "active.json"
    archive_path = tasks_root / "archive.json"
    if not active_path.exists():
        return ""
    active_tasks = json.loads(active_path.read_text(encoding="utf-8"))
    archive_tasks = []
    if archive_path.exists():
        archive_tasks = json.loads(archive_path.read_text(encoding="utf-8"))
    remaining = []
    completed_task = None
    for task in active_tasks:
        if isinstance(task, dict) and task.get("id") == task_id:
            completed_task = task
            continue
        remaining.append(task)
    if completed_task is None:
        return ""
    completed_task["status"] = "completed"
    completed_task["archived_at"] = utc_now_iso()
    archive_by_id = {str(task.get("id")): task for task in archive_tasks if isinstance(task, dict) and task.get("id")}
    archive_by_id[task_id] = completed_task
    active_path.write_text(json.dumps(remaining, ensure_ascii=False, indent=2), encoding="utf-8")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(json.dumps(list(archive_by_id.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    return task_id


def _ingest_summary(result: object) -> str:
    raw_source = getattr(result, "raw_source")
    write_result = getattr(result, "write_result", None)
    if write_result:
        return json.dumps({"rawSourceId": raw_source.id, "wikiTargetPath": write_result.target_path}, ensure_ascii=False)
    return raw_source.id


def _prompt_metadata(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


if __name__ == "__main__":
    raise SystemExit(main())
