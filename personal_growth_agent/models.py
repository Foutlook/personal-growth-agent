from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Sensitivity = Literal["safe", "redacted", "local_only"]
EvidenceStatus = Literal["Observed", "Inferred", "Unknown", "HumanConfirmed"]
GrowthMemoryType = Literal["growth_cycle", "diagnosis", "growth_task", "growth_review", "maturity_snapshot", "profile_snapshot", "report_summary"]
GrowthMemoryLifecycleStatus = Literal["proposed", "active", "completed", "carried_forward", "stale", "superseded", "rejected"]


@dataclass
class ConversationSession:
    id: str
    source: str
    started_at: str
    ended_at: str
    messages: list[dict[str, str]]
    tool_calls: list[dict[str, Any]]
    referenced_files: list[str]
    project_paths: list[str]
    task_type: str
    outcome: str
    source_ref: str


@dataclass
class RawSource:
    id: str
    type: str
    path: str
    origin: str
    created_at: str
    hash: str
    sensitivity: Sensitivity
    mutable: bool = False


@dataclass
class KnowledgeSourceInput:
    source_type: str
    title: str
    content: str
    original_location: str
    origin_url: str = ""
    publisher: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    fetch_requested: bool = False
    final_url: str = ""
    fetch_status: str = ""


@dataclass
class KnowledgeGap:
    id: str
    title: str
    source_raw_ids: list[str]
    tracks: list[str]
    summary: str
    confidence: float
    review_state: str


@dataclass
class KnowledgeIngestResult:
    raw_source: RawSource
    proposal: "WikiUpdateProposal"
    gaps: list[KnowledgeGap]
    manifest_entry: dict[str, Any]
    write_result: "WikiWriteResult | None" = None


@dataclass
class SourceManifest:
    source_id: str
    raw_source_id: str
    original_location: str
    ingested_at: str
    source_type: str
    tool: str
    redaction_status: str
    hash: str


@dataclass
class EvidenceItem:
    id: str
    source_session_id: str
    source_ref: str
    category: str
    signal: str
    summary: str
    sensitivity: Sensitivity
    confidence: float
    tags: list[str] = field(default_factory=list)


@dataclass
class EvidenceSignal:
    id: str
    name: str
    category: str
    polarity: str
    observed_in_evidence_ids: list[str]
    frequency: int
    contexts: list[str]
    confidence: float
    supports_maturity: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Diagnosis:
    id: str
    type: str
    title: str
    target_tracks: list[str]
    summary: str
    confidence: float
    supporting_signal_ids: list[str]
    supporting_evidence_ids: list[str]
    recommended_focus: str


@dataclass
class MaturityEstimate:
    track: str
    estimated_level: str
    confidence: float
    status: Literal["Observed", "Inferred", "Unknown"]
    observed_signals: list[str]
    missing_signals_for_next_level: list[str]
    caution: str = ""


@dataclass
class GrowthTask:
    id: str
    cycle_id: str
    title: str
    primary_track: str
    secondary_tracks: list[str]
    maturity_move: dict[str, str]
    task_type: str
    level: str
    time_budget_minutes: int
    why_this_task: str
    start_here: list[str]
    source_diagnosis_ids: list[str]
    steps: list[str]
    output_path: str
    output_example: str
    done_definition: list[str]
    review_questions: list[str]
    expected_artifacts: list[str]
    glossary: dict[str, str] = field(default_factory=dict)


@dataclass
class ActionAsset:
    id: str
    type: str
    title: str
    trigger: str
    target_tool: str
    content: str
    usage_instruction: str
    source_task_ids: list[str]
    source_diagnosis_ids: list[str]
    source_evidence_ids: list[str]
    review_metric: str
    export_path: str


@dataclass
class WikiPage:
    id: str
    title: str
    path: str
    type: str
    status: str
    source_evidence_ids: list[str]
    source_raw_ids: list[str]
    linked_pages: list[str]
    tracks: list[str]
    confidence: float
    last_reviewed_at: str
    lifecycle_status: str = "proposed"
    source_run_id: str = ""
    evidence_status: str = "Unknown"
    human_confirmed: bool = False
    valid_until: str = ""
    review_state: str = "pending"


@dataclass
class WikiUpdateProposal:
    id: str
    type: str
    target_path: str
    reason: str
    source_evidence_ids: list[str]
    source_raw_ids: list[str]
    diff_path: str
    risk: str
    requires_human_review: bool
    status: str


@dataclass
class WikiWriteResult:
    id: str
    target_path: str
    path: str
    operation: str
    source_evidence_ids: list[str]
    source_raw_ids: list[str]
    prompt_id: str = ""
    prompt_version: str = ""
    prompt_path: str = ""
    prompt_digest: str = ""
    compiler: str = "local_rule"
    provider: str = ""
    model: str = ""
    content_hash: str = ""
    written_at: str = ""


@dataclass
class WikiLintIssue:
    id: str
    severity: str
    page_path: str
    type: str
    message: str
    suggested_fix: str


@dataclass
class GrowthMemoryMetadata:
    type: GrowthMemoryType
    lifecycle_status: GrowthMemoryLifecycleStatus
    source_run_id: str
    source_evidence_ids: list[str]
    source_raw_ids: list[str]
    evidence_status: EvidenceStatus
    confidence: float
    human_confirmed: bool
    valid_until: str
    review_state: str
    tracks: list[str]
    related: list[str] = field(default_factory=list)


@dataclass
class GrowthRunSnapshot:
    id: str
    run_id: str
    path: str
    source_evidence_ids: list[str]
    source_raw_ids: list[str]
    created_at: str
    hash: str


@dataclass
class GrowthReview:
    id: str
    task_id: str
    source_run_id: str
    completed: bool
    usefulness: str
    blockers: list[str]
    follow_up_evidence_ids: list[str]
    created_at: str


@dataclass
class GrowthMemoryContext:
    active_diagnoses: list[dict[str, Any]] = field(default_factory=list)
    active_tasks: list[dict[str, Any]] = field(default_factory=list)
    recent_reviews: list[dict[str, Any]] = field(default_factory=list)
    maturity_snapshots: list[dict[str, Any]] = field(default_factory=list)
    north_star_pages: list[str] = field(default_factory=list)
    inferred_memory: list[dict[str, Any]] = field(default_factory=list)
    human_confirmed_memory: list[dict[str, Any]] = field(default_factory=list)
    knowledge_summaries: list[dict[str, Any]] = field(default_factory=list)
    knowledge_gaps: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DashboardBuildResult:
    entry_path: str
    data_path: str
    assets_path: str
    omitted_local_only_count: int


@dataclass
class OutboundPayloadPreview:
    target: str
    purpose: str
    included_evidence_count: int
    redacted_items_count: int
    contains_raw_code: bool
    contains_original_messages: bool
    payload_digest: str


@dataclass
class RepositoryEvidencePack:
    path: str
    git_summary: dict[str, Any]
    structure_summary: dict[str, Any]
    signals: dict[str, bool]
    sensitivity_notes: list[str]
    skipped_paths: list[str]
    source_references: list[str]


@dataclass
class GrowthCycle:
    id: str
    theme: str
    cadence: str
    constraints: dict[str, Any]
    maturity_estimates: list[MaturityEstimate]
    diagnoses: list[Diagnosis]
    tasks: list[GrowthTask]
    action_asset_ids: list[str] = field(default_factory=list)
    wiki_update_proposal_ids: list[str] = field(default_factory=list)
