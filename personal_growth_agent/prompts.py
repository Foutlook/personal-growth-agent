from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .utils import sha256_text


SCENARIO_PROMPTS = {
    "role_profile": "role_profile.zh.md",
    "maturity_scoring": "maturity_scoring.zh.md",
    "growth_planning": "growth_planning.zh.md",
    "evidence_enrichment": "evidence_enrichment.zh.md",
    "knowledge_ingest": "knowledge_ingest.zh.md",
    "wiki_maintenance": "wiki_maintenance.zh.md",
    "report_generation": "report_generation.zh.md",
}


@dataclass
class PromptTemplate:
    id: str
    version: str
    scenario: str
    path: str
    content: str
    digest: str


class PromptRegistry:
    def __init__(self, workspace: Path, prompt_dir: Path | None = None, explicit_prompts: dict[str, Path] | None = None):
        self.workspace = workspace
        self.prompt_dir = prompt_dir or workspace / "prompts"
        self.explicit_prompts = explicit_prompts or {}
        self.package_dir = Path(__file__).parent / "default_prompts"

    def ensure_workspace_prompts(self) -> None:
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        for scenario, filename in SCENARIO_PROMPTS.items():
            target = self.prompt_dir / filename
            if target.exists():
                continue
            package_prompt = self.package_dir / filename
            content = package_prompt.read_text(encoding="utf-8") if package_prompt.exists() else _default_prompt(scenario)
            target.write_text(content, encoding="utf-8")

    def load(self, scenario: str) -> PromptTemplate:
        path = self._resolve_path(scenario)
        content = path.read_text(encoding="utf-8")
        metadata = _parse_frontmatter(content)
        prompt_id = str(metadata.get("id") or scenario)
        version = str(metadata.get("version") or "v1")
        return PromptTemplate(
            id=prompt_id,
            version=version,
            scenario=scenario,
            path=str(path),
            content=content,
            digest=sha256_text(content),
        )

    def _resolve_path(self, scenario: str) -> Path:
        explicit_path = self.explicit_prompts.get(scenario)
        if explicit_path:
            return explicit_path
        filename = SCENARIO_PROMPTS.get(scenario, f"{scenario}.zh.md")
        workspace_path = self.prompt_dir / filename
        if workspace_path.exists():
            return workspace_path
        package_path = self.package_dir / filename
        if package_path.exists():
            return package_path
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        fallback_path = self.prompt_dir / filename
        fallback_path.write_text(_default_prompt(scenario), encoding="utf-8")
        return fallback_path


def prompt_to_payload(prompt: PromptTemplate) -> dict[str, str]:
    return {
        "id": prompt.id,
        "version": prompt.version,
        "scenario": prompt.scenario,
        "path": prompt.path,
        "digest": prompt.digest,
        "content": prompt.content,
    }


def _parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _default_prompt(scenario: str) -> str:
    return "\n".join(
        [
            "---",
            f"id: {scenario}",
            "version: v1",
            "---",
            f"你是 Personal Growth Agent 的 {scenario} 分析器。",
            "只基于输入中的 evidenceIds、signals 和允许的 Wiki memory 输出 JSON。",
            "不要使用未提供的原始消息、代码或私人信息。",
            "",
        ]
    )
