## ADDED Requirements

### Requirement: Compile raw sources with an explicit prompt
The system SHALL support compiling selected raw sources into Wiki pages using an explicit prompt path.

#### Scenario: User compiles a raw directory
- **WHEN** the user requests Wiki compilation with `--raw <path>` and `--prompt <path>`
- **THEN** the system reads supported raw source files from the raw path, loads the prompt file, generates compiled Wiki content, writes it directly to `wiki/`, and records write provenance

#### Scenario: User compiles a single raw file
- **WHEN** the user requests Wiki compilation for a raw file path
- **THEN** the system compiles that file with the selected prompt and records the source path in the write log

### Requirement: Preserve prompt provenance during compilation
The system SHALL record prompt identity for raw-to-Wiki compilation.

#### Scenario: Prompt file is used
- **WHEN** a prompt file is used to compile raw sources into Wiki pages
- **THEN** the write log records the prompt path, prompt ID when available, prompt version when available, and prompt digest

### Requirement: Support local and remote compilers
The system SHALL support local-rule compilation and approved remote LLM compilation for raw-to-Wiki workflows.

#### Scenario: Remote compiler is unavailable
- **WHEN** remote LLM compilation is not approved, not configured, or fails validation
- **THEN** the system either uses the configured local compiler fallback or records a skipped compile result without writing unsupported content

#### Scenario: Remote compiler is approved
- **WHEN** a remote LLM compiler is configured and outbound use is explicitly approved
- **THEN** the system prepares a privacy-checked payload, records outbound prompt/provider metadata, validates the response, and writes only validated compiled Wiki content
