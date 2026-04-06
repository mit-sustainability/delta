# Contract: Domain Structure and Selection

## Purpose
Define required repository structure and selection interfaces for supporting MITOS and CSS scopes in Dagster and dbt.

## Contract Clauses

### C1. Domain Identifiers
- Supported domain identifiers are exactly `mitos` and `css`.
- Identifiers are lowercase and used consistently in paths, tags, and group names.

### C2. Dagster Interface
- Every domain asset MUST be assigned to Dagster group matching its domain.
- Domain-focused jobs MUST support selecting MITOS or CSS independently.
- Shared assets MUST use `shared` group and be explicitly included/excluded by job intent.

### C3. dbt Interface
- Domain models MUST live under `dbt/models/<domain>/...`.
- Domain models MUST include a stable domain tag (`domain:mitos` or `domain:css`) or equivalent selector contract.
- Project config MUST allow domain-targeted builds without editing SQL files.

### C4. Warehouse Compatibility
- Domain changes MUST preserve local/test Postgres and production Snowflake compatibility.
- Snowflake-only expressions in locally supported models MUST be behind adapter-aware macros.

### C5. Migration Compatibility
- MITOS may remain temporary default where existing runs require backward compatibility.
- Default behavior sunset conditions must be documented when CSS rollout is complete.
