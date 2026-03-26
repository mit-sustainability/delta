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
