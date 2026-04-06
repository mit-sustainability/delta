# Backlog

## Usage

- This is the default work queue for the repository.
- Keep items small, independently ownable, and easy to hand to a cloud execution agent.
- Use a dedicated feature spec folder under `specs/` only when a backlog item is cross-domain, contract-changing, migration-sensitive, deployment-changing, integration-heavy, or otherwise ambiguous.
- When a backlog item gets a dedicated feature folder, link it from the item and keep status in sync.

## Item Template

```md
## DELTA-XXX: Short Title

- Status: todo | in_progress | blocked | done
- Priority: high | medium | low
- Domain: ingestion | orchestration | dbt | warehouse | migration | deployment | docs | testing
- Owner: unassigned
- Design Required: no | specify | plan | tasks
- Dependencies: none
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: none
- Outcome: one clear sentence describing the operator-facing or downstream-facing result
- Scope: concrete files, modules, systems, or boundaries expected to change
- Verification: tests, checks, or operational validation expected before completion
- Notes: optional migration assumptions, risks, or constraints
```

## Active Backlog

<!-- Add backlog items below this line -->

## DELTA-001: Sync Snowflake notebooks into repo

- Status: todo
- Priority: medium
- Domain: warehouse
- Owner: unassigned
- Design Required: plan
- Dependencies: Snowflake Git integration access and an agreed source notebook inventory
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: none
- Outcome: Snowflake-authored notebooks are version controlled under `./notebooks` with a repeatable sync workflow that operators can run without ad hoc file copying.
- Scope: `notebooks/`, notebook sync documentation in `README.md` or `notebooks/README.md`, and any minimal helper or validation code needed to inventory synced notebook files.
- Verification: produce a state-diff report comparing the intended Snowflake notebook inventory to committed files under `./notebooks`, plus automated validation if a helper or manifest is added.
- Notes: define the canonical repo layout, file naming rules, and whether Snowflake remains the source of truth or the repo becomes the reviewed handoff point after sync.

## DELTA-002: Add Snowflake-to-Postgres dbt adapter macros

- Status: todo
- Priority: high
- Domain: dbt
- Owner: unassigned
- Design Required: no
- Dependencies: none
- Legacy Reference: none
- Parity Required: yes
- Linked Issue: none
- Linked Spec: none
- Outcome: dbt model authors can write Snowflake-first warehouse logic while local Postgres builds remain supported through explicit adapter-aware macros.
- Scope: `dbt/macros/`, dbt model conventions, and any targeted model updates required to replace inline Snowflake-only SQL with dispatched macros.
- Verification: automated dbt validation on both `DBT_TARGET=local` and `DBT_TARGET=prod` for any models that adopt the new macros.
- Notes: prefer Snowflake SQL in model design, but any syntax that does not run on local Postgres must move behind adapter-dispatched macros rather than remain inline in model bodies.

## DELTA-003: Introduce MITOS/CSS domain structure for Dagster and dbt

- Status: in_progress
- Priority: high
- Domain: orchestration
- Owner: codex
- Design Required: plan
- Dependencies: none
- Legacy Reference: MITOS-only defaults in current dbt schemas/groups
- Parity Required: yes
- Linked Issue: none
- Linked Spec: `specs/003-mitos-css-scope-planning/spec.md`
- Outcome: Repository structure and runtime selection patterns support independent MITOS and CSS scopes across Dagster and dbt.
- Scope: `cockpit/assets/`, `cockpit/definitions.py`, `dbt/models/`, `dbt/dbt_project.yml`, `dbt/selectors.yml`, and planning docs under `specs/003-mitos-css-scope-planning/`.
- Verification: domain-targeted Dagster selection checks plus `dbt build` in local/prod for both domain selectors.
- Notes: keep MITOS as transitional default until explicit domain parameterization is complete.
