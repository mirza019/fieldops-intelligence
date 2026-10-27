# Delivery checklist

Legend: `[x]` implemented and verified, `[~]` in progress, `[ ]` not started, `[!]` external verification required.

## Phase 1 — Architecture and planning

- [x] Repository structure and engineering conventions
- [x] Business requirements, roles, and acceptance boundaries
- [x] System architecture and data-flow design
- [x] Warehouse grains and dimensional model
- [x] Governed KPI catalog for the 18 required KPIs
- [x] Initial data-quality rule catalog and scoring method
- [x] Phased implementation plan

## Phase 2 — Synthetic data and database

- [~] Deterministic synthetic-data generator (core entities and orders implemented)
- [~] Controlled defect injection with clean ground truth (implemented for orders)
- [ ] Complete operational entities, visits, parts, time, costs, SLA, improvements
- [~] Six-schema SQLAlchemy physical model (43 tables including visit-technician junction)
- [~] Alembic baseline migration; live PostgreSQL execution pending
- [ ] PostgreSQL seed loader
- [x] Generator reproducibility and defect-manifest tests

## Phase 3 — Data engineering

- [ ] Ingestion, validation, quarantine, and incremental publish pipeline
- [ ] KPI SQL views and reconciliation tests
- [ ] Run state, checkpoints, retry, and transaction recovery

## Phase 4 — Power BI

- [ ] PBIP/PBIR/TMDL project source
- [ ] DAX measures and Power Query
- [ ] Five required report pages and theme
- [ ] Automated source validation
- [!] Windows Power BI Desktop verification

## Phases 5–10

- [ ] FastAPI APIs, authentication, authorization, and audit
- [ ] React workflow application connected to APIs
- [ ] Grounded AI analyst with mock, Gemini, and Ollama providers
- [ ] DMAIC workflow and what-if simulation
- [ ] PDF reports, alerts, scheduler, and notifications
- [ ] End-to-end verification, screenshots, deployment, and portfolio polish

## Added portfolio and deployment requirements

- [ ] Shared analytical KPI/filter contract
- [ ] Read-only Streamlit application with eight pages
- [ ] Portable governed Parquet/DuckDB demonstration snapshot
- [ ] Genuine PBIP/PBIR/TMDL source and structural validator
- [ ] Optional `fabric-cicd` access check and deployment scripts
- [ ] Streamlit Community Cloud and student Power BI setup documentation
- [ ] CI workflows for Python, data/KPI, Streamlit, Power BI, frontend, and security
- [~] Local Git repository configuration
- [!] GitHub authentication is invalid; repository creation/push blocked until re-authenticated
- [!] External Streamlit, Power BI, and Fabric deployments require account access
