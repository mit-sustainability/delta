# AGENTS.md

## Working Rule

Decompose problems from first principles. Prefer concise, clean solutions over broad rewrites. Changes MUST be atomic: do not mix functional logic, linting, or unrelated refactors in a single task.

## Required Context

Before making non-trivial or cross-cutting changes, read the repository baseline guidance:

- `.specify/memory/constitution.md`
- `specs/BACKLOG.md` if it exists
- any active feature folder under `specs/` if the work already has a dedicated spec

These files are the current source of truth for repository boundaries, orchestration, and migration expectations. Hierarchy of Truth: If code behavior violates the constitution.md, the Constitution takes precedence as the target state. Identify the violation and propose a code fix; do not update the Constitution to match a bug.

These files are the current source of truth for:

- repository boundaries
- orchestration and dbt runtime expectations
- PostgreSQL local or test warehouse behavior
- Snowflake target warehouse behavior
- external dependencies
- deployment and documentation expectations
- migration expectations for replacing Basin

If a repository-level baseline feature spec is created later, treat it as required context for cross-cutting work and keep this file in sync.

## Legacy Basin Reference

- `specs/legacy-basin-baseline/` contains reverse-engineered Basin documentation for reference only.
- Treat it as migration context, not as the source of truth for this repository.
- Do not read it by default for routine Delta work.
- Read it only when a backlog item, spec, or task explicitly calls for legacy reference, parity comparison, pipeline migration context, or contract comparison.
- If Delta behavior intentionally differs from Basin, prefer the Delta constitution, active specs, and current code paths, and document the deviation explicitly when it matters.

## Backlog-First Workflow

- Treat `specs/BACKLOG.md` as the active work queue.
- Each backlog item should be a small, independently ownable unit of work such as an ingestion flow, asset, model chain, resource, utility, deployment change, migration step, or docs update.
- Use one agent per backlog item when parallelizing work.
- Keep backlog status current when work is added, started, blocked, or completed.

## How To Use Specs

- Do not create a feature-specific spec folder by default.
- Create a feature-specific spec folder under `specs/` only when the work is cross-domain, changes runtime contracts, adds a new external integration, materially changes schedules or deployment, changes Basin migration assumptions, or is ambiguous enough that written design will prevent churn.
- Verification Anchoring: "Manual verification" is insufficient. Every implementation MUST include automated tests or a state-diff report (e.g., dbt-audit-helper results) to prove parity/correctness.
- If code and specs disagree but the code is functionally correct and intentionally improved, update the relevant spec to reflect the new "Code-Derived Truth."

## Spec Kit Usage

This repository uses Spec Kit artifacts plus repo-local Codex skills under `.agents/skills/`.

- When asked to `/specify`, use the `speckit-specify` skill.
- When asked to `/clarify`, use the `speckit-clarify` skill.
- When asked to `/plan`, use the `speckit-plan` skill.
- When asked to `/tasks`, use the `speckit-tasks` skill.
- When asked to `/analyze`, use the `speckit-analyze` skill.
- When asked to create or update the constitution, use the `speckit-constitution` skill when it fits the task.

Slash-style names here are workflow aliases, not native Codex CLI commands.

## Repository Expectations

- Preserve the distinction between PostgreSQL as the local or test warehouse path and Snowflake as the target production warehouse and query engine unless a spec explicitly changes it.
- Preserve clear ingestion -> raw/staging -> final warehouse boundaries unless the change is intentional and documented.
- Keep external credentials, endpoints, and runtime configuration environment-variable driven.
- Favor minimal, verifiable changes.
- Prefer backlog maintenance and targeted spec updates over ceremony-heavy feature specs for small pipeline work.
- Do not normalize undocumented Basin behavior as a permanent contract without explicit acceptance.

## Preferred Execution Pattern

- For routine and well-scoped backlog items: update backlog context, implement directly, and verify.
- For ambiguous or cross-cutting work: create or update a feature spec first, then plan, then tasks if needed.
- New feature work should normally include both implementation and verification updates, even when the change is small.

## Preferred Personas

Use these repo-local skills when the task matches:

- `.agents/skills/delta-platform-implementer/` for the main developer agent that executes one backlog item or one planned task.
- `.agents/skills/delta-test-coverage-guardian/` for an agent dedicated to adding or improving tests once behavior is defined.
- `.agents/skills/delta-docs-auditor/` for scheduled or manual audits of documentation, backlog state, and spec currency.
- `.agents/skills/speckit-specify/`, `.agents/skills/speckit-clarify/`, `.agents/skills/speckit-plan/`, `.agents/skills/speckit-tasks/`, and `.agents/skills/speckit-analyze/` for feature design and planning workflows.

Cloud execution agents should normally pick up one concrete backlog item or one task from `tasks.md`, not an entire feature.
