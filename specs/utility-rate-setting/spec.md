# Feature Specification: Utility Rate Setting — Month-End Accounting Workflow

**Feature Branch**: `utility-ingest`
**Created**: 2026-05-05
**Status**: Draft
**Backlog Items**: DELTA-004 through DELTA-011
**Domain**: MITOS

---

## Problem Framing

This is **not a generic ETL pipeline**. It is a month-end accounting state compiler for MIT utility rate setting. The system must answer one binary question at the end of each run: **is the month closable?**

### Inputs (manual, inconsistently delivered)

| Source | Owner | Represents |
|--------|-------|-----------|
| SAP export (cost pool) | Finance | Financial truth — total cost per commodity to be allocated |
| Mehdi adjusted usage | Mehdi | Allocation truth — metered consumption with manual adjustments |
| Josh exceptions | Josh | Edge cases — missing meters, special assignments, overrides |
| Production data | Operations | Physical truth — actual commodity produced/delivered |

### Known Problems This System Replaces

- Unit inconsistencies (kWh, CCF, gallons mixed with MMBTU)
- Missing exceptions silently propagate to downstream allocations
- Circular dependency in CUP electricity self-use allocation
- Rounding drift across the reconciliation chain
- No centralized controls — Excel + human judgment is the current gate

### Core Design Principle

> Inputs are **authoritative but unreliable**. The system trusts what it receives and fails loudly when inputs violate structural invariants. No silent fallbacks. No implicit fixes.

---

## Architecture

### Dagster = Orchestration and Control Layer

- Load monthly input files into raw tables
- Partition runs by month (`MonthlyPartitionsDefinition`)
- Validate input completeness and schema before dbt runs
- Execute dbt transformations
- Enforce cross-source invariants after dbt
- Generate SAP-ready output files
- Gate whether the month is closable

### dbt = Transformation Layer

- Normalize units (→ MMBTU for all commodities)
- Clean and standardize all four sources
- Apply exceptions to adjusted usage
- Build allocation base (weighted shares per entity/commodity)
- Calculate rates (cost pool ÷ allocation base)
- Produce SAP staging output tables

---

## Data Flow

```
raw files (SAP, Mehdi, Josh, production)
    ↓
Dagster: input validation (completeness, schema, period match)
    ↓
dbt: staging (clean + normalize + unit conversion → MMBTU)
    ↓
dbt: intermediate — allocation base (adjusted usage ∪ exceptions)
    ↓
dbt: intermediate — rate calculation (cost pool ÷ allocation base)
    ↓
dbt: final — SAP staging output tables
    ↓
Dagster: cross-source invariant checks
    ↓
Dagster: close gate (pass = month closable; fail = named blocking conditions)
    ↓
Dagster: output generation (SAP-ready files, close report)
```

---

## Key Invariants

These must always hold. Hard failure stops the run — no silent fallback.

| ID | Invariant | Check Location |
|----|-----------|---------------|
| INV-01 | All required input files exist for the month | Dagster input validation |
| INV-02 | All usage and production normalized to MMBTU | dbt staging tests |
| INV-03 | `sum(adjusted consumption) == production` per commodity | Dagster post-dbt check |
| INV-04 | `total SAP cost pool == total allocated cost == total charges` | Dagster post-dbt check |
| INV-05 | No residual logic downstream — adjusted meters eliminate residuals upstream | dbt model structure |
| INV-06 | CUP electricity self-use uses 12-month rolling average only | dbt intermediate model |
| INV-07 | `true charges ≠ SAP charges → variance tracked explicitly` | dbt final + Dagster check |
| INV-08 | Every entity in Mehdi usage has a Josh exception or none needed (no coverage gaps) | Dagster post-dbt check |

---

## Checks Strategy

### dbt tests (table-level)

- `not_null` on all key columns
- `unique` on `(entity, commodity, month)` composite keys
- `accepted_values` on commodity names and unit codes
- Custom generic test: `valid_normalized_unit` — ensures unit is `MMBTU` after staging

### Dagster asset checks (system-level)

All implemented as `@asset_check` decorators alongside the relevant assets:

- Input validation: required files exist, schema columns present, period column matches partition month
- Josh vs Mehdi coverage: no entity in adjusted usage is missing a required exception without explicit "no exception needed" flag
- Conservation: `sum(adjusted_consumption_mmbtu) == production_mmbtu` per commodity
- Cost closure: `sum(allocated_charges) == sap_cost_pool` per commodity
- Assumed rate guard: assumed rate used only where explicitly allowed
- SAP rounding variance tracked: delta between true charge and SAP charge stored per entity
- **Month closable gate**: composite check — all prior checks green → emit `MonthClosable` asset

---

## File Scope

### New Dagster files

```
cockpit/mitos/assets/utility/
    __init__.py
    ingest.py          # Raw file loading assets, monthly partition
    validation.py      # Input completeness + schema checks (@asset_check)
    invariants.py      # Cross-source invariant checks (@asset_check)
    close_gate.py      # Month closable gate asset + output generation
cockpit/mitos/jobs/utility_jobs.py     # utility_month_close_job
```

### New dbt files

```
dbt/models/mitos/staging/
    stg_utility_sap_cost_pool.sql
    stg_utility_adjusted_usage.sql
    stg_utility_exceptions.sql
    stg_utility_production.sql
    schema.yml                   # sources + tests for all 4 staging models

dbt/models/mitos/intermediate/   # new layer
    int_utility_allocation_base.sql
    int_utility_rate_calculation.sql
    int_utility_cup_electric_rolling_avg.sql
    schema.yml

dbt/models/mitos/final/
    fct_utility_sap_output.sql
    fct_utility_close_report.sql
    schema.yml

dbt/macros/
    validate_unit_normalized.sql   # reusable generic test
```

### Updated files

```
dbt/models/mitos/sources.yml       # add utility raw source tables
cockpit/mitos/assets/__init__.py   # add utility assets
cockpit/mitos/defs.py              # add utility job
```

---

## Domain Constraints

**Warehouse parity**: All dbt models must run on `DBT_TARGET=local` (Postgres) and `DBT_TARGET=prod` (Snowflake). Unit conversion math uses `dbt.type_numeric()`. No inline Snowflake functions.

**Monthly partitioning**: Dagster partitions are `MonthlyPartitionsDefinition`. Partition key format: `YYYY-MM-DD` (start of month). All file loading assets reference the partition key to scope file discovery.

**Idempotency**: Each run for a given month-partition is a full replace, not an append. Loading assets must write with replace semantics to the raw tables.

**No implicit fixes**: Exception application is an explicit `LEFT JOIN` + `COALESCE` in the allocation base model. The join result must be inspectable. Missing exceptions that should exist are an INV-08 failure, not a silent default.

**Circularity**: CUP electricity self-use cannot use current-month production data (circular). Use 12-month rolling average computed from the `int_utility_cup_electric_rolling_avg` model, which reads from prior closed months only.

---

## Phases

| Phase | Backlog Items | Description |
|-------|--------------|-------------|
| 1 | DELTA-004 | Raw file ingestion — Dagster assets load monthly files into raw tables |
| 2 | DELTA-005 | dbt staging — clean, standardize, normalize units to MMBTU |
| 3 | DELTA-006 | dbt allocation base — apply exceptions, build allocation weights |
| 4 | DELTA-007, DELTA-008 | dbt rate calc + SAP output tables |
| 5 | DELTA-009, DELTA-010 | Dagster validation checks + cross-source invariants |
| 6 | DELTA-011 | Dagster close gate + output generation |

Phases 1–2 can be implemented before inputs are real (use fixture files). Phases 3–4 require staging to be complete. Phase 5 requires all dbt models to exist. Phase 6 requires Phase 5 to pass.

---

## Assumptions

- Input files land in a known directory per month (path convention TBD when real files are available).
- SAP export is a CSV or Excel file with cost pool by commodity; exact column names require one real file to lock the schema.
- Adjusted usage (Mehdi) is tabular with columns: entity, commodity, month, consumption, unit.
- Exceptions (Josh) are tabular with columns: entity, commodity, month, exception_type, adjusted_value, unit.
- Production data has columns: commodity, month, production, unit.
- All unit conversions to MMBTU use fixed factors (e.g., 1 CCF natural gas = 1.02 MMBTU); factors are a seed table in dbt.
- MITOS scope and group naming conventions from DELTA-003 apply to all utility assets.
