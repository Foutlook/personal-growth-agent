## Why

Current usage requires users to remember and chain multiple CLI commands for reports, Wiki, growth tasks, dashboard review, and analysis runs. The tool should feel closer to opencode: after installation, running `pga` opens a conversational terminal workspace where users can ask questions, run common actions, and keep a durable local conversation history.

## What Changes

- Add an interactive terminal REPL launched by `pga` when no subcommand is provided.
- Support `/` local shortcut commands for deterministic actions such as listing tasks, completing tasks, viewing Wiki indexes, summarizing the latest report, running analysis, and opening the dashboard.
- Support free-form LLM chat with streaming output.
- Allow the LLM chat loop to call a fixed whitelist of local tools for reading reports, tasks, Wiki indexes, knowledge gaps, and for controlled write/actions such as completing a growth task, running the growth cycle, and opening the dashboard.
- Store interactive conversation records under the resolved workspace outside `llm-wiki/`.
- Ensure conversation records are retained locally and are not added to Wiki pages, raw Wiki sources, or Wiki manifests.
- Preserve existing CLI subcommands and workspace/config resolution behavior.

## Capabilities

### New Capabilities
- `interactive-agent-repl`: Covers the terminal REPL, `/` commands, streaming chat, local tool calling, and local conversation retention.

### Modified Capabilities
- `cli-workspace-management`: Running `pga` without a subcommand should enter the interactive REPL while existing subcommands remain compatible.
- `llm-provider-and-prompt-registry`: The configured LLM provider/model should support interactive chat requests with streaming output and tool-call metadata.
- `privacy-audit`: Interactive chat payloads, tool calls, and retained conversation logs need privacy boundaries that keep records local and outside the LLM Wiki.

## Impact

- Affected code: `personal_growth_agent/cli.py`, new interactive REPL module, provider request/streaming helpers, local tool adapter functions, and tests.
- Affected storage: new `<workspace>/conversations/YYYY-MM-DD/<session-id>.jsonl` files.
- Affected dependencies: likely add `prompt_toolkit` for REPL input/history and `rich` for readable terminal rendering. A full TUI framework such as Textual is out of scope for this MVP.
- Compatibility: existing `pga <subcommand>` behavior remains available; only no-subcommand `pga` changes from help output to interactive mode.
