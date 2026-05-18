## 1. Project Foundation

- [x] 1.1 Choose the initial runtime, package manager, test framework, and CLI entrypoint for the local-first MVP.
- [x] 1.2 Create the project skeleton with separate modules for data, evidence, growth, assets, wiki, audit, repository, and reporting.
- [x] 1.3 Define core data models for ConversationSession, RawSource, SourceManifest, EvidenceItem, EvidenceSignal, Diagnosis, MaturityEstimate, GrowthCycle, GrowthTask, ActionAsset, WikiPage, WikiUpdateProposal, WikiLintIssue, and PrivacyAudit.
- [x] 1.4 Add fixture directories for sanitized conversations, repository summaries, expected evidence, expected growth cycles, and expected wiki outputs.

## 2. Conversation Source Ingestion

- [x] 2.1 Implement source discovery interfaces for Codex, Claude Code, and opencode with configurable default paths.
- [x] 2.2 Implement source inventory generation without exposing raw message content.
- [x] 2.3 Implement ConversationSession parsing for sanitized fixture records.
- [x] 2.4 Add parse failure handling that records unsupported or corrupt files and continues processing other files.
- [x] 2.5 Add local source references from ConversationSession records back to source map entries.
- [x] 2.6 Add tests for discovered, missing, valid, and unsupported conversation source cases.

## 3. Privacy And Audit Baseline

- [x] 3.1 Implement local redaction utilities for secrets, credentials, private identifiers, internal endpoints, company names, customer names, project codes, raw code, and personal privacy content.
- [x] 3.2 Implement EvidenceItem sensitivity classification with safe, redacted, and local_only states.
- [x] 3.3 Implement OutboundPayloadPreview generation for any external LLM payload.
- [x] 3.4 Implement PrivacyAudit output for source usage, skipped files, redaction counts, local_only items, outbound payload summaries, ActionAssets, WikiUpdateProposals, and lint privacy findings.
- [x] 3.5 Add tests that block unredacted sensitive content from outbound payloads, ActionAssets, WikiPages, and WikiUpdateProposals.

## 4. Evidence And Signal Pipeline

- [x] 4.1 Implement EvidenceItem extraction from ConversationSession and fixture repository summaries.
- [x] 4.2 Implement the MVP EvidenceSignal taxonomy for AI collaboration, Agent engineering, business depth, AI system management, and knowledge curation.
- [x] 4.3 Implement EvidenceSignal aggregation with frequency, contexts, confidence, and supported maturity tracks.
- [x] 4.4 Implement missing-evidence handling so absence of a signal does not become a negative conclusion.
- [x] 4.5 Add tests for MVP signal detection, repeated signal aggregation, sensitivity propagation, and missing evidence behavior.

## 5. Growth Cycle Execution

- [x] 5.1 Implement three-track North Star configuration for AI Agent engineering, business depth, and AI system management.
- [x] 5.2 Implement MaturityEstimate generation with Observed, Inferred, and Unknown evidence status.
- [x] 5.3 Implement Diagnosis generation from EvidenceSignal combinations.
- [x] 5.4 Implement GrowthTask templates for AI session flow analysis, Agent spec draft, business goal card, business process card, AI output rubric, and AI failure taxonomy.
- [x] 5.5 Implement task routing from Diagnosis, MaturityEstimate, Growth Constraints, and available case bindings.
- [x] 5.6 Add validators that reject GrowthTask outputs missing target track, maturity move, time budget, steps, done definition, review questions, evidence basis, or expected artifacts.
- [x] 5.7 Add tests for one complete MVP GrowthCycle with three executable tasks.

## 6. Action Asset Generation

- [x] 6.1 Implement ActionAsset generation for prompt_snippet, checklist, template, agent_rule, and playbook.
- [x] 6.2 Link each ActionAsset to source GrowthTask, Diagnosis, EvidenceItem, or RawSource references.
- [x] 6.3 Export valid ActionAssets under llm-wiki/machine-usable/ using type-specific subdirectories.
- [x] 6.4 Add privacy validation for generated ActionAsset content.
- [x] 6.5 Add tests for action asset generation, evidence linkage, export paths, and sensitive content blocking.

## 7. LLM Wiki Maintenance

- [x] 7.1 Implement llm-wiki/ initialization with AGENTS.md or SCHEMA.md, raw/, wiki/, machine-usable/, diff/, report/, and data/.
- [x] 7.2 Implement RawSource ingestion that writes new raw entries or source manifest entries without overwriting existing raw content.
- [x] 7.3 Implement SourceManifest generation linking original local source pointers, RawSource IDs, evidence IDs, and wiki update proposals.
- [x] 7.4 Implement WikiPage draft generation with required frontmatter.
- [x] 7.5 Implement WikiUpdateProposal generation with target path, reason, source references, diff path, risk, review requirement, and status.
- [x] 7.6 Enforce diff-first behavior so existing wiki/ pages remain unchanged until proposal approval.
- [x] 7.7 Implement Wiki Lint checks for missing sources, broken links, stale claims, duplicate pages, privacy risk, and invalid frontmatter.
- [x] 7.8 Add tests for llm-wiki/ structure, raw immutability, frontmatter validity, proposal state, diff-first behavior, and lint output.

## 8. Repository Signal Analysis

- [x] 8.1 Implement repository path confirmation flow before any repository scanning.
- [x] 8.2 Implement shallow Git metadata extraction for commit timing, commit messages, and active periods.
- [x] 8.3 Implement directory, language, file type, docs, tests, CI, scripts, config, and Agent workflow file detection.
- [x] 8.4 Implement repository evidence pack output with sensitivity notes, skipped paths, source references, and limitations.
- [x] 8.5 Add safety handling for large or high-risk repositories that restricts analysis to metadata and top-level summaries.
- [x] 8.6 Add tests for confirmed paths, unconfirmed paths, large repository degradation, and Agent workflow file detection.

## 9. Reports And Run Outputs

- [x] 9.1 Implement per-run output structure under runs/<timestamp>/ for source inventory, privacy audit, evidence, growth cycle, wiki update proposals, reports, and errors.
- [x] 9.2 Implement report.md with the GrowthTask package first, followed by rationale, maturity estimates, diagnoses, ActionAssets, LLM Wiki update suggestions, Wiki Lint summary, privacy audit, and appendices.
- [x] 9.3 Implement report.json with machine-readable references to EvidenceItem, EvidenceSignal, Diagnosis, GrowthTask, ActionAsset, WikiUpdateProposal, and WikiLintIssue IDs.
- [x] 9.4 Add tests that report output prioritizes GrowthTask before scoring or profile appendices.

## 10. End-To-End Verification

- [x] 10.1 Create sanitized end-to-end fixtures covering at least one complex AI collaboration case.
- [x] 10.2 Run the full fixture pipeline from source inventory to ConversationSession, EvidenceItem, EvidenceSignal, GrowthCycle, ActionAsset, WikiUpdateProposal, Wiki Lint, and report output.
- [x] 10.3 Verify generated tasks include steps, done definitions, review questions, expected artifacts, and evidence references.
- [x] 10.4 Verify privacy audit confirms no raw conversation text, raw code, secrets, or unsafe identifiers appear in outbound payload previews or public Wiki outputs.
- [x] 10.5 Verify OpenSpec requirements map to automated or documented tests for each capability.
