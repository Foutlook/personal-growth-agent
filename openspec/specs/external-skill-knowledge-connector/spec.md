# external-skill-knowledge-connector Specification

## Purpose

Define the boundary between Growth Knowledge Hub and third-party knowledge skills such as IMA: host CLIs may use third-party skills to fetch or summarize content, while Growth Knowledge Hub stores durable local summaries and provenance.

## Requirements

### Requirement: Treat third-party skills as host-managed sources
The system SHALL NOT implement a generic third-party skill runtime inside Growth Knowledge Hub.

#### Scenario: User wants to use IMA or another knowledge skill
- **WHEN** the user asks to search, read, or fetch third-party knowledge
- **THEN** the host CLI uses its own configured skill/tool integration and passes only selected structured summaries or locators to Growth Knowledge Hub

### Requirement: Persist connector-derived summaries locally
The system SHALL accept summaries derived from third-party skills through the material ingestion workflow.

#### Scenario: Host imports an external skill result
- **WHEN** the host CLI summarizes a third-party item and calls `gkh.py ingest`
- **THEN** Growth Knowledge Hub writes a local summary page with source locator, summary policy, retention policy, and fetch-on-demand metadata

### Requirement: Avoid credential storage
The system MUST NOT store third-party skill credentials in Wiki pages, raw sources, dashboards, source manifests, or write logs.

#### Scenario: Connector credentials exist in the host CLI
- **WHEN** the host CLI uses credentials to access a third-party source
- **THEN** Growth Knowledge Hub receives no credential value and persists only safe source locator or provider metadata supplied in the structured summary

### Requirement: Keep full-content retrieval on demand
The system SHALL rely on the host CLI for future full-content retrieval when a local summary is insufficient.

#### Scenario: Local summary is insufficient
- **WHEN** a user asks a detailed question that cannot be answered from local summary pages
- **THEN** recall results indicate the original source locator so the host CLI can decide whether to fetch full content through the appropriate third-party skill

### Requirement: Support multiple third-party sources through the same summary shape
The system SHALL keep connector-derived local persistence source-agnostic.

#### Scenario: Different providers produce summaries
- **WHEN** summaries come from IMA, a web reader, local notes, or another host-managed skill
- **THEN** the same material ingestion schema can persist them with provider/source locator metadata and no provider-specific application code
