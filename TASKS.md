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
- [x] Complete synthetic visits, parts, time, costs, SLA, improvements, and actions
- [~] Six-schema SQLAlchemy physical model (43 tables including visit-technician junction)
- [x] Alembic baseline migration verified on PostgreSQL 16 (43 tables, 45 foreign keys)
- [ ] PostgreSQL seed loader
- [x] Generator reproducibility and defect-manifest tests

## Phase 3 — Data engineering

- [ ] Ingestion, validation, quarantine, and incremental publish pipeline
- [~] Shared KPI calculations/tests complete; PostgreSQL KPI views pending
- [ ] Run state, checkpoints, retry, and transaction recovery

## Phase 4 — Power BI

- [x] PBIP/PBIR/TMDL project source baseline
- [~] Initial DAX and PostgreSQL Power Query; full measure catalog pending
- [ ] Five required report pages and theme
- [x] Automated source validation
- [!] Windows Power BI Desktop verification

## Phases 5–10

- [~] FastAPI read APIs and demo RBAC; production identity/mutations/audit pending
- [~] React command center connected to APIs; remaining workflows use Streamlit
- [~] Grounded mock AI; Gemini/Ollama adapters pending
- [~] DMAIC read-only workspace and calculated what-if simulation
- [~] Verified management PDF/API complete; alerts, scheduler, and notifications pending
- [ ] End-to-end verification, screenshots, deployment, and portfolio polish

## Added portfolio and deployment requirements

- [x] Shared analytical KPI/filter contract
- [x] Read-only Streamlit application with eight modes
- [x] Portable governed Parquet demonstration snapshot
- [x] PBIP/PBIR/TMDL source and structural validator
- [x] Optional `fabric-cicd` 1.4 access check and deployment scripts
- [x] Streamlit Community Cloud and student Power BI setup documentation
- [x] CI workflows for Python, data/KPI, Streamlit, Power BI, frontend, and security
- [~] Local Git repository configuration
- [!] GitHub authentication is invalid; repository creation/push blocked until re-authenticated
- [!] External Streamlit, Power BI, and Fabric deployments require account access
