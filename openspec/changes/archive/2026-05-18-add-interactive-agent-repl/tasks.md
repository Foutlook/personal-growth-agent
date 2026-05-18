## 1. REPL Entry And Command Routing

- [x] 1.1 Add interactive dependencies for REPL input and terminal rendering.
- [x] 1.2 Add an interactive module that starts a terminal REPL with resolved workspace, Wiki path, config, and session metadata.
- [x] 1.3 Change no-subcommand `pga` startup to launch the REPL while preserving `pga --help` and all existing subcommands.
- [x] 1.4 Implement `/help`, `/exit`, and `/quit` command handling.
- [x] 1.5 Add tests proving no-subcommand `pga` enters interactive mode through an injectable runner and existing subcommands still execute normally.

## 2. Local Slash Commands

- [x] 2.1 Implement `/tasks` using the current active growth task storage.
- [x] 2.2 Implement `/task complete <task-id>` by reusing the existing task archive behavior.
- [x] 2.3 Implement `/wiki` and `/gaps` using local Wiki/dashboard-safe indexes.
- [x] 2.4 Implement `/summary` from the latest report without writing new Wiki content.
- [x] 2.5 Implement `/run` and `/dashboard` by reusing existing growth cycle and dashboard workflows with terminal status output.
- [x] 2.6 Add tests for each slash command, including missing data and invalid task ID cases.

## 3. Conversation Storage And Privacy Boundaries

- [x] 3.1 Add a conversation JSONL writer under `<workspace>/conversations/YYYY-MM-DD/<session-id>.jsonl`.
- [x] 3.2 Record user messages, assistant final text, tool calls, tool results, errors, provider, model, and timestamps.
- [x] 3.3 Ensure conversation logs are not written under `llm-wiki` and are not added to Wiki source manifests.
- [x] 3.4 Add sanitization for logged tool arguments and compact result summaries.
- [x] 3.5 Add tests verifying log location, JSONL structure, UTF-8 without BOM, and no Wiki manifest side effects.

## 4. Interactive Chat Provider

- [x] 4.1 Add chat-specific provider request helpers that reuse provider route and credential resolution.
- [x] 4.2 Implement streaming chat output for providers that support streaming.
- [x] 4.3 Add a non-streaming fallback path that returns final assistant text through the same REPL interface.
- [x] 4.4 Return clear missing-credential messages without exposing credential values.
- [x] 4.5 Keep analyzer JSON-schema request validation unchanged.
- [x] 4.6 Add provider tests for credential resolution, streaming chunks, non-streaming fallback, and secret omission.

## 5. Whitelisted Local Tools

- [x] 5.1 Implement the tool registry with only `get_latest_report`, `list_growth_tasks`, `complete_growth_task`, `list_wiki_pages`, `read_wiki_page`, `list_knowledge_gaps`, `run_growth_cycle`, and `build_open_dashboard`.
- [x] 5.2 Implement read tools with compact, dashboard-safe outputs.
- [x] 5.3 Implement action tools by routing through existing task, growth cycle, and dashboard functions.
- [x] 5.4 Reject unapproved tool names and log the rejection.
- [x] 5.5 Add tests for approved read tools, approved action tools, unapproved tool rejection, and local-only content redaction.

## 6. Chat Loop Integration

- [x] 6.1 Connect free-form REPL input to the chat provider and stream output to the terminal renderer.
- [x] 6.2 Assemble compact safe context from latest report summaries, active tasks, Wiki page indexes, and knowledge gaps.
- [x] 6.3 Handle tool-call turns by dispatching local tools and continuing the chat loop with tool results.
- [x] 6.4 Record all chat turns and tool activity in the conversation log.
- [x] 6.5 Add integration tests for a multi-turn chat with one tool call and a streamed final answer.

## 7. Documentation And Verification

- [x] 7.1 Update README usage docs to describe `pga` interactive mode, `/` commands, chat behavior, and conversation log location.
- [x] 7.2 Document that conversation records are retained locally and are not saved to the LLM Wiki.
- [x] 7.3 Run the targeted test suite for CLI, provider, dashboard/Wiki data access, and interactive REPL behavior.
- [x] 7.4 Run OpenSpec validation for `add-interactive-agent-repl` before implementation is marked complete.
