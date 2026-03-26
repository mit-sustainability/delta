---
name: "delta-test-coverage-guardian"
description: "Add or improve tests for a defined backlog item, specification, plan, or task without widening product scope."
compatibility: "Requires AGENTS.md, constitution.md, and either backlog context or feature task context"
---

## Purpose

Use this skill for an agent dedicated to writing or strengthening tests once behavior is defined.

## Required Context

Before making changes, read:

- `.specify/memory/constitution.md`
- `AGENTS.md`
- the relevant backlog item
- `spec.md`, `plan.md`, and `tasks.md` when they exist

## Operating Rules

- Do not invent new product behavior.
- Derive tests from stated requirements, planned behavior, and current code contracts.
- Prefer the smallest test set that proves the changed behavior.
- If behavior is not defined clearly enough to test, stop and report the missing requirement.
- Preserve repository warehouse-path assumptions: PostgreSQL for local or test control paths, Snowflake for target-state production behavior.

## Expected Workflow

1. Map the assigned work to explicit behaviors that require verification.
2. Identify existing tests and current coverage gaps.
3. Add or update tests with minimal unrelated refactoring.
4. Run the relevant verification commands.
5. Report what behaviors are now covered and what remains intentionally untested.

## Deliverables

- New or improved tests for the assigned work
- Verification results
- Explicit note of any remaining coverage gap caused by missing requirements, missing seams, or infrastructure limits
