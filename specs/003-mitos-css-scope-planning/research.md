# Research: MITOS/CSS Domain Scoping for Dagster + dbt

## Decision 1: Use domain-first directories under existing roots
- **Decision**: Keep top-level `cockpit/` and `dbt/` unchanged; add `mitos/`, `css/`, and `shared/` subtrees under each relevant area.
- **Rationale**: Minimal disruption to imports/tooling while giving explicit ownership boundaries.
- **Alternatives considered**:
  - Separate repositories per domain (rejected: operational overhead and duplicate platform code).
  - Flat naming conventions only (rejected: weak enforcement, harder review boundaries).

## Decision 2: Dagster grouping via deterministic domain metadata
- **Decision**: Assign each domain asset to Dagster group `mitos` or `css`; keep shared assets in `shared` group.
- **Rationale**: Matches user request for group-based organization and enables domain-filtered UI and jobs.
- **Alternatives considered**:
  - Keep layer-based groups only (`raw`, `staging`, `final`) (rejected: does not isolate MITOS/CSS scope).
  - Multi-dimensional naming in asset key only (rejected: harder operations and selection ergonomics).

## Decision 3: dbt path + tag selectors for domain build isolation
- **Decision**: Organize models by path (`models/mitos/**`, `models/css/**`) and tag models with `domain:mitos` / `domain:css`; add selectors for stable commands.
- **Rationale**: Works with dbt selection semantics and keeps CI/jobs readable.
- **Alternatives considered**:
  - Tags only with mixed folders (rejected: path drift risk).
  - Separate dbt projects (rejected: unnecessary complexity for shared macros/dependencies).

## Decision 4: Preserve warehouse dialect parity through shared macros
- **Decision**: Any domain-specific SQL that diverges by warehouse is implemented through adapter-aware macros in shared macro paths.
- **Rationale**: Satisfies constitution and repo rules around Postgres local compatibility plus Snowflake prod execution.
- **Alternatives considered**:
  - Snowflake-only SQL inline in domain models (rejected: breaks local/test builds).

## Decision 5: MITOS-default transitional compatibility
- **Decision**: Keep MITOS as default schema/tag fallback until jobs and env vars are fully domain-parameterized.
- **Rationale**: Avoids breaking existing runs while enabling incremental CSS rollout.
- **Alternatives considered**:
  - Hard switch to mandatory domain variables immediately (rejected: high migration risk).
