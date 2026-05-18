from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


DEFAULT_WORKSPACE = Path.home() / "pga-workspace"


@dataclass
class SourceConfig:
    enabled: bool = True
    paths: list[Path] = field(default_factory=list)


@dataclass
class ProviderConfig:
    provider: str = "local"
    model: str = ""
    base_url: str = ""
    api_key_env: str = ""
    analysis_mode: str = "local"
    approve_outbound: bool = False
    timeout_seconds: int = 30


@dataclass
class LlmProviderConfig:
    provider: str
    base_url: str = ""
    api_key: str = ""
    api_key_env: str = ""
    default_model: str = ""
    timeout_seconds: int = 60
    models: dict[str, str] = field(default_factory=dict)


@dataclass
class LlmScenarioConfig:
    provider: str = ""
    model: str = ""
    prompt: str = ""
    requires_approval: bool = True


@dataclass
class LlmConfig:
    default_provider: str = "deepseek"
    default_model: str = "deepseek-v4-flash"
    default_analysis_mode: str = "llm_first"
    prompt_dir: Path = DEFAULT_WORKSPACE / "prompts"
    approve_outbound: bool = False
    providers: dict[str, LlmProviderConfig] = field(default_factory=dict)
    scenarios: dict[str, LlmScenarioConfig] = field(default_factory=dict)


@dataclass
class AppConfig:
    workspace: Path = DEFAULT_WORKSPACE
    wiki: Path | None = None
    sources: dict[str, SourceConfig] = field(default_factory=dict)
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    llm: LlmConfig = field(default_factory=LlmConfig)


@dataclass
class ResolvedPaths:
    workspace: Path
    wiki: Path
    runs: Path
    cache: Path
    config: Path
    source_manifests: Path


def load_config(path: Path | None) -> AppConfig:
    if not path or not path.exists():
        return AppConfig()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    workspace = Path(str(data.get("workspace") or DEFAULT_WORKSPACE)).expanduser()
    wiki_value = data.get("wiki")
    wiki = Path(str(wiki_value)).expanduser() if wiki_value else None
    provider_data = data.get("analyzer") or {}
    provider = ProviderConfig(
        provider=str(provider_data.get("provider") or "local"),
        model=str(provider_data.get("model") or ""),
        base_url=str(provider_data.get("base_url") or ""),
        api_key_env=str(provider_data.get("api_key_env") or ""),
        analysis_mode=str(provider_data.get("analysis_mode") or "local"),
        approve_outbound=bool(provider_data.get("approve_outbound") or False),
        timeout_seconds=int(provider_data.get("timeout_seconds") or 30),
    )
    llm = _load_llm_config(data.get("llm") or {}, workspace)
    sources: dict[str, SourceConfig] = {}
    source_data = data.get("sources") or {}
    if isinstance(source_data, dict):
        for name, value in source_data.items():
            if isinstance(value, dict):
                source_paths = [Path(str(item)).expanduser() for item in value.get("paths", [])]
                sources[str(name)] = SourceConfig(enabled=bool(value.get("enabled", True)), paths=source_paths)
    return AppConfig(workspace=workspace, wiki=wiki, sources=sources, provider=provider, llm=llm)


def write_default_config(path: Path, workspace: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            f'workspace = "{workspace.as_posix()}"',
            f'wiki = "{(workspace / "llm-wiki").as_posix()}"',
            "",
            "[analyzer]",
            'provider = "deepseek"',
            'model = "deepseek-v4-flash"',
            'base_url = ""',
            'api_key = ""',
            'api_key_env = ""',
            'analysis_mode = "llm_first"',
            "approve_outbound = false",
            "timeout_seconds = 30",
            "",
            "[llm]",
            'default_provider = "deepseek"',
            'default_model = "deepseek-v4-flash"',
            'default_analysis_mode = "llm_first"',
            f'prompt_dir = "{(workspace / "prompts").as_posix()}"',
            "approve_outbound = false",
            "",
            "[llm.providers.deepseek]",
            'provider = "deepseek"',
            'base_url = "https://api.deepseek.com"',
            'api_key = ""',
            'api_key_env = "PGA_DEEPSEEK_API_KEY"',
            'default_model = "deepseek-v4-flash"',
            "timeout_seconds = 60",
            "",
            "[llm.providers.deepseek.models]",
            'flash = "deepseek-v4-flash"',
            'pro = "deepseek-v4-pro"',
            "",
            "[llm.providers.openai]",
            'provider = "openai"',
            'base_url = "https://api.openai.com/v1"',
            'api_key = ""',
            'api_key_env = "PGA_OPENAI_API_KEY"',
            'default_model = "gpt-5.4"',
            "timeout_seconds = 60",
            "",
            "[llm.scenarios.role_profile]",
            'prompt = "role_profile.zh.md"',
            "",
            "[llm.scenarios.maturity_scoring]",
            'prompt = "maturity_scoring.zh.md"',
            "",
            "[llm.scenarios.growth_planning]",
            'prompt = "growth_planning.zh.md"',
            "",
            "[sources.codex]",
            "enabled = true",
            'paths = ["~/.codex"]',
            "",
            "[sources.claude_code]",
            "enabled = true",
            'paths = ["~/.claude"]',
            "",
            "[sources.opencode]",
            "enabled = true",
            'paths = ["~/.local/share/opencode"]',
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def _load_llm_config(data: object, workspace: Path) -> LlmConfig:
    if not isinstance(data, dict):
        return _default_llm_config(workspace)
    default_provider = str(data.get("default_provider") or "deepseek")
    default_model = str(data.get("default_model") or "deepseek-v4-flash")
    default_analysis_mode = str(data.get("default_analysis_mode") or "llm_first")
    prompt_dir = Path(str(data.get("prompt_dir") or workspace / "prompts")).expanduser()
    approve_outbound = bool(data.get("approve_outbound") or False)
    providers = _load_llm_providers(data.get("providers") or {})
    if not providers:
        providers = _default_llm_providers()
    scenarios = _load_llm_scenarios(data.get("scenarios") or {})
    return LlmConfig(
        default_provider=default_provider,
        default_model=default_model,
        default_analysis_mode=default_analysis_mode,
        prompt_dir=prompt_dir,
        approve_outbound=approve_outbound,
        providers=providers,
        scenarios=scenarios,
    )


def _load_llm_providers(data: object) -> dict[str, LlmProviderConfig]:
    providers: dict[str, LlmProviderConfig] = {}
    if not isinstance(data, dict):
        return providers
    for name, value in data.items():
        if not isinstance(value, dict):
            continue
        provider_name = str(value.get("provider") or name)
        providers[str(name)] = LlmProviderConfig(
            provider=provider_name,
            base_url=str(value.get("base_url") or ""),
            api_key=str(value.get("api_key") or ""),
            api_key_env=str(value.get("api_key_env") or ""),
            default_model=str(value.get("default_model") or ""),
            timeout_seconds=int(value.get("timeout_seconds") or 60),
            models={str(model_name): str(model_id) for model_name, model_id in (value.get("models") or {}).items()} if isinstance(value.get("models"), dict) else {},
        )
    return providers


def _load_llm_scenarios(data: object) -> dict[str, LlmScenarioConfig]:
    scenarios: dict[str, LlmScenarioConfig] = {}
    if not isinstance(data, dict):
        return scenarios
    for name, value in data.items():
        if not isinstance(value, dict):
            continue
        scenarios[str(name)] = LlmScenarioConfig(
            provider=str(value.get("provider") or ""),
            model=str(value.get("model") or ""),
            prompt=str(value.get("prompt") or ""),
            requires_approval=bool(value.get("requires_approval", True)),
        )
    return scenarios


def _default_llm_config(workspace: Path) -> LlmConfig:
    return LlmConfig(
        prompt_dir=workspace / "prompts",
        providers=_default_llm_providers(),
        scenarios={
            "role_profile": LlmScenarioConfig(prompt="role_profile.zh.md"),
            "maturity_scoring": LlmScenarioConfig(prompt="maturity_scoring.zh.md"),
            "growth_planning": LlmScenarioConfig(prompt="growth_planning.zh.md"),
        },
    )


def _default_llm_providers() -> dict[str, LlmProviderConfig]:
    return {
        "deepseek": LlmProviderConfig(
            provider="deepseek",
            base_url="https://api.deepseek.com",
            api_key_env="PGA_DEEPSEEK_API_KEY",
            default_model="deepseek-v4-flash",
            models={"flash": "deepseek-v4-flash", "pro": "deepseek-v4-pro"},
        ),
        "openai": LlmProviderConfig(provider="openai", base_url="https://api.openai.com/v1", api_key_env="PGA_OPENAI_API_KEY", default_model="gpt-5.4"),
    }


def resolve_paths(config: AppConfig, workspace_arg: Path | None, wiki_arg: Path | None, config_arg: Path | None, env: Mapping[str, str] | None = None) -> ResolvedPaths:
    env_values = env if env is not None else os.environ
    env_workspace = env_values.get("PGA_WORKSPACE")
    env_wiki = env_values.get("PGA_WIKI")
    env_config = env_values.get("PGA_CONFIG")
    workspace = Path(workspace_arg or env_workspace or config.workspace or DEFAULT_WORKSPACE).expanduser()
    if wiki_arg or env_wiki:
        wiki = Path(wiki_arg or env_wiki).expanduser()
    elif workspace_arg or env_workspace:
        wiki = workspace / "llm-wiki"
    else:
        wiki = Path(config.wiki or workspace / "llm-wiki").expanduser()
    config_path = Path(config_arg or env_config or workspace / "config.toml").expanduser()
    return ResolvedPaths(
        workspace=workspace,
        wiki=wiki,
        runs=workspace / "runs",
        cache=workspace / "cache",
        config=config_path,
        source_manifests=workspace / "source-manifests",
    )


def ensure_workspace(paths: ResolvedPaths) -> None:
    paths.workspace.mkdir(parents=True, exist_ok=True)
