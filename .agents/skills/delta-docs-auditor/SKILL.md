---
name: "delta-docs-auditor"
description: "Audit documentation, backlog, and spec artifacts for correctness and currency against the current repository behavior."
compatibility: "Requires AGENTS.md, constitution.md, and repository docs or spec artifacts"
---

## Purpose

Use this skill for a scheduled agent that checks whether documentation and planning artifacts still match the repository.

## Required Context

Before auditing, read:

- `.specify/memory/constitution.md`
- `AGENTS.md`
- `specs/BACKLOG.md` if it exists
- active feature folders under `specs/` if they exist
- the repository docs or operational docs being audited

## Operating Rules

- Default to read-only analysis unless the task explicitly authorizes doc fixes.
- Treat code paths and current runtime behavior as the source of truth when docs disagree.
- Focus on correctness, currency, migration assumptions, execution boundaries, and dependency declarations.
- Check that docs do not blur PostgreSQL local or test behavior with Snowflake target-state production behavior.
- Open or recommend concrete follow-up work when drift is found.

## Expected Workflow

1. Identify the docs and artifacts in scope.
2. Compare them against current code paths, config, workflows, and repository structure.
3. Record drift, stale assumptions, missing dependencies, and incorrect operational guidance.
4. Recommend or apply minimal documentation fixes if authorized.
5. Produce a concise audit summary with file references and suggested next actions.

## Deliverables

- Audit report of stale, incorrect, or missing documentation
- Optional doc-only fixes if explicitly requested
- Follow-up backlog or spec recommendations when drift is large enough to require design updates
