## Why

The current MVP runs as a Python module with explicit source paths and a local-rules analyzer only. To make the system usable and open-source friendly, it needs an installable CLI, predictable workspace configuration, robust source discovery, and an optional LLM-enhanced analyzer that preserves local-first privacy guarantees.

## What Changes

- Package the project as an installable CLI with a `pga` command.
- Add workspace initialization and configuration so users can run the tool without passing paths every time.
- Define default user-level workspace behavior while still supporting explicit workspace and Wiki paths.
- Add source adapter discovery for Codex, Claude Code, and opencode with scan, inventory, parse status, and incremental processing metadata.
- Add analyzer provider abstraction with `local`, `openai-compatible`, and `ollama` provider modes.
- Add hybrid analysis modes where local-rules produce baseline evidence and LLMs enrich evidence, role inference, growth tasks, and Wiki update suggestions.
- Add outbound payload preview and explicit approval requirements before any external LLM call.
- Add LLM output schema validation and reconciliation rules so unsupported LLM claims cannot become high-confidence evidence.

## Capabilities

### New Capabilities
- `cli-workspace-management`: Defines installable CLI commands, workspace resolution, config files, and user-level defaults.
- `source-adapter-discovery`: Defines source adapters, scanning, default paths, incremental inventory, and parse status for Codex, Claude Code, and opencode.
- `analyzer-provider-interface`: Defines local, openai-compatible, ollama, and future provider interfaces.
- `llm-evidence-enrichment`: Defines how LLMs enrich local evidence, role/profile inference, candidate signals, growth tasks, and Wiki updates.
- `analyzer-output-validation`: Defines schema validation, evidence linkage, confidence handling, and local-rules/LLM reconciliation.

### Modified Capabilities
- `conversation-source-ingestion`: Source discovery becomes adapter-based and supports incremental scan metadata.
- `evidence-signal-extraction`: Evidence extraction can include validated LLM-enriched evidence in addition to local-rules output.
- `growth-cycle-execution`: Growth cycle generation can use validated LLM analysis while preserving evidence status and confidence constraints.
- `privacy-audit`: External analyzer payloads require preview, redaction, approval, and audit records.

## Impact

- Affected modules: CLI, configuration, source discovery/parsing, evidence extraction, growth generation, privacy audit, reporting, and tests.
- Packaging changes: `pyproject.toml` gains a console script entrypoint and optional provider configuration support.
- New files are expected for config/workspace handling, source adapters, analyzer providers, prompt/schema contracts, and validation.
- No external LLM calls are made by default; `local` remains the default provider.
- External providers must respect privacy gates and are opt-in through config or command flags.
