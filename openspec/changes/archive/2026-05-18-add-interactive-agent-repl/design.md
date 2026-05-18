## Context

Personal Growth Agent currently exposes an installable `pga` CLI with subcommands for initialization, scanning, analysis runs, reports, Wiki paths, knowledge ingest, dashboard generation, and task completion. This is functional but command-heavy: users must remember which command to run, switch between report paths, dashboard pages, and task files, and cannot ask follow-up questions in the same workspace.

The target experience is closer to opencode: running `pga` opens a terminal interaction loop. Users can ask free-form questions, use `/` commands for deterministic local actions, stream LLM answers, and preserve the interaction as local conversation history. Existing subcommands remain valid for automation and compatibility.

## Goals / Non-Goals

**Goals:**
- Launch an interactive terminal REPL when `pga` is run without a subcommand.
- Keep existing `pga <subcommand>` behavior intact.
- Support `/` shortcut commands for common local workflows.
- Support free-form chat through the configured default LLM provider/model.
- Stream chat responses to the terminal.
- Allow chat to call a fixed whitelist of local tools for report, task, Wiki, gap, analysis-run, and dashboard workflows.
- Store conversation logs under the resolved workspace, outside `llm-wiki/`.
- Keep conversation logs out of Wiki pages, raw Wiki sources, and Wiki manifests.

**Non-Goals:**
- Building a full multi-pane TUI in the first implementation.
- Introducing arbitrary shell execution as an LLM tool.
- Automatically converting chat history into Wiki knowledge.
- Replacing the static dashboard.
- Changing the existing growth analysis business logic.

## Decisions

### Use a lightweight REPL for the MVP

The first implementation should use a lightweight REPL rather than a full TUI framework. `prompt_toolkit` is a good fit for input editing, command history, and future autocomplete. `rich` is a good fit for readable tables, markdown-like output, status lines, and streaming display.

Alternative considered: Textual. Textual is the right option for a later multi-pane app with session lists, context panels, task detail views, and focus management. It is heavier than needed for the MVP because the immediate risk is interaction semantics, not layout.

### Keep `/` commands deterministic and separate from chat

Inputs beginning with `/` should be dispatched by the local REPL command router. They should not go through the LLM. This preserves predictable actions for workflows such as `/tasks`, `/task complete <id>`, `/run`, and `/dashboard`.

Free-form inputs should enter the LLM chat loop. This keeps the user model simple: commands are explicit actions; normal language is conversation.

### Model local tools as a whitelist

The chat loop should expose only named local tools:
- `get_latest_report`
- `list_growth_tasks`
- `complete_growth_task`
- `list_wiki_pages`
- `read_wiki_page`
- `list_knowledge_gaps`
- `run_growth_cycle`
- `build_open_dashboard`

The tool layer should call existing project functions where possible and return compact, sanitized results. It must not expose arbitrary file reads, arbitrary writes, or shell commands. Write/action tools should be represented explicitly in logs.

### Add chat-specific provider support without weakening analyzer contracts

The current analyzer flow expects scenario-specific JSON responses and validation. Free-form chat needs a separate request path that supports normal assistant messages, streaming, and tool calls. It should still reuse provider routing and credential resolution.

Provider helpers should separate:
- analyzer requests, which keep strict JSON contracts and validation;
- interactive chat requests, which stream assistant text and process tool calls.

### Store conversation history as local JSONL

Each REPL session should write JSONL records under:

```text
<workspace>/conversations/YYYY-MM-DD/<session-id>.jsonl
```

Records should include user inputs, assistant final text, provider/model metadata, tool call summaries, tool result summaries, timestamps, and errors. Logs should be readable and durable, but they should not be registered as Wiki raw sources or Wiki manifest entries.

### Context assembly should be compact and safe

The chat loop should assemble compact context from latest report summaries, active tasks, Wiki page indexes, and knowledge gaps. It should avoid sending raw conversation transcripts, raw code, secrets, or local-only content to external providers. When a user asks about a specific Wiki page, `read_wiki_page` can provide that page content after applying the same local-only and sensitivity boundaries used by dashboard-safe exports.

## Risks / Trade-offs

- External chat is now default when credentials exist -> mitigate by applying existing credential resolution, redaction boundaries, outbound audit summaries, and clear missing-credential messages.
- Streaming behavior differs across providers -> mitigate by implementing a provider abstraction that can fall back to non-streaming output while preserving the same REPL interface.
- Tool calls can mutate local state -> mitigate by keeping the whitelist small, logging every tool call, and routing mutations through existing functions such as task completion and growth cycle execution.
- `/run` and `run_growth_cycle` may take time -> mitigate with status output and clear completion/error records in the conversation log.
- Lightweight REPL may feel less like a full app -> accept for MVP; preserve a path to Textual after core semantics are validated.
- Conversation logs may contain sensitive content -> store locally outside Wiki, do not include them in dashboard-safe exports by default, and avoid adding them to source manifests.

## Migration Plan

1. Add the interactive REPL behind the no-subcommand `pga` entrypoint.
2. Keep existing subcommands unchanged for automation and backward compatibility.
3. Add local conversation storage under the resolved workspace on first interactive use.
4. Add prompt/provider chat support without changing analyzer request validation.
5. Add tests for command dispatch, tool whitelist behavior, storage location, and no-Wiki persistence.
6. Rollback is straightforward: restore no-subcommand `pga` to printing help while leaving existing subcommands unaffected.

## Open Questions

- Should write/action tools such as `complete_growth_task` and `run_growth_cycle` require an inline confirmation inside the REPL, or is the conversation log sufficient for MVP?
- Should `/summary` be purely local report summarization, or should it call the LLM when credentials are configured?
- Should conversation history have a retention limit or pruning command in the first implementation?
