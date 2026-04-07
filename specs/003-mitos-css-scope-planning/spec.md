# Feature Specification: MITOS/CSS Domain Scoping for Dagster + dbt

**Feature Branch**: `003-mitos-css-scope-planning`
**Created**: 2026-04-04
**Status**: Draft
**Input**: User description: "/plan I’m thinking to use this code base to support two different scopes: MITOS (our office) and CSS (campus service and stewardship) for both Dagster (using group) and dbt. Help me structure the copilot and dbt folders to do this."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Domain-Isolated Development Layout (Priority: P1)

As a platform developer, I need a consistent repository layout for MITOS and CSS so I can add or modify assets/models without mixing domain ownership.

**Why this priority**: Domain isolation is prerequisite to any safe implementation in Dagster and dbt.

**Independent Test**: A new MITOS-only and CSS-only model/asset can be added without touching the opposite domain folder.

**Acceptance Scenarios**:

1. **Given** both MITOS and CSS are supported, **When** I inspect the folder tree, **Then** Dagster and dbt paths are split by domain with clear naming.
2. **Given** a developer contributes a change, **When** code review runs, **Then** reviewers can identify which domain is affected from path and group names alone.

---

### User Story 2 - Dagster Group Boundaries by Domain (Priority: P1)

As an operator, I need Dagster assets grouped by MITOS/CSS so I can run, observe, and permission jobs per domain.

**Why this priority**: Dagster grouping is directly requested and affects operator workflows.

**Independent Test**: Dagster definitions expose explicit domain groups and jobs can target one domain without selecting the other.

**Acceptance Scenarios**:

1. **Given** Dagster loads definitions, **When** I inspect asset groups, **Then** each asset is in either MITOS or CSS group.
2. **Given** domain-specific jobs exist, **When** I execute MITOS job, **Then** CSS assets are not selected.

---

### User Story 3 - dbt Domain Boundaries and Selectors (Priority: P2)

As an analytics engineer, I need dbt models organized by MITOS/CSS and selectable per domain so builds can run independently.

**Why this priority**: dbt structure is needed for scalable model ownership and selective builds.

**Independent Test**: `dbt build --select` can run MITOS-only and CSS-only model paths/tags independently on local and prod targets.

**Acceptance Scenarios**:

1. **Given** dbt project config defines domain nodes, **When** I run a MITOS selector, **Then** only MITOS models build.
2. **Given** both local Postgres and Snowflake targets, **When** I build each domain, **Then** both targets execute valid SQL through shared adapter-aware macros.

### Edge Cases

- What happens when a shared model/macro is used by both MITOS and CSS domains?
- How does the system handle a domain that has no models/assets yet (empty folder bootstrap)?
- How should naming be enforced when a model appears to belong to both domains?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST define two first-class data domains: `mitos` and `css`.
- **FR-002**: Dagster orchestration code under `cockpit/` MUST be organized by scope and shared concerns so MITOS and CSS assets/jobs/tests are discoverable and maintainable by domain.
- **FR-003**: Dagster asset grouping metadata MUST expose domain-level groups (`mitos`, `css`) to the UI.
- **FR-004**: dbt model folders MUST be organized by domain while preserving existing layer conventions (raw/staging/final or equivalent).
- **FR-005**: dbt project configuration MUST support domain-specific selection (path/tag/selector strategy) for targeted builds.
- **FR-006**: Shared transformations or macros used by both domains MUST live in explicitly shared locations and avoid duplicate logic.
- **FR-007**: Planned structure MUST maintain dual-warehouse expectations: local/test Postgres and production Snowflake.
- **FR-008**: Migration guidance MUST document how existing MITOS-rooted defaults transition without breaking current runs.
- **FR-009**: Python-managed Dagster assets MUST use stable logical IO manager keys in asset definitions, while scope defs bind those keys to environment-specific Postgres or Snowflake IO managers.
- **FR-010**: Shared connection resources and Dagster IO managers MUST be defined separately so warehouse connectivity, dbt orchestration, and persistence behavior can evolve independently.

### Key Entities *(include if feature involves data)*

- **Domain**: Logical scope boundary (`mitos`, `css`) used for folder hierarchy, ownership, and run selection.
- **Dagster Asset Group**: Group metadata assigned to Dagster assets to reflect domain.
- **dbt Domain Node Set**: dbt models/tests grouped by domain path/tag/selector.
- **Shared Component**: Macro/model/utilities reused across domains.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Dagster assets in-scope for this feature can be mapped to either MITOS or CSS group.
- **SC-002**: A domain-targeted orchestration run selects only the intended domain assets.
- **SC-003**: `dbt build` succeeds for each domain independently on both local (`DBT_TARGET=local`) and prod (`DBT_TARGET=prod`) targets.
- **SC-004**: New contributor onboarding for domain placement can be completed by following one documented folder + naming guide without tribal knowledge.

## Assumptions

- Existing package name `cockpit` remains unchanged in this planning increment.
- Existing dbt layer semantics (raw/staging/final) remain and are nested under domain paths rather than replaced.
- MITOS stays current default domain for backward compatibility during transition.
- Domain-specific schedules/sensors may be added later and are not required in this planning-only deliverable.
- The repository now treats `core` as a first-class shared orchestration scope for Python-managed assets that are not owned exclusively by MITOS or CSS.
