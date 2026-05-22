## Why

The agent can currently use local Wiki pages and a fixed local tool whitelist, but third-party knowledge exposed through installed skills such as IMA remains outside the product's own memory and tool model. Users need a controlled way to discover and summarize external skill-backed knowledge locally while fetching full third-party content only when a concrete question requires it.

## What Changes

- Add a generic read-only external skill knowledge connector abstraction with four operations: list collections, search items, read summary/metadata, and fetch full content on demand.
- Add IMA as the first connector implementation while keeping the public contract generic enough for future knowledge-oriented skills.
- Store only long-lived, user-readable summary notes in the local LLM Wiki, with each summary capped at six bullet points and linked back to its third-party source.
- Keep full third-party content out of the local Wiki by default; fetch full content only when the user asks a question that requires the original source.
- Allow the interactive agent to search and inspect external skill-backed knowledge through explicit, read-only tools, and to import selected summaries into the local Wiki.
- Preserve the existing rule that external knowledge is learning context, not evidence of the user's current maturity or capability.

## Capabilities

### New Capabilities

- `external-skill-knowledge-connector`: Generic read-only connector contract for skill-backed third-party knowledge sources, including list, search, read, and fetch semantics.

### Modified Capabilities

- `external-knowledge-ingestion`: Support summary-only ingestion from external skill knowledge items, storing user-readable notes rather than full third-party content.
- `interactive-agent-repl`: Expose controlled read-only external knowledge tools to the interactive agent without opening arbitrary shell or arbitrary skill execution.
- `llm-wiki-maintenance`: Define local Wiki representation and provenance rules for external skill summary notes.
- `growth-memory-wiki-integration`: Ensure external skill summaries remain learning context and cannot directly raise or lower maturity estimates.
- `privacy-audit`: Audit third-party skill connector metadata, credential handling, and on-demand full-content fetches.

## Impact

- Affected modules likely include `personal_growth_agent/interactive.py`, `interactive_tools.py`, `knowledge.py`, `models.py`, `wiki.py`, dashboard export code, and new connector modules.
- Affected workspace layout includes new or extended `llm-wiki/wiki/knowledge/` summary pages and `llm-wiki/data/` provenance/index metadata.
- Affected user experience includes new interactive tools for listing/searching external knowledge and selectively importing summaries.
- Security impact includes strict read-only connector policy, credential redaction, source provenance, and no arbitrary skill execution.
