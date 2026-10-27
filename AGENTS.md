# FieldOps Intelligence Engineering Guide

## Scope and priorities

Build a production-inspired, synthetic-data-only field-service analytics platform. Prefer working vertical slices over disconnected screens. Power BI source is a mandatory deliverable, but desktop validation must be recorded separately because the primary environment is macOS.

## Architecture rules

- Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Pydantic 2.
- React, TypeScript, Vite, Tailwind, TanStack Query, and Recharts.
- Keep source, staging/quarantine, validated operational, and dimensional analytical layers distinct.
- Facts have an explicit documented grain. Never join two facts directly or aggregate measures after a fan-out join.
- Use UTC timestamps in persistence and ISO 8601 at API boundaries.
- Preserve source business keys and use surrogate keys in analytical dimensions.
- KPI values come from governed SQL/analytics functions, never UI constants or LLM output.
- LLMs may call only allowlisted, parameterized analytics tools. Human approval is required for workflow changes.
- All demo entities and data are fictional. Never add confidential or corporate-branded material.

## Business definitions

- Eligible completed order: status `completed`, not cancelled, has valid completion timestamps, and meets the KPI-specific completeness rules.
- SLA compliant: an eligible completed order whose completion timestamp is on or before its contractual due timestamp.
- First-time fix: an eligible resolved order completed successfully with exactly one completed service visit and no reopen event.
- Productive hours: approved on-site maintenance, commissioning, inspection, repair, or remote technical-support time.
- Available hours: scheduled working hours less approved leave, public holidays, and training.
- Backlog: non-cancelled orders not in a terminal status as of the reporting timestamp.

## Development workflow

1. Update `TASKS.md` as acceptance criteria move.
2. Add migrations for persistent schema changes.
3. Add or update tests with functional changes.
4. Run the narrow test suite, then the complete suite before marking a phase complete.
5. Keep docs and `.env.example` synchronized with behavior.

## Testing and quality gates

- Python: `pytest`, `ruff check .`, and type checking once configured.
- Frontend: unit tests, TypeScript build, and lint.
- Database/KPIs: test zero denominators, exclusions, boundaries, filtering, idempotency, and rollback.
- Power BI: run source-structure validation locally; record Power BI Desktop validation only after it is performed on Windows.
- Do not use placeholder assertions, fake buttons, or hardcoded dashboard metrics.

## Database and public-demo rules

- PostgreSQL schemas are `ops`, `staging`, `mart`, `governance`, `workflow`, and `platform`.
- Financial values use `NUMERIC(18,2)` plus ISO 4217 currency codes. Persisted timestamps are timezone-aware.
- Many-to-many relationships use junction tables; relational columns never contain lists of IDs.
- Incremental loads use stable business keys, source update timestamps, and content hashes.
- Streamlit is read-only and uses governed Parquet/DuckDB snapshots; it complements React/FastAPI.
- Public Power BI embedding is allowed only for approved synthetic public data.
- Fabric deployment is opt-in and never deletes unrelated items or prints credentials.
