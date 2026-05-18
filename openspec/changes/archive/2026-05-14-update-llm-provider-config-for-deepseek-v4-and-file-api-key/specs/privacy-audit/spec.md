## ADDED Requirements

### Requirement: Audit credential resolution without exposing secrets
The system MUST audit remote provider credential resolution without storing plaintext credentials.

#### Scenario: File credential is used
- **WHEN** a remote provider uses a credential from `api_key`
- **THEN** the privacy audit records credential source `file` and omits the credential value

#### Scenario: Environment credential is used
- **WHEN** a remote provider uses a credential from `api_key_env`
- **THEN** the privacy audit records credential source `env` and omits the environment variable value

#### Scenario: Credential is missing
- **WHEN** a remote provider call is skipped because no credential can be resolved
- **THEN** the privacy audit records credential source `missing`, provider, model, scenario, and skip reason without storing any secret material
