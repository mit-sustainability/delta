# Implementation Plan: MITOS/CSS Domain Scoping for Dagster + dbt

**Branch**: `003-mitos-css-scope-planning` | **Date**: 2026-04-04 | **Spec**: `/specs/003-mitos-css-scope-planning/spec.md`
**Input**: Feature specification from `/specs/003-mitos-css-scope-planning/spec.md`

## Summary

Introduce a domain-first repository structure so both Dagster orchestration code (`cockpit`) and dbt project artifacts can support two scopes—MITOS and CSS—without cross-domain coupling. The plan keeps warehouse parity (Postgres local/test + Snowflake prod), adds explicit domain grouping/selection patterns, and defines a migration path from current MITOS-default layout.

## Technical Context

**Language/Version**: Python 3.13 + SQL (dbt)  
**Primary Dependencies**: Dagster, dagster-dbt, dbt-core, dbt-postgres, dbt-snowflake  
**Storage**: PostgreSQL (local/test) and Snowflake (prod target)  
**Testing**: pytest for orchestration + `dbt build`/`dbt ls` validation per target/domain  
**Target Platform**: Containerized Linux execution for orchestration and dbt jobs  
**Project Type**: Batch data platform (Dagster + dbt monorepo)  
**Performance Goals**: Domain-targeted runs must avoid unnecessary cross-domain execution  
**Constraints**: Idempotent reruns, adapter parity, no Snowflake-only SQL left unabstracted for local-supported models  
**Scale/Scope**: Two active domains (`mitos`, `css`) across orchestration assets and dbt folders

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code-Derived Truth**: PASS — Plan is derived from current repo layout (`cockpit/` + `dbt/`) and introduces additive domain segmentation.
- **II. Dagster and dbt Contract First**: PASS — Plan specifies impacted Dagster assets/groups and dbt model selection/paths with both warehouse paths.
- **III. Idempotent Batch Operations**: PASS — No non-idempotent write semantics introduced; rerun safety retained.
- **IV. External Dependency Explicitness**: PASS — No new external systems; existing Dagster/dbt/Postgres/Snowflake contracts remain explicit.
- **V. Minimal and Testable Change Surface**: PASS — Scope limited to structure, grouping metadata, selection configuration, and docs/tests.
- **VI. Migration Clarity Over Legacy Drift**: PASS — MITOS-default compatibility path explicitly documented as transitional.

## Project Structure

### Documentation (this feature)

```text
specs/003-mitos-css-scope-planning/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── domain-structure-contract.md
└── tasks.md              # created later by /tasks
```

### Source Code (repository root)

```text
cockpit/
├── assets/
│   ├── shared/
│   ├── mitos/
│   ├── css/
│   └── dbt.py                  # domain-aware dbt asset factories/translators
├── jobs/
│   ├── mitos.py
│   └── css.py
└── definitions.py              # registers domain asset groups/jobs/resources

dbt/
├── models/
│   ├── shared/
│   ├── mitos/
│   │   ├── raw/
│   │   ├── staging/
│   │   └── final/
│   └── css/
│       ├── raw/
│       ├── staging/
│       └── final/
├── selectors.yml               # domain selectors (if adopted)
└── dbt_project.yml             # domain tags/groups/schemas/defaults
```

**Structure Decision**: Keep existing monorepo and package roots; introduce domain segmentation under both orchestration and dbt directories with a small shared layer for reusable code.

## Phase 0: Research

Research outcomes are captured in `/specs/003-mitos-css-scope-planning/research.md` and resolve implementation choices for domain directory strategy, Dagster grouping, dbt selectors, and migration handling.

## Phase 1: Design & Contracts

Design artifacts are captured in:
- `/specs/003-mitos-css-scope-planning/data-model.md`
- `/specs/003-mitos-css-scope-planning/contracts/domain-structure-contract.md`
- `/specs/003-mitos-css-scope-planning/quickstart.md`

## Post-Design Constitution Check

- **I–VI**: PASS — Design keeps dual-warehouse support, explicit contracts, narrow change surface, and clear transition behavior.

## Complexity Tracking

No constitution violations identified.
