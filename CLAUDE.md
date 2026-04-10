# CLAUDE.md

## Working Rules

Decompose problems from first principles. Prefer concise, clean solutions over broad rewrites. Changes MUST be atomic: do not mix functional logic, linting, or unrelated refactors in a single task.

## Required Context

Before making non-trivial or cross-cutting changes, read:

- `.specify/memory/constitution.md` — authoritative repo principles; if code violates the constitution, fix the code, not the constitution
- `specs/BACKLOG.md` if it exists — active work queue

## Backlog-First Workflow

- `specs/BACKLOG.md` is the default work queue. Most routine data-platform work does not need a feature spec folder.
- Each backlog item should be a small, independently ownable unit: an ingestion flow, asset, model chain, resource, utility, deployment change, migration step, or docs update.
- Keep backlog status current when work is added, started, blocked, or completed.
- Create a feature spec folder under `specs/` only when the work is cross-domain, changes runtime contracts, adds a new external integration, materially changes schedules or deployment, or is ambiguous enough that written design will prevent churn.

## Repository Constraints

**Warehouse Dialect Parity**: Code MUST be valid in both PostgreSQL (local/test) and Snowflake (production). Use dbt macros to abstract Snowflake-specific syntax. Do not leave Snowflake-only syntax inline in any model body expected to run on `DBT_TARGET=local`.

**Orchestration Layout**: `cockpit/` is organized by scope. New code lands under `cockpit/shared/`, `cockpit/core/`, `cockpit/mitos/`, or `cockpit/css/`. Each scope owns its own `defs.py`, `assets/`, `jobs/`, `tests/`, and optional `utils.py`.

**Resource and IO Manager Separation**: Connection resources are separate from IO managers.
- dbt execution: `cockpit/shared/resources/dbt.py`
- Warehouse connections: `cockpit/shared/resources/postgres.py` and `cockpit/shared/resources/snowflake.py`
- Dagster persistence: `cockpit/shared/resources/io_managers.py`

**dbt Orchestration**: Models live under `dbt/models/<scope>/<layer>/`. Dagster dbt asset wrappers live under the owning scope package (e.g. `cockpit/mitos/assets/`). Dagster orchestrates dbt via `DbtCliResource`; dbt remains the source of truth for model schemas and materializations.

**Dependency Integrity**: Any new Python library or dbt package must be added to the relevant environment config (`pyproject.toml`, `packages.yml`). No ghost imports.

**Idempotency**: All ingestion and transformation logic MUST be idempotent. Retrying a partially failed job must not produce duplicate records or state corruption.

**Minimal Surface**: Broad refactors are forbidden unless separated into a dedicated task with explicit reasoning.

**Migration Clarity**: This repository replaces Basin. Prefer the target architecture over reproducing Basin internals. Any intentional Basin compatibility must be explicit: what is preserved, for how long, and what exit condition removes it.

## Code Style

**Prefer classes when** the code represents one cohesive workflow with shared configuration, shared dependencies, repeated internal state, or multiple related execution steps. Good examples: extractors, parsers, API clients, transformation workflows, report builders, loaders.

**Class constraints**: one responsibility per class, explicit constructor dependencies, small public API, internal methods directly support the main flow.

**Helper extraction test** — before creating a helper function or private method, ask:
1. Is it reused across separate call sites?
2. Does it hide noise rather than hide important logic?
3. Would inlining make the file easier to read?
4. Is the function name genuinely clearer than its body?

If mostly no, inline it.

**Avoid**: many single-use helper functions, deep call chains for simple workflows, private helpers that merely rename a few lines, utility dumping grounds, fragmenting one logical operation across scattered free functions.

**Dagster-specific**: Keep asset definitions explicit and easy to trace. Make input/output boundaries obvious at the asset or workflow entrypoint. Centralize side effects. Avoid hiding asset behavior behind thin wrappers. Prefer implementation shapes that make idempotency, writes, and failure surfaces easy to inspect.

## Execution Patterns

**Routine work**: Update backlog → Implement → Verify (automated).

**Complex or cross-domain work**: Use Claude's plan mode to think through the approach before touching code. If the work touches schedules, deployment, or external integrations, check whether baseline docs need updates.

**Migration work**: Do not normalize undocumented legacy Basin behavior. If a Basin logic path is preserved, it must have an explicit TODO for eventual removal.

**Verification**: Manual verification is insufficient. Every implementation MUST include automated tests or a state-diff report (e.g., dbt-audit-helper results) to prove parity or correctness.

## Subagents

When parallelizing work, use one subagent per backlog item or one concrete task. Do not assign an entire feature to a single subagent. Subagents should read `CLAUDE.md` and `.specify/memory/constitution.md` before starting.

Three working modes:

- **Implementer** — add, modify, or connect Dagster assets, jobs, resources, IO managers, schedules, sensors, or dbt-facing pipeline boundaries. Follow code style rules above. Deliverable: narrow production-ready patch with implementation changes, relevant tests, and baseline doc updates when contracts changed.

- **Test coverage** — add or improve tests for defined behavior. Do not invent new product behavior. Derive tests from stated requirements and current code contracts. Report coverage gaps caused by missing requirements rather than filling them speculatively.

- **Docs auditor** — read-only analysis of documentation and planning artifacts against current repository behavior. Treat code paths as the source of truth when docs disagree. Check that docs do not blur PostgreSQL local/test behavior with Snowflake production behavior. Produce an audit report with file references and suggested follow-ups.

## Active Technologies

- Python 3.13 + SQL (dbt) + Dagster, dagster-dbt, dbt-core, dbt-postgres, dbt-snowflake
- PostgreSQL (local/test warehouse) and Snowflake (production target)
- Pre-commit for type checking, linting, and format fixes
