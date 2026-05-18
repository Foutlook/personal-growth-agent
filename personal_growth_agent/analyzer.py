from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .audit import assert_no_sensitive_content, create_outbound_preview, redact_text
from .models import OutboundPayloadPreview
from .utils import sha256_text


@dataclass
class AnalyzerConfig:
    provider: str = "local"
    model: str = ""
    base_url: str = ""
    api_key_env: str = ""
    analysis_mode: str = "local"
    approve_outbound: bool = False
    timeout_seconds: int = 30


@dataclass
class AnalyzerRequest:
    provider: str
    model: str
    analysis_mode: str
    evidence: list[dict[str, Any]]
    signals: list[dict[str, Any]]
    wiki_memory: list[dict[str, Any]]
    approved: bool
    dry_run: bool
    scenario: str = "evidence_enrichment"
    prompt: dict[str, Any] = field(default_factory=dict)
    output_schema: str = "analyzer_v1"
    provider_route: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyzerResponse:
    provider: str
    model: str
    analysis_mode: str
    payload_preview: OutboundPayloadPreview | None
    output: dict[str, Any]
    validation_status: str
    network_called: bool = False
    errors: list[str] = field(default_factory=list)
    scenario: str = ""
    prompt: dict[str, Any] = field(default_factory=dict)
    fallback_reason: str = ""


@dataclass
class ProviderRoute:
    provider: str
    model: str
    base_url: str
    api_key: str
    api_key_env: str
    timeout_seconds: int
    approval_required: bool = True
    models: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProviderCredential:
    source: str
    available: bool
    value: str = ""
    message: str = ""


@dataclass
class RemoteProviderResult:
    output: dict[str, Any]
    network_called: bool
    validation_status: str
    error: str = ""
    credential_source: str = ""
    response_digest: str = ""

    def audit_metadata(self) -> dict[str, Any]:
        return {
            "networkCalled": self.network_called,
            "validationStatus": self.validation_status,
            "error": self.error,
            "credentialSource": self.credential_source,
            "responseDigest": self.response_digest,
        }


class LocalAnalyzerProvider:
    provider = "local"

    def analyze(self, request: AnalyzerRequest) -> AnalyzerResponse:
        return AnalyzerResponse(
            provider="local",
            model="local-rules",
            analysis_mode=request.analysis_mode,
            payload_preview=None,
            output={"candidateSignals": [], "growthTasks": [], "wikiUpdates": []},
            validation_status="skipped",
            network_called=False,
        )


def build_analyzer_payload(request: AnalyzerRequest, max_evidence_items: int | None = None) -> tuple[dict[str, Any], OutboundPayloadPreview]:
    safe_evidence = []
    redacted_count = 0
    evidence_items = request.evidence[:max_evidence_items] if max_evidence_items is not None else request.evidence
    omitted_evidence_count = max(0, len(request.evidence) - len(evidence_items))
    for item in evidence_items:
        if item.get("sensitivity") == "local_only":
            redacted_count += 1
            continue
        summary = str(item.get("summary") or "")
        redacted_summary, findings = redact_text(summary)
        redacted_count += len(findings)
        safe_evidence.append({"id": item.get("id"), "summary": redacted_summary, "sensitivity": item.get("sensitivity", "safe")})
    payload = {
        "analysisMode": request.analysis_mode,
        "scenario": request.scenario,
        "provider": request.provider,
        "model": request.model,
        "prompt": {
            "id": request.prompt.get("id"),
            "version": request.prompt.get("version"),
            "scenario": request.prompt.get("scenario") or request.scenario,
            "digest": request.prompt.get("digest"),
            "content": request.prompt.get("content"),
        },
        "outputSchema": request.output_schema,
        "evidence": safe_evidence,
        "signals": request.signals,
        "wikiMemory": request.wiki_memory,
    }
    if omitted_evidence_count:
        payload["omittedEvidenceCount"] = omitted_evidence_count
    payload_text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    assert_no_sensitive_content(payload_text)
    preview = create_outbound_preview(request.provider, "llm-evidence-enrichment", [str(item.get("id")) for item in safe_evidence], [], payload_text)
    preview.redacted_items_count = redacted_count
    return payload, preview


def resolve_provider_route(llm_config: Any, scenario: str, provider_override: str | None = None, model_override: str | None = None) -> ProviderRoute:
    scenario_config = getattr(llm_config, "scenarios", {}).get(scenario)
    scenario_provider = getattr(scenario_config, "provider", "") if scenario_config else ""
    scenario_model = getattr(scenario_config, "model", "") if scenario_config else ""
    provider_name = provider_override or scenario_provider or getattr(llm_config, "default_provider", "local")
    providers = getattr(llm_config, "providers", {})
    provider_config = providers.get(provider_name)
    if not provider_config:
        provider_config = _fallback_provider_config(provider_name)
    default_model = getattr(llm_config, "default_model", "")
    requested_model = model_override or scenario_model or getattr(provider_config, "default_model", "") or default_model
    models = getattr(provider_config, "models", {}) if provider_config else {}
    model = _resolve_model_preset(str(requested_model), models)
    warnings = _legacy_model_warnings(provider_name, model)
    if not provider_config:
        return ProviderRoute(provider=provider_name, model=model, base_url="", api_key="", api_key_env="", timeout_seconds=30, warnings=warnings)
    return ProviderRoute(
        provider=getattr(provider_config, "provider", provider_name),
        model=model,
        base_url=getattr(provider_config, "base_url", ""),
        api_key=getattr(provider_config, "api_key", ""),
        api_key_env=getattr(provider_config, "api_key_env", ""),
        timeout_seconds=int(getattr(provider_config, "timeout_seconds", 60)),
        approval_required=True,
        models=dict(models),
        warnings=warnings,
    )


def _fallback_provider_config(provider_name: str) -> Any | None:
    defaults = {
        "deepseek": {
            "provider": "deepseek",
            "base_url": "https://api.deepseek.com",
            "api_key": "",
            "api_key_env": "PGA_DEEPSEEK_API_KEY",
            "default_model": "deepseek-v4-flash",
            "timeout_seconds": 60,
            "models": {"flash": "deepseek-v4-flash", "pro": "deepseek-v4-pro"},
        },
        "openai": {
            "provider": "openai",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "api_key_env": "PGA_OPENAI_API_KEY",
            "default_model": "gpt-5.4",
            "timeout_seconds": 60,
            "models": {},
        },
    }
    value = defaults.get(provider_name)
    if not value:
        return None
    return type("FallbackProviderConfig", (), value)()


def resolve_provider_credential(route: ProviderRoute, env: dict[str, str] | None = None) -> ProviderCredential:
    if route.provider in {"local", "ollama"}:
        return ProviderCredential(source="none", available=True)
    file_key = route.api_key.strip()
    if file_key:
        return ProviderCredential(source="file", available=True, value=file_key)
    env_values = os.environ if env is None else env
    env_key = env_values.get(route.api_key_env, "").strip() if route.api_key_env else ""
    if env_key:
        return ProviderCredential(source="env", available=True, value=env_key)
    message = _missing_credential_message(route)
    return ProviderCredential(source="missing", available=False, message=message)


def build_provider_request(route: ProviderRoute, payload: dict[str, Any], credential: ProviderCredential | None = None) -> dict[str, Any]:
    system_content = _build_system_content(payload)
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, sort_keys=True)},
    ]
    resolved_credential = credential or resolve_provider_credential(route)
    if route.provider in {"deepseek", "openai", "openai-compatible"}:
        return {
            "provider": route.provider,
            "baseUrl": route.base_url,
            "apiKeyEnv": route.api_key_env,
            "credentialSource": resolved_credential.source,
            "timeoutSeconds": route.timeout_seconds,
            "body": {
                "model": route.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
            },
        }
    if route.provider == "ollama":
        return {
            "provider": "ollama",
            "baseUrl": route.base_url,
            "timeoutSeconds": route.timeout_seconds,
            "body": {"model": route.model, "messages": messages, "stream": False},
        }
    return {"provider": route.provider, "body": {"model": route.model, "messages": messages}}


def call_remote_provider(route: ProviderRoute, payload: dict[str, Any], credential: ProviderCredential, transport: Any | None = None) -> RemoteProviderResult:
    if not credential.available:
        return RemoteProviderResult(output={}, network_called=False, validation_status="skipped_missing_credentials", error=credential.message, credential_source=credential.source)
    if route.provider not in {"deepseek", "openai", "openai-compatible"}:
        return RemoteProviderResult(output={}, network_called=False, validation_status="unsupported_provider", error=f"unsupported provider: {route.provider}", credential_source=credential.source)
    request = build_provider_request(route, payload, credential)
    url = _chat_completions_url(route.base_url)
    headers = {"Authorization": f"Bearer {credential.value}", "Content-Type": "application/json"}
    body = request["body"]
    try:
        response = transport(url, headers, body, route.timeout_seconds) if transport else _urlopen_json(url, headers, body, route.timeout_seconds)
        output = _extract_provider_output(response)
        return RemoteProviderResult(output=output, network_called=True, validation_status="returned", credential_source=credential.source, response_digest=response_digest(output))
    except Exception as exc:
        return RemoteProviderResult(output={}, network_called=True, validation_status="provider_error", error=str(exc), credential_source=credential.source)


def validate_scenario_output(scenario: str, output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    if scenario == "role_profile":
        return _validate_role_profile(output, known_evidence_ids)
    if scenario == "maturity_scoring":
        return _validate_maturity_scoring(output, known_evidence_ids)
    if scenario == "growth_planning":
        return _validate_growth_planning(output, known_evidence_ids)
    if scenario in {"knowledge_ingest", "wiki_maintenance"}:
        return _validate_wiki_scenario(output, known_evidence_ids)
    return validate_llm_analysis(output, known_evidence_ids)


def validate_llm_analysis(output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    if not isinstance(output, dict):
        raise ValueError("analyzer output must be an object")
    normalized = {
        "roleInference": output.get("roleInference") or {},
        "strengths": output.get("strengths") or [],
        "risks": output.get("risks") or [],
        "candidateSignals": output.get("candidateSignals") or [],
        "growthTasks": output.get("growthTasks") or [],
        "wikiUpdates": output.get("wikiUpdates") or [],
    }
    _validate_claim("roleInference", normalized["roleInference"], known_evidence_ids, allow_empty=True)
    for field_name in ("strengths", "risks", "candidateSignals", "growthTasks", "wikiUpdates"):
        if not isinstance(normalized[field_name], list):
            raise ValueError(f"{field_name} must be a list")
        for claim in normalized[field_name]:
            _validate_claim(field_name, claim, known_evidence_ids, allow_empty=False)
            assert_no_sensitive_content(json.dumps(claim, ensure_ascii=False))
    return normalized


def reconcile_signals(local_signals: list[dict[str, Any]], llm_signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    local_by_name = {str(signal.get("name")): signal for signal in local_signals}
    reconciled: list[dict[str, Any]] = []
    seen: set[str] = set()
    for llm_signal in llm_signals:
        name = str(llm_signal.get("name"))
        seen.add(name)
        local_signal = local_by_name.get(name)
        if local_signal:
            local_confidence = float(local_signal.get("confidence") or 0)
            llm_confidence = float(llm_signal.get("confidence") or 0)
            reconciled.append({**local_signal, "confidence": min(0.95, max(local_confidence, llm_confidence) + 0.05), "status": "agreed", "provenance": ["local", "llm"]})
        else:
            reconciled.append({**llm_signal, "status": "llm_candidate", "provenance": ["llm"]})
    for name, local_signal in local_by_name.items():
        if name not in seen:
            reconciled.append({**local_signal, "status": "local_only", "provenance": ["local"]})
    return reconciled


def response_digest(output: dict[str, Any]) -> str:
    return sha256_text(json.dumps(output, ensure_ascii=False, sort_keys=True))


def _validate_role_profile(output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    role = output.get("roleInference")
    if not isinstance(role, dict):
        raise ValueError("roleInference is required")
    _validate_claim("roleInference", role, known_evidence_ids, allow_empty=False)
    return {"roleInference": role, "strengths": output.get("strengths") or [], "risks": output.get("risks") or []}


def _validate_maturity_scoring(output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    estimates = output.get("maturityEstimates") or []
    if not isinstance(estimates, list) or not estimates:
        raise ValueError("maturityEstimates must be a non-empty list")
    for estimate in estimates:
        _validate_claim("maturityEstimates", estimate, known_evidence_ids, allow_empty=False)
    return {"maturityEstimates": estimates}


def _validate_growth_planning(output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    tasks = output.get("growthTasks") or []
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("growthTasks must be a non-empty list")
    for task in tasks:
        _validate_claim("growthTasks", task, known_evidence_ids, allow_empty=False)
        if not task.get("steps") or not task.get("doneDefinition") or not task.get("reviewQuestions") or not task.get("track"):
            raise ValueError("growth task requires track, steps, doneDefinition, and reviewQuestions")
    return {"growthTasks": tasks}


def _validate_wiki_scenario(output: dict[str, Any], known_evidence_ids: set[str]) -> dict[str, Any]:
    updates = output.get("wikiUpdates") or output.get("knowledgeUpdates") or []
    if not isinstance(updates, list):
        raise ValueError("wiki updates must be a list")
    for update in updates:
        _validate_claim("wikiUpdates", update, known_evidence_ids, allow_empty=False)
    return {"wikiUpdates": updates}


def _validate_claim(field_name: str, claim: Any, known_evidence_ids: set[str], allow_empty: bool) -> None:
    if not claim:
        if allow_empty:
            return
        raise ValueError(f"{field_name} claim is empty")
    if not isinstance(claim, dict):
        raise ValueError(f"{field_name} claim must be an object")
    evidence_ids = claim.get("evidenceIds") or claim.get("sourceEvidenceIds") or []
    if not evidence_ids and not allow_empty:
        raise ValueError(f"{field_name} claim requires evidenceIds")
    for evidence_id in evidence_ids:
        if str(evidence_id) not in known_evidence_ids:
            raise ValueError(f"unknown evidence id: {evidence_id}")


def _resolve_model_preset(model: str, models: dict[str, str]) -> str:
    if model in models:
        return models[model]
    return model


def _legacy_model_warnings(provider_name: str, model: str) -> list[str]:
    provider = provider_name.lower()
    if provider != "deepseek":
        return []
    if model not in {"deepseek-chat", "deepseek-reasoner"}:
        return []
    return [f"DeepSeek model {model} is deprecated on 2026-07-24; use deepseek-v4-flash or deepseek-v4-pro."]


def _missing_credential_message(route: ProviderRoute) -> str:
    options = ["llm.providers.<provider>.api_key"]
    if route.api_key_env:
        options.append(f"environment variable {route.api_key_env}")
    return f"Missing API key for provider {route.provider}. Configure {' or '.join(options)} before remote analysis."


def _build_system_content(payload: dict[str, Any]) -> str:
    prompt = payload.get("prompt") if isinstance(payload.get("prompt"), dict) else {}
    prompt_content = str(prompt.get("content") or "")
    schema = str(payload.get("outputSchema") or "")
    lines = [
        "You are Personal Growth Agent. Return JSON only.",
        prompt_content,
    ]
    if schema == "role_profile_v1":
        lines.extend(
            [
                "Required JSON schema:",
                '{"roleInference":{"currentRole":"string","level":"string","confidence":0.0,"evidenceIds":["ev_id"],"cautions":["string"]},"strengths":[],"risks":[]}',
                "Every claim MUST include evidenceIds from the provided evidence.",
                "Do not include markdown fences or prose outside JSON.",
            ]
        )
    return "\n".join(line for line in lines if line)


def _chat_completions_url(base_url: str) -> str:
    normalized = (base_url or "").rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _urlopen_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"provider HTTP {exc.code}: {error_text}") from exc
    value = json.loads(response_text)
    if not isinstance(value, dict):
        raise ValueError("provider response must be an object")
    return value


def _extract_provider_output(response: dict[str, Any]) -> dict[str, Any]:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("provider response missing choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("provider choice must be an object")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("provider response missing message")
    content = message.get("content")
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise ValueError("provider message content must be JSON text")
    value = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError("provider output must be an object")
    return value
