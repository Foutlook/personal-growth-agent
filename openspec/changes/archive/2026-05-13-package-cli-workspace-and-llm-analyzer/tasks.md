## 1. CLI Packaging and Workspace

- [x] 1.1 Add `pga` console script entrypoint to package metadata.
- [x] 1.2 Replace the flat CLI with subcommands for `init`, `run`, `sources scan`, `report latest`, and `wiki path`.
- [x] 1.3 Implement workspace, Wiki, config, runs, cache, and source manifest path resolution.
- [x] 1.4 Implement `pga init` to create user-level workspace, config, runs, and LLM Wiki directories without overwriting existing files.
- [x] 1.5 Add tests for CLI help, workspace resolution order, init idempotency, latest report, and Wiki path output.

## 2. Configuration

- [x] 2.1 Add TOML config loading and writing using standard-library compatible behavior.
- [x] 2.2 Support source paths, workspace paths, provider settings, model settings, analysis mode, and outbound approval defaults in config.
- [x] 2.3 Support CLI flags and environment variables overriding config values.
- [x] 2.4 Add tests for missing config, partial config, env override, CLI override, and config roundtrip.

## 3. Source Adapter Discovery

- [x] 3.1 Define SourceAdapter contract for default paths, discovery, fingerprinting, parsing, and failure reporting.
- [x] 3.2 Implement Codex adapter using current fixture-compatible parsing.
- [x] 3.3 Implement Claude Code adapter using current fixture-compatible parsing.
- [x] 3.4 Implement opencode adapter using current fixture-compatible parsing.
- [x] 3.5 Implement `pga sources scan` output and persisted source scan manifest.
- [x] 3.6 Implement incremental scan behavior using file hash, mtime, size, adapter name, parse status, and prior run references.
- [x] 3.7 Add tests for adapter discovery, missing sources, corrupt files, parse failures, unchanged file reuse, and raw-content-free inventory.

## 4. Analyzer Provider Interface

- [x] 4.1 Define AnalyzerProvider request, response, provider metadata, and error models.
- [x] 4.2 Implement LocalAnalyzerProvider that wraps existing local-rules behavior.
- [x] 4.3 Implement openai-compatible provider request construction with base URL, model, API key env var, timeout, and dry-run support.
- [x] 4.4 Implement ollama provider request construction with endpoint, model, timeout, and dry-run support.
- [x] 4.5 Add tests that local provider performs no network call and non-local providers require configured model data.

## 5. Privacy Gate and Outbound Preview

- [x] 5.1 Build redacted analyzer payloads from EvidenceItem summaries, EvidenceSignal summaries, allowed Wiki growth memory, and source inventory metadata.
- [x] 5.2 Exclude raw messages, raw code, private identifiers, and local_only evidence from non-local analyzer payloads.
- [x] 5.3 Generate OutboundPayloadPreview for every non-local provider request.
- [x] 5.4 Implement `--dry-run` so payload preview is written and provider invocation is skipped.
- [x] 5.5 Implement approval gating so external calls require explicit CLI or config approval.
- [x] 5.6 Add privacy audit records for provider, model, payload digest, redaction counts, approval state, response digest, and validation state.
- [x] 5.7 Add tests for dry-run, missing approval, local_only exclusion, redaction counts, and audit output.

## 6. LLM Analysis Contract

- [x] 6.1 Define strict JSON schema for role inference, strengths, risks, candidate signals, growth tasks, and Wiki update suggestions.
- [x] 6.2 Add prompt pack files or embedded prompt templates for evidence enrichment and growth task suggestion.
- [x] 6.3 Implement schema validation for analyzer responses.
- [x] 6.4 Validate all LLM claims against known evidence IDs or safe source summary IDs.
- [x] 6.5 Reject malformed output, unsupported claims, sensitive content, and missing evidence references.
- [x] 6.6 Add tests for valid output, invalid JSON, unknown evidence IDs, missing required fields, and sensitive response content.

## 7. Local and LLM Reconciliation

- [x] 7.1 Implement reconciliation of local-rules signals with LLM candidate signals.
- [x] 7.2 Increase confidence only when local and LLM outputs agree and evidence references are valid.
- [x] 7.3 Preserve local evidence and mark conflicts when LLM contradicts local-rules signals.
- [x] 7.4 Keep missing evidence distinct from negative evidence in LLM-derived conclusions.
- [x] 7.5 Track analyzer provenance on accepted LLM-derived evidence, signals, tasks, and Wiki suggestions.
- [x] 7.6 Add tests for agreement, LLM-only candidate, contradiction, missing-evidence caution, and provenance.

## 8. Growth Cycle Integration

- [x] 8.1 Add analysis mode selection for `local`, `assist`, and `hybrid`.
- [x] 8.2 Use validated LLM candidate signals as supplemental evidence in assist and hybrid modes.
- [x] 8.3 Use validated LLM growth task suggestions as candidate tasks while enforcing GrowthTask validators.
- [x] 8.4 Ensure local fallback still generates a complete GrowthCycle when LLM provider is unavailable, unapproved, or invalid.
- [x] 8.5 Add tests for local mode, assist mode, hybrid mode, provider failure fallback, and invalid LLM fallback.

## 9. Reporting and CLI UX

- [x] 9.1 Update report outputs to show analyzer provider, analysis mode, outbound approval state, and LLM validation summary.
- [x] 9.2 Update report outputs to distinguish local-rules, LLM-derived, and reconciled signals.
- [x] 9.3 Update CLI command output to print run directory, Wiki path, provider mode, dry-run status, and next suggested command.
- [x] 9.4 Add smoke tests for `pga run`, `pga run --dry-run`, `pga sources scan`, `pga report latest`, and `pga wiki path`.

## 10. End-to-End Verification

- [x] 10.1 Add fixture analyzer responses for valid, invalid, conflicting, and missing-evidence cases.
- [x] 10.2 Run end-to-end local provider pipeline with adapter-based discovery.
- [x] 10.3 Run end-to-end dry-run openai-compatible pipeline without making network calls.
- [x] 10.4 Verify OpenSpec requirements map to automated tests or documented verification.
- [x] 10.5 Verify UTF-8 no BOM and no generated cache directories remain after test runs.
