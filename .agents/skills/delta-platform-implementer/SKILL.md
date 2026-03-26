---
name: "delta-platform-implementer"
description: "Implement one backlog item or one planned task with minimal scope, aligned to the repository constitution and spec artifacts."
compatibility: "Requires AGENTS.md, constitution.md, and optionally specs/BACKLOG.md or a feature folder under specs/"
---

## Purpose

Use this skill for the main developer agent that executes one concrete unit of work in the repository.

## Required Context

Before making changes, read:

- `.specify/memory/constitution.md`
- `AGENTS.md`
- `specs/BACKLOG.md` if the task originated from the backlog
- the relevant `spec.md`, `plan.md`, and `tasks.md` if the task belongs to a feature folder

## Operating Rules

- Work on one backlog item or one task at a time.
- Prefer the smallest defensible change surface.
- If the work is ambiguous, missing scope, or likely cross-domain, stop and require a spec or plan instead of improvising.
- If code and docs disagree, verify the code path first and report spec or doc drift explicitly.
- Preserve the distinction between PostgreSQL local or test warehouse behavior and Snowflake target-state production behavior unless the governing spec changes it.

## Expected Workflow

1. Identify the exact work unit being executed.
2. Confirm whether backlog-only context is sufficient or feature-spec context is required.
3. Read only the necessary repository files for that work unit.
4. Implement the change with minimal scope.
5. Run the relevant verification for changed behavior.
6. Update the related task or backlog status if part of the requested workflow.
7. Report code changes, verification results, and any detected doc or spec drift.

## Deliverables

- Code changes for the assigned work unit
- Verification for the changed behavior
- Status update for the matching backlog item or task when requested
- Explicit note if follow-up spec, docs, or migration cleanup is needed
