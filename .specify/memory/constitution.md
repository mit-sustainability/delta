# Delta Constitution

## Core Principles

### I. Code-Derived Truth
Specifications for this repository MUST be derived from observable repository behavior before they are used to drive changes. When documentation, backlog items, or inherited Delta assumptions disagree with the current code paths, deployment workflow, or runtime contracts, the current repository behavior takes precedence until the divergence is resolved explicitly.

### II. Dagster and dbt Contract First
Every material behavior change MUST identify the affected Dagster assets, asset jobs, dbt models, schedules, sensors, and external resources. Changes are not complete until the spec states how data enters the platform, how it is persisted in PostgreSQL for local or test execution when applicable, how it is transformed by dbt, how it is materialized in Snowflake for production outcomes, and which execution path produces the result.

### III. Idempotent Batch Operations
This platform is a batch data system, not an interactive application. Specs and implementations MUST preserve safe reruns, explicit write semantics such as replace versus append, and predictable recovery from partial failures such as missing source files, failed upstream APIs, orchestration retries, PostgreSQL write failures in local or test contexts, and Snowflake write failures in production paths.

### IV. External Dependency Explicitness
All work MUST document the external systems it relies on: PostgreSQL for local or test warehouse behavior, Snowflake as the target warehouse and query engine, Dagster, dbt, cloud resources, source systems, network APIs, and any legacy Deltan interfaces still required during migration. Code changes MUST be valid in both PostgreSQL (Local/Test) and Snowflake (Prod) dialects, using dbt macros to abstract differences where they exist. Required environment variables, authentication assumptions, data contracts, and failure modes must be named directly in the spec rather than implied. Any new library import constitutes a change to "External Dependencies" and must be reflected in the environment config.

### V. Minimal and Testable Change Surface
Changes SHOULD stay within the smallest domain slice that solves the problem. Backlog items and, when needed, specs MUST identify the minimum affected files, expected tests, and operational checks. Broad refactors MUST be separated into a distinct PR/Task from functional changes, and document the reasoning in task plan.

### VI. Migration Clarity Over Legacy Drift
This repository exists to replace Basin and move warehouse outcomes to Snowflake. New work MUST prefer the target architecture over reproducing Basin internals by default. Any intentional compatibility with Basin, or any decision to keep behavior anchored to PostgreSQL beyond local or test control paths, must be explicit: what is being preserved, for how long, and what exit condition removes the compatibility path.

## Repository Constraints

- Primary stack: Python 3.14 orchestration plus dbt-managed warehouse transformations.
- Warehouse topology: PostgreSQL remains the local or testing warehouse path controlled by dbt; Snowflake is the target production warehouse and query engine.
- Data movement path: external source or API -> Dagster asset or ingestion step -> PostgreSQL landing or staging for local and test workflows when applicable -> dbt transformation layers -> Snowflake warehouse outputs for target-state production use.
- Runtime configuration is environment-variable driven; secrets are not committed to the repository.
- Warehouse behavior must respect the distinction between local or test PostgreSQL semantics and target-state Snowflake semantics, rather than assuming they are interchangeable.
- Migration work must distinguish between Delta parity work, temporary compatibility work, and target-state platform improvements.
- Type checking, linting, format fix should be handled by tools like pre-commit.

## Development Workflow

- This repository is backlog-first. `specs/BACKLOG.md` is the default work queue, and most routine data-platform work does not require a dedicated feature spec folder.
- Every backlog item must state a narrow outcome, expected scope, and affected domain so it can be owned independently.
- A dedicated feature spec is required for cross-domain, contract-changing, schedule-changing, deployment-changing, integration-heavy, migration-sensitive, or otherwise ambiguous work.
- Every spec for a behavioral change must name the operator-facing or downstream-facing outcome, affected domain, execution trigger, PostgreSQL impact if any, and Snowflake impact if any.
- Every plan must list the concrete repository paths it will touch across orchestration code, dbt project files, deployment or workflow configuration, and docs when relevant.
- Every implementation must preserve or improve verification for changed orchestration logic, data contracts, and dbt transformations. If no automated test exists yet, the plan must define the substitute verification and why it is sufficient.

## Governance

This constitution governs all Spec Kit artifacts in this repository. Amendments require updating this file and any impacted spec, plan, checklist, or workflow expectations in the same change. Reviewers should reject specs that omit execution boundaries, external dependencies, warehouse-path assumptions, migration assumptions, or verification strategy.

**Version**: 1.0.0 | **Ratified**: 2026-03-26 | **Last Amended**: 2026-03-26
