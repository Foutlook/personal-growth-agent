## ADDED Requirements

### Requirement: Discover local AI conversation sources
The system SHALL discover supported local AI conversation sources for Codex, Claude Code, and opencode without requiring users to manually locate default record directories.

#### Scenario: Supported source is found
- **WHEN** a supported tool has readable local conversation records in a known or configured path
- **THEN** the system records the source name, path, readable status, file count, time range, and parse readiness in the source inventory

#### Scenario: Supported source is missing
- **WHEN** a supported tool has no readable local conversation records
- **THEN** the system marks that source as missing and continues processing other available sources

### Requirement: Inspect sources before parsing content
The system MUST create a source inventory before detailed parsing and MUST avoid exposing raw message content in that inventory.

#### Scenario: Inventory is generated
- **WHEN** source discovery completes
- **THEN** the system outputs source metadata including source type, path, time range, file count, size summary, parseability, and sensitivity hints

### Requirement: Parse records into ConversationSession
The system SHALL parse supported source records into a unified ConversationSession model.

#### Scenario: Conversation record is parsed
- **WHEN** a supported record file is readable and valid
- **THEN** the system produces a ConversationSession with source, timestamps, messages summary, tool call summary, referenced files, project paths, task type, and outcome

#### Scenario: Record format is unsupported
- **WHEN** a record file cannot be parsed because the format is unsupported or corrupt
- **THEN** the system records a parse failure with the source path and reason and continues parsing other records

### Requirement: Preserve local source references
The system MUST retain local references from parsed ConversationSession records back to their source files or source map entries.

#### Scenario: Session has source trace
- **WHEN** a ConversationSession is created
- **THEN** it includes a local source reference that can be used for audit and evidence traceability without exposing raw content externally
