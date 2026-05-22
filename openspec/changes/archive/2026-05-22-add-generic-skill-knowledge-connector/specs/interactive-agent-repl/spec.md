## ADDED Requirements

### Requirement: Expose approved external knowledge tools
The interactive chat loop SHALL expose approved read-only external skill knowledge tools to the LLM when connectors are configured.

#### Scenario: LLM searches external knowledge
- **WHEN** the LLM requests an approved external knowledge search tool with a query and optional connector or collection scope
- **THEN** the system executes the read-only connector operation and returns compact, redacted search results to the chat loop

#### Scenario: LLM lists external collections
- **WHEN** the LLM requests an approved external collection listing tool
- **THEN** the system returns available connector collections with safe names, descriptions, and counts when available

### Requirement: Reject arbitrary skill execution in interactive chat
The interactive chat loop MUST NOT expose arbitrary installed skill execution to the LLM.

#### Scenario: LLM requests a non-whitelisted skill operation
- **WHEN** the LLM requests direct shell execution, direct skill script execution, or a connector operation outside list, search, read, and fetch
- **THEN** the system rejects the tool call and records the rejection in the conversation log

### Requirement: Import external summaries only through explicit action
The interactive agent SHALL import external skill summaries into the local Wiki only after the user explicitly requests or confirms the import.

#### Scenario: Search finds relevant external items
- **WHEN** external search results are available but the user has not requested import
- **THEN** the system displays or uses the results for the current answer without creating local Wiki pages

#### Scenario: User requests summary import
- **WHEN** the user asks the agent to save or import selected external items
- **THEN** the system writes summary-only local Wiki notes through the knowledge ingestion flow and records tool activity in the conversation log

### Requirement: Fetch full content only for specific questions
The interactive agent MUST avoid fetching third-party full content unless the current user request requires original details.

#### Scenario: Summary answer is sufficient
- **WHEN** local summaries or connector previews answer the user's question
- **THEN** the interactive agent answers without calling the connector fetch operation

#### Scenario: User asks for details requiring original content
- **WHEN** the user asks for details not present in local summaries or connector previews
- **THEN** the interactive agent may call the connector fetch operation for the relevant item and summarize the fetched content safely
