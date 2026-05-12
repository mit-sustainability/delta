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

---
## Utility Rate Setting — Month-End Accounting Workflow
*Feature spec*: `specs/utility-rate-setting/spec.md`
*Branch*: `utility-ingest`

### Phase 1 — Input Infrastructure

## DELTA-004: Utility monthly file ingestion loader

- Status: in_progress
- Priority: high
- Domain: ingestion
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-003 (mitos scope structure in place)
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: Dagster assets load the four monthly input files (SAP cost pool, adjusted usage, exceptions, production) into raw warehouse tables, partitioned by month, with replace-semantics idempotency.
- Scope: `cockpit/mitos/assets/utility/ingest.py`, `cockpit/mitos/assets/__init__.py`, `dbt/models/mitos/sources.yml` (add utility source tables), `cockpit/mitos/jobs/utility_jobs.py`
- Verification: pytest asset materialization tests using fixture CSV files for one partition month; raw table row counts match fixture; rerunning the same partition produces identical output (no duplicates).
- Notes: Monthly partition key format is `YYYY-MM-DD` (start of month). File discovery path convention should be defined using an env var so it can point to a local fixture dir in tests and a real upload dir in prod. Exact column names for SAP export require one real file before schema can be locked — use a flexible schema contract with explicit mapping until then.

---

### Phase 2 — dbt Staging and Normalization

## DELTA-005: dbt staging models for all four utility sources

- Status: todo
- Priority: high
- Domain: dbt
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-004
- Legacy Reference: none
- Parity Required: yes
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: All four input sources are cleaned, standardized, and unit-normalized to MMBTU in dedicated dbt staging models, with schema tests enforcing non-null, uniqueness, accepted commodity values, and normalized units.
- Scope: `dbt/models/mitos/staging/stg_utility_sap_cost_pool.sql`, `stg_utility_adjusted_usage.sql`, `stg_utility_exceptions.sql`, `stg_utility_production.sql`, `dbt/models/mitos/staging/schema.yml`, `dbt/macros/validate_unit_normalized.sql` (generic test), `dbt/seeds/` (unit conversion factors seed table)
- Verification: `dbt build --select path:models/mitos/staging/` passes on both `DBT_TARGET=local` and `DBT_TARGET=prod`. All schema tests pass. A fixture with a known CCF row confirms correct MMBTU output value.
- Notes: Unit conversion factors (e.g., 1 CCF = 1.02 MMBTU) must be a dbt seed table so they are auditable and editable without a code change. All staging models must produce `consumption_mmbtu` as the canonical output column — no raw unit columns passed downstream.

---

### Phase 3 — Allocation Base

## DELTA-006: dbt allocation base model

- Status: todo
- Priority: high
- Domain: dbt
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-005
- Legacy Reference: none
- Parity Required: yes
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: A single dbt model joins adjusted usage with exceptions to produce the final per-entity, per-commodity allocation base with explicit allocation weights; all exception applications are inspectable in the output table.
- Scope: `dbt/models/mitos/intermediate/int_utility_allocation_base.sql`, `dbt/models/mitos/intermediate/schema.yml` (new intermediate layer)
- Verification: dbt tests on `(entity, commodity, month)` uniqueness. Fixture test: known exception overrides a usage row and the output reflects the exception value, not the original. Sum of allocation weights per commodity per month equals 1.0 (±float tolerance).
- Notes: Exception application is an explicit LEFT JOIN + COALESCE — no implicit default. If an entity has usage but no exception when one is expected, that is a data gap (caught in DELTA-010), not a model default. The intermediate layer directory is new; create `dbt/models/mitos/intermediate/` and ensure `dbt_project.yml` materializes it as `table` or `view` as appropriate.

---

### Phase 4 — Rate Calculation and SAP Outputs

## DELTA-007: dbt rate calculation models

- Status: todo
- Priority: high
- Domain: dbt
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-006
- Legacy Reference: Excel rate-setting workbook
- Parity Required: yes
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: Per-commodity rates are calculated as SAP cost pool divided by allocation base, with CUP electricity self-use circularity resolved by substituting a 12-month rolling average from prior closed months.
- Scope: `dbt/models/mitos/intermediate/int_utility_rate_calculation.sql`, `dbt/models/mitos/intermediate/int_utility_cup_electric_rolling_avg.sql`, `dbt/models/mitos/intermediate/schema.yml`
- Verification: Fixture test: known cost pool + known allocation base produces expected rate to 4 decimal places. CUP electricity test: the rolling average model reads only rows where `month < current_partition_month` and produces the 12-month mean. `dbt build` passes on both targets.
- Notes: The rolling average for CUP electricity must explicitly filter out the current month (`month < '{{ var("partition_month") }}'`) to break the circular dependency. If fewer than 12 prior months exist, use the available months and document the minimum period as a dbt variable with a default of 3.

## DELTA-008: dbt SAP staging output tables

- Status: todo
- Priority: high
- Domain: dbt
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-007
- Legacy Reference: none
- Parity Required: yes
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: Final structured tables match the SAP upload format, with a separate variance column tracking the delta between true calculated charges and prior SAP-posted charges per entity.
- Scope: `dbt/models/mitos/final/fct_utility_sap_output.sql`, `dbt/models/mitos/final/fct_utility_close_report.sql`, `dbt/models/mitos/final/schema.yml`
- Verification: Fixture test: known rate × known allocation base = expected charge; variance column = true charge − sap charge. Schema test: no null charges in output. `dbt build` passes on both targets. Output column names and types confirmed against a sample SAP import template.
- Notes: The variance column must always be populated (zero is a valid value; null is a test failure). The close report model should be a summary view — one row per commodity per month — suitable for operator review before sign-off.

---

### Phase 5 — Dagster Validation and Invariants

## DELTA-009: Dagster input validation checks

- Status: todo
- Priority: high
- Domain: orchestration
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-004
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: Dagster `@asset_check` decorators on all four ingest assets enforce file completeness, expected schema columns, and partition-period alignment before any dbt transformation runs; any failure raises a blocking `AssetCheckSeverity.ERROR`.
- Scope: `cockpit/mitos/assets/utility/validation.py`, `cockpit/mitos/assets/__init__.py`
- Verification: pytest: fixture missing one required column → check fails with named column in error message. Fixture with wrong period in data → check fails with period mismatch message. All four sources pass checks against their valid fixtures.
- Notes: Checks must reference the partition key to verify the `month` column values in each file match the expected partition period. Period mismatch is a hard failure — do not allow a March file to silently populate a February partition.

## DELTA-010: Dagster cross-source invariant enforcement

- Status: todo
- Priority: high
- Domain: orchestration
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-007, DELTA-008, DELTA-009
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: Dagster `@asset_check` decorators on dbt final assets enforce the four system-level invariants: conservation, cost closure, Josh/Mehdi exception coverage, and assumed-rate guard; each failure names the exact commodity and entity blocking close.
- Scope: `cockpit/mitos/assets/utility/invariants.py`, `cockpit/mitos/assets/__init__.py`
- Verification: pytest per invariant: (a) adjusted consumption != production → check fails naming the commodity; (b) allocated charges != SAP pool → check fails with cost delta; (c) entity in usage with required exception absent → check fails naming the entity; (d) assumed rate used outside allowed context → check fails. All checks pass on valid fixture data.
- Notes: Conservation tolerance should be configurable (default ±0.01 MMBTU per commodity) to account for legitimate rounding, but must be explicit — not silent. Any variance outside tolerance is a hard failure. INV-07 (SAP variance tracking) is handled by the dbt model in DELTA-008; the Dagster check here validates that the variance column is populated and within a declared acceptable band.

---

### Phase 6 — Close Gate and Outputs

## DELTA-011: Dagster month-close gate and output generation

- Status: todo
- Priority: high
- Domain: orchestration
- Owner: unassigned
- Design Required: plan
- Dependencies: DELTA-009, DELTA-010
- Legacy Reference: none
- Parity Required: no
- Linked Issue: none
- Linked Spec: specs/utility-rate-setting/spec.md
- Outcome: A `month_closable` Dagster asset evaluates all prior check results and either emits a close-ready artifact or a structured failure report naming every blocking condition by invariant ID, commodity, and entity; SAP-ready output files are written only when the gate passes.
- Scope: `cockpit/mitos/assets/utility/close_gate.py`, `cockpit/mitos/assets/__init__.py`, `cockpit/mitos/jobs/utility_jobs.py` (add `utility_month_close_job`)
- Verification: Integration test with fixture: all checks passing → `month_closable` asset materializes with `status: closable` and output files written to expected path. One check failing → `month_closable` materializes with `status: blocked`, lists failing invariant IDs, no output files written.
- Notes: The close gate must never produce an ambiguous state. The output is binary: `closable` or `blocked`. The failure report must be structured (JSON or tabular), not a log message, so it can be consumed by downstream notification or review workflows. Output files written to a path controlled by an env var (same pattern as DELTA-004 file discovery).

---

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
- Scope: `cockpit/shared/`, `cockpit/core/`, `cockpit/mitos/`, `cockpit/css/`, `cockpit/definitions.py`, `dbt/models/`, `dbt/dbt_project.yml`, `dbt/selectors.yml`, and planning docs under `specs/003-mitos-css-scope-planning/`.
- Verification: domain-targeted Dagster selection checks plus `dbt build` in local/prod for both domain selectors.
- Notes: keep MITOS as transitional default until explicit domain parameterization is complete; Python-managed assets now use scope-owned `defs.py` plus logical IO manager keys rather than a single top-level `cockpit/assets/` tree.
