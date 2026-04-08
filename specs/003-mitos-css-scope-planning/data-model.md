# Data Model: MITOS/CSS Domain Scoping

## Entity: Domain
- **Fields**:
  - `domain_id` (`mitos` | `css`)
  - `display_name` (string)
  - `default_schema_raw` (string)
  - `default_schema_transform` (string)
  - `enabled` (boolean)
- **Validation**:
  - `domain_id` must be unique and lowercase.
  - Domain-specific schema defaults must be non-empty.

## Entity: DagsterDomainAssetBinding
- **Fields**:
  - `asset_key` (Dagster asset key)
  - `domain_id` (FK -> Domain)
  - `group_name` (`mitos` | `css` | `shared`)
  - `job_membership` (list of job names)
- **Validation**:
  - Every non-shared asset must map to exactly one domain.
  - `group_name` must align with `domain_id` for domain assets.

## Entity: DbtDomainNodeBinding
- **Fields**:
  - `node_name` (dbt model/test identifier)
  - `path_domain` (`mitos` | `css` | `shared`)
  - `tags` (includes one domain tag unless shared)
  - `target_support` (`local`, `prod`, or both)
- **Validation**:
  - Domain nodes must be under matching domain directory.
  - Domain nodes must include a domain tag for selector stability.
  - Nodes runnable on local must avoid inline Snowflake-only syntax.

## Relationships
- `Domain` 1..N `DagsterDomainAssetBinding`
- `Domain` 1..N `DbtDomainNodeBinding`
- `shared` nodes/assets may be referenced by both domains.

## State Transitions
- **Bootstrap**: `css` domain exists with empty folders and baseline config.
- **Active**: domain has at least one asset and one dbt model with passing domain-targeted checks.
- **Mature**: domain has dedicated jobs/schedules and no transitional fallbacks.
