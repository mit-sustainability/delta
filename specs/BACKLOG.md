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
