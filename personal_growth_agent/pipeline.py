from __future__ import annotations

import json
import shutil
from pathlib import Path

from .analyzer import AnalyzerRequest, build_analyzer_payload, call_remote_provider, resolve_provider_credential, resolve_provider_route, validate_scenario_output
from .assets import export_action_assets, generate_action_assets
from .audit import create_outbound_preview
from .data import discover_sources, generate_source_inventory, parse_sources
from .evidence import aggregate_signals, extract_evidence
from .growth import generate_growth_cycle
from .reporting import write_reports
from .utils import to_jsonable, utc_now_iso, write_json
from .wiki import create_growth_memory_proposals, create_growth_run_snapshot, init_llm_wiki, lint_wiki, load_growth_memory_context, read_wiki_write_log
from .prompts import PromptRegistry, prompt_to_payload


def run_growth_cycle(source_paths: dict[str, list[Path]], output_root: Path, constraints: dict[str, object]) -> dict[str, str]:
    run_date = utc_now_iso()[:10]
    run_dir = output_root / "runs" / run_date
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    wiki_root = output_root / "llm-wiki"
    init_llm_wiki(wiki_root)
    memory_context = load_growth_memory_context(wiki_root)

    sources = discover_sources(source_paths)
    inventory = generate_source_inventory(sources)
    sessions, failures = parse_sources(sources)
    evidence = extract_evidence(sessions)
    signals = aggregate_signals(evidence)
    llm_config = constraints.get("llmConfig")
    provider_override = str(constraints.get("provider") or "")
    model_override = str(constraints.get("model") or "")
    if llm_config:
        provider_route = resolve_provider_route(llm_config, "role_profile", provider_override or None, model_override or None)
        provider = provider_route.provider
        model = provider_route.model
    else:
        provider = provider_override or "local"
        model = model_override
        provider_route = None
    analysis_mode = str(constraints.get("analysisMode") or getattr(llm_config, "default_analysis_mode", "local"))
    dry_run = bool(constraints.get("dryRun") or False)
    approve_outbound = bool(constraints.get("approveOutbound") or False)
    provider_transport = constraints.get("providerTransport")
    analyzer_payload_preview = None
    analyzer_validation = {
        "provider": provider,
        "model": model,
        "analysisMode": analysis_mode,
        "dryRun": dry_run,
        "approved": approve_outbound,
        "validationStatus": "local",
        "networkCalled": False,
        "prompts": [],
        "fallbackMode": "",
        "skipReason": "",
        "credentialSource": "",
        "message": "",
        "warnings": [],
        "responseDigest": "",
    }
    if provider != "local":
        prompt_dir = constraints.get("promptDir")
        prompt_root = Path(prompt_dir) if prompt_dir else output_root / "prompts"
        prompt = PromptRegistry(output_root, prompt_root).load("role_profile")
        prompt_payload = prompt_to_payload(prompt)
        analyzer_request = AnalyzerRequest(
            provider=provider,
            model=model,
            analysis_mode=analysis_mode,
            evidence=[{"id": item.id, "summary": item.summary, "sensitivity": item.sensitivity} for item in evidence],
            signals=[{"name": signal.name, "evidenceIds": signal.observed_in_evidence_ids, "confidence": signal.confidence} for signal in signals],
            wiki_memory=memory_context.active_tasks + memory_context.active_diagnoses,
            approved=approve_outbound,
            dry_run=dry_run,
            scenario="role_profile",
            prompt=prompt_payload,
            output_schema="role_profile_v1",
            provider_route=to_jsonable(provider_route) if provider_route else {},
        )
        credential = resolve_provider_credential(provider_route) if provider_route else None
        analyzer_validation["prompts"].append({key: prompt_payload[key] for key in ("id", "version", "scenario", "digest", "path") if key in prompt_payload})
        analyzer_validation["credentialSource"] = credential.source if credential else ""
        analyzer_validation["warnings"] = provider_route.warnings if provider_route else []
        analyzer_validation["fallbackMode"] = "local_rules"
        if credential and not credential.available:
            analyzer_validation["validationStatus"] = "skipped_missing_credentials"
            analyzer_validation["skipReason"] = "missing_credentials"
            analyzer_validation["message"] = credential.message
        else:
            payload, analyzer_payload_preview = build_analyzer_payload(analyzer_request, max_evidence_items=int(constraints.get("maxRemoteEvidenceItems") or 80))
            if dry_run:
                analyzer_validation["validationStatus"] = "dry_run"
                analyzer_validation["skipReason"] = "dry_run"
            elif not approve_outbound:
                analyzer_validation["validationStatus"] = "skipped_without_approval"
                analyzer_validation["skipReason"] = "missing_outbound_approval"
            else:
                remote_result = call_remote_provider(provider_route, payload, credential, provider_transport)
                analyzer_validation.update(remote_result.audit_metadata())
                if remote_result.output:
                    try:
                        validate_scenario_output("role_profile", remote_result.output, {item.id for item in evidence})
                        analyzer_validation["validationStatus"] = "accepted"
                        analyzer_validation["skipReason"] = ""
                    except Exception as exc:
                        analyzer_validation["validationStatus"] = "validation_error"
                        analyzer_validation["skipReason"] = "validation_error"
                        analyzer_validation["message"] = str(exc)
                elif remote_result.error:
                    analyzer_validation["skipReason"] = "provider_error"
                    analyzer_validation["message"] = remote_result.error
    cycle_constraints = {key: value for key, value in constraints.items() if key != "providerTransport"}
    cycle = generate_growth_cycle(signals, cycle_constraints, memory_context)
    active_tasks, archived_tasks = _sync_growth_tasks(wiki_root, cycle.tasks)
    cycle.tasks = active_tasks
    assets = generate_action_assets(cycle.tasks, cycle.diagnoses, evidence)
    export_action_assets(wiki_root, assets)

    write_json(run_dir / "source-inventory.json", inventory)
    write_json(run_dir / "evidence" / "evidence-items.json", evidence)
    write_json(run_dir / "evidence" / "signals.json", signals)
    write_json(run_dir / "evidence" / "maturity-estimate.json", cycle.maturity_estimates)
    write_json(run_dir / "evidence" / "diagnoses.json", cycle.diagnoses)
    write_json(run_dir / "growth-cycle" / "tasks.json", cycle.tasks)
    write_json(run_dir / "growth-cycle" / "archived-tasks.json", archived_tasks)
    (run_dir / "growth-cycle" / "plan.md").parent.mkdir(parents=True, exist_ok=True)
    (run_dir / "growth-cycle" / "plan.md").write_text("# GrowthCycle\n", encoding="utf-8")
    (run_dir / "growth-cycle" / "review-template.md").write_text("# Review\n", encoding="utf-8")
    write_json(run_dir / "wiki-updates" / "accepted-updates.json", [])
    write_json(run_dir / "wiki-updates" / "wiki-pages.json", [])
    growth_snapshot = create_growth_run_snapshot(
        wiki_root,
        cycle.id,
        {
            "runDir": str(run_dir),
            "sourceInventory": inventory,
            "evidenceIds": [item.id for item in evidence],
            "signalIds": [signal.id for signal in signals],
            "diagnosisIds": [diagnosis.id for diagnosis in cycle.diagnoses],
            "taskIds": [task.id for task in cycle.tasks],
            "maturityTracks": [estimate.track for estimate in cycle.maturity_estimates],
            "reportPath": str(run_dir / "report.md"),
        },
        [item.id for item in evidence],
        [],
    )
    growth_memory_proposals = create_growth_memory_proposals(wiki_root, cycle, growth_snapshot, [item.id for item in evidence[:5]])
    write_json(run_dir / "wiki-updates" / "growth-memory-updates.json", growth_memory_proposals)
    lint_issues = lint_wiki(wiki_root)
    (run_dir / "wiki-updates" / "wiki-lint-report.md").write_text("\n".join(issue.message for issue in lint_issues) or "No lint issues.", encoding="utf-8")
    preview = create_outbound_preview("none", "local-rule-baseline", [item.id for item in evidence], [], "local only")
    outbound_payloads = [preview]
    if analyzer_payload_preview:
        outbound_payloads.append(analyzer_payload_preview)
    wiki_writes = read_wiki_write_log(wiki_root)
    write_json(
        run_dir / "privacy-audit.json",
        {
            "sourcesUsed": [item["name"] for item in inventory["sources"]],
            "parseFailures": [to_jsonable(item) for item in failures],
            "outboundPayloads": outbound_payloads,
            "analyzer": analyzer_validation,
            "actionAssets": [asset.id for asset in assets],
            "wikiUpdates": [],
            "wikiWrites": wiki_writes,
            "growthRunSnapshots": [growth_snapshot.id],
            "growthMemoryUpdates": [proposal.id for proposal in growth_memory_proposals],
            "lintPrivacyFindings": [],
        },
    )
    write_reports(run_dir, cycle, evidence, signals, assets, [], lint_issues, growth_snapshot, growth_memory_proposals, analyzer_validation)
    return {"run_dir": str(run_dir), "wiki_root": str(wiki_root)}
def _sync_growth_tasks(wiki_root: Path, candidate_tasks: list) -> tuple[list, list[dict[str, object]]]:
    tasks_root = wiki_root / "data" / "growth-tasks"
    active_path = tasks_root / "active.json"
    archive_path = tasks_root / "archive.json"
    tasks_root.mkdir(parents=True, exist_ok=True)
    active_records = _read_task_records(active_path)
    archive_records = _read_task_records(archive_path)
    completed_records = [record for record in active_records if str(record.get("status") or "") == "completed"]
    still_active_records = [record for record in active_records if str(record.get("status") or "") != "completed"]
    archive_by_id = {str(record.get("id")): record for record in archive_records if record.get("id")}
    for record in completed_records:
        record["archived_at"] = utc_now_iso()
        archive_by_id[str(record.get("id"))] = record
    active_by_id = {str(record.get("id")): record for record in still_active_records if record.get("id")}
    for task in candidate_tasks:
        if task.id in archive_by_id:
            continue
        active_by_id.setdefault(task.id, _task_record(task))
    active_ids = set(active_by_id)
    synced_tasks = [task for task in candidate_tasks if task.id in active_ids and task.id not in archive_by_id]
    write_json(active_path, list(active_by_id.values()))
    write_json(archive_path, list(archive_by_id.values()))
    return synced_tasks, list(archive_by_id.values())


def _read_task_records(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _task_record(task) -> dict[str, object]:
    record = to_jsonable(task)
    record["status"] = "active"
    record["created_at"] = utc_now_iso()
    record["updated_at"] = utc_now_iso()
    return record
