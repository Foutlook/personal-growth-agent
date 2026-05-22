## ADDED Requirements

### Requirement: Provide read-only external skill knowledge connectors
The system SHALL provide a generic connector contract for read-only, skill-backed third-party knowledge sources.

#### Scenario: Connector exposes allowed operations
- **WHEN** a connector is registered
- **THEN** it exposes only list, search, read, and fetch operations through the generic connector contract

#### Scenario: Connector attempts unsupported mutation
- **WHEN** a connector or LLM request attempts to upload, edit, delete, append, or otherwise mutate third-party content
- **THEN** the system rejects the operation as outside the approved connector contract

### Requirement: List external knowledge collections
The system SHALL allow approved connectors to list third-party knowledge collections without fetching full item bodies.

#### Scenario: User lists connector collections
- **WHEN** the user asks what collections are available from an approved external knowledge connector
- **THEN** the system returns collection names, safe descriptions, provider metadata, and item counts when available

### Requirement: Search external knowledge items
The system SHALL allow approved connectors to search third-party knowledge items by query and optional collection scope.

#### Scenario: User searches a connector
- **WHEN** the user searches external skill knowledge for a query
- **THEN** the system returns matching item titles, provider, collection, safe snippets or summaries when available, and opaque source locators without exposing credentials

### Requirement: Read external item summary metadata
The system SHALL allow approved connectors to read summary-level metadata for a third-party item without retrieving or persisting the full body by default.

#### Scenario: User previews an external item
- **WHEN** the user asks to inspect an external search result
- **THEN** the system returns the item title, provider, collection, available summary or preview, source locator, and last observed metadata

### Requirement: Fetch external item full content on demand
The system SHALL fetch full third-party item content only when a user question or explicit action requires the original content.

#### Scenario: Local summary is insufficient
- **WHEN** a user asks a detailed question that cannot be answered from local summaries or item metadata
- **THEN** the system may call connector fetch for the relevant item and use the fetched content transiently to answer the question

#### Scenario: Fetch is not needed
- **WHEN** local summaries or metadata are sufficient to answer the user
- **THEN** the system does not fetch full third-party content

### Requirement: Register IMA as an external knowledge connector
The system SHALL support IMA as the first implementation of the generic external skill knowledge connector contract.

#### Scenario: IMA connector is configured
- **WHEN** valid IMA credentials are available and the IMA connector is enabled
- **THEN** the system can list IMA knowledge bases, search items, read item metadata or summaries, and fetch full item content through the generic connector operations

#### Scenario: IMA credentials are missing
- **WHEN** the IMA connector is requested but credentials are unavailable
- **THEN** the system returns a configuration error that names the missing credential source without exposing any secret material
