# Implementation plan

## Delivery approach

The platform will be built as verifiable vertical slices while respecting the requested phase order. Each phase exits only after its functional acceptance checks pass. PostgreSQL is the system of record; the web application and Power BI semantic model consume governed APIs/views rather than reproducing business logic.

## Phase sequence

1. **Foundation:** requirements, C4-style architecture, roles, fact grains, KPI and quality catalogs, conventions.
2. **Synthetic source and persistence:** deterministic generators, defect manifest, operational schema, warehouse schema, Alembic migrations, seed command.
3. **Governed pipeline:** immutable landing batches, configurable rules, quarantine, validated publish, dimensional loading, KPI snapshots, run audit.
4. **Power BI:** supported PBIP/PBIR/TMDL source, database-backed Power Query, explicit DAX, five report pages, structural checks, Windows validation checklist.
5. **API:** authentication, RBAC, KPIs, governance, pipeline control, improvements, alerts, audit.
6. **Web application:** design system and ten real workflow pages with loading, error, empty, and authorization states.
7. **AI analyst:** allowlisted tools, evidence envelope, deterministic mock, optional Gemini/Ollama providers, injection resistance.
8. **Improvement and simulation:** DMAIC transitions, approvals, 5 Whys, Pareto, scenario model with explicit assumptions.
9. **Automation and reporting:** APScheduler with database locks/state, in-app notifications, verified PDF reports.
10. **Release:** complete tests, demo seed and storyline, screenshots, container builds, CI, deployment docs, limitation register.

## Mandatory physical architecture extension

The persistence baseline is 43 tables across six PostgreSQL schemas: the required 42-table inventory plus `ops.visit_technicians`, which normalizes the visit-to-technician many-to-many relationship. PostgreSQL remains authoritative for full local development; the public portfolio path reads governed Parquet snapshots through DuckDB. Streamlit complements rather than replaces React/FastAPI or Power BI.

After the database/pipeline contract is stable, delivery adds the Streamlit vertical slice, genuine Power BI project source, optional `fabric-cicd` scripts, CI checks, and deployment runbooks. External publication is recorded only after verified account-backed deployment.

## Verification gates

- Generation: same seed produces byte-equivalent data and the configured anomalies appear in a machine-readable manifest.
- Pipeline: reruns are idempotent, failed critical stages roll back, and rejected rows are explainable.
- KPI: SQL results match fixture calculations and DAX reconciliation extracts, including empty denominators.
- API/UI: role checks are enforced server-side; every displayed metric is fetched; mutations create audit events.
- AI: every numerical statement maps to an evidence item; arbitrary SQL is impossible.
- Power BI: source validator passes. Desktop load, refresh, relationships, DAX, visuals, and interactions remain explicitly pending until tested on Windows.

## Initial milestone

Milestone 1 establishes all Phase 1 artifacts and a runnable Phase 2 generator slice. It generates clean customers, sites, technicians, equipment, and service orders plus a corrupted raw order feed and a precise defect manifest. Subsequent work expands this schema without changing the deterministic contract.
