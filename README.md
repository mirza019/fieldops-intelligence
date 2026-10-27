# FieldOps Intelligence

## 1. Project title and executive summary
**FieldOps Intelligence — AI-Powered Field Service Performance & Digital Transformation Platform** is a synthetic industrial field-service portfolio system connecting deterministic data generation, quality governance, dimensional modeling, shared KPIs, protected APIs, React, Streamlit, Power BI source, evidence-grounded AI, Lean workflows, simulation, and optional Fabric CI/CD. Local components are tested; external services and Windows validation are reported separately.

## 2. Business problem
Service organizations face SLA breaches, repeat visits, constrained technicians, parts delays, travel cost, fragmented definitions, unreliable data, and slow corrective action. This project provides one governed path from source event to management action.

## 3. Project objectives
Generate reproducible data; govern quality and metrics; publish trustworthy analytics; keep AI grounded; require human approval for operational change; remain runnable on Apple Silicon without an AI key.

## 4. Job-relevant technical competencies
Python, Pandas, SQLAlchemy, Alembic, PostgreSQL, dimensional modeling, KPI/data governance, FastAPI/RBAC, React/TypeScript, Streamlit/Plotly, Parquet, PBIP/PBIR/TMDL/DAX/M, Fabric CI/CD, Docker, and GitHub Actions.

## 5. Key features
Implemented locally: three data-volume profiles, 43-table metadata, calculated KPIs, quality results, eight-mode Streamlit app, Parquet snapshot, protected FastAPI analytics, React KPI command center, deterministic evidence-grounded AI, simulation, Power BI structural validation, and non-destructive Fabric publisher.

## 6. Application screenshots and demonstration
The live public Streamlit application is available at [fieldops-intelligence-mirza019.streamlit.app](https://fieldops-intelligence-mirza019.streamlit.app/). It was deployed from `main` using `streamlit_app/app.py` and verified after cloud build. Power BI screenshots remain pending Windows Desktop validation.

## 7. High-level system architecture diagram
```mermaid
flowchart LR
 G[Generator]-->S[Staging/Quality]-->M[(PostgreSQL Mart)]-->K[Shared KPI Contract]
 K-->P[Power BI];K-->API[FastAPI]-->R[React];K-->D[Parquet]-->ST[Streamlit];K-->AI[Grounded AI]-->W[Human-approved action]
```

## 8. Technology stack
Python 3.12, Pandas/NumPy/Faker, SQLAlchemy/Alembic/PostgreSQL, FastAPI/Pydantic, React/TypeScript/Vite/TanStack Query, Streamlit/Plotly/Parquet, Power BI project formats, `fabric-cicd`, Docker Compose, Pytest/Ruff and GitHub Actions.

## 9. Database architecture and schema overview
The authoritative model is `backend/app/models/database.py`; the migration is `backend/migrations/versions/0001_enterprise_baseline.py`. UUID operational/control keys, integer analytical keys, `NUMERIC(18,2)` money, currency codes, timezone-aware timestamps, checks, uniques, and indexes are implemented.

## 10. Complete table inventory with table counts by schema
Metadata-verified total: **43 tables**—`ops` 11, `staging` 4, `mart` 15, `governance` 5, `workflow` 4, `platform` 4. The required 42 are extended by normalized `ops.visit_technicians`. Live PostgreSQL row counts await migration execution. Full inventory: `docs/data-model/physical-model.md`.

## 11. Operational entity relationship diagram
```mermaid
erDiagram
 CUSTOMERS||--o{SITES:owns
 SITES||--o{EQUIPMENT:contains
 EQUIPMENT||--o{SERVICE_ORDERS:receives
 SERVICE_ORDERS||--o{SERVICE_VISITS:comprises
 SERVICE_VISITS||--o{VISIT_TECHNICIANS:assigns
 TECHNICIANS||--o{VISIT_TECHNICIANS:works
 SERVICE_VISITS||--o{TIME_ENTRIES:records
 SERVICE_ORDERS||--o{PARTS_REQUESTS:requires
 SERVICE_ORDERS||--o{COST_TRANSACTIONS:incurs
```

## 12. Dimensional star schema diagram
```mermaid
flowchart TB
 D[DimDate]-->O[FactServiceOrder];C[DimCustomer]-->O;R[DimRegion]-->O;E[DimEquipment]-->O;T[DimServiceType]-->O;S[DimStatus]-->O;SL[DimSLA]-->O
 O-->V[FactServiceVisit];V-->TT[FactTechnicianTime];O-->CO[FactServiceCost];O-->PF[FactPartsFulfillment];O-->SE[FactSLAEvent];D-->DQ[FactDataQuality]
```

## 13. Power BI semantic model overview
`powerbi/FieldOpsIntelligence.pbip` links PBIR and TMDL sources with explicit measures, Power Query, date source, one-direction relationship metadata, and five page identifiers. Structural checks pass; Desktop validation is pending.

## 14. Data modeling design decisions
Facts declare grain; aggregations avoid fact-to-fact joins; conformed dimensions filter facts; SCD2 preserves meaningful history; date roles are explicit; bidirectional filtering is avoided; staging/operational tables stay outside the report model.

## 15. Data generation and synthetic business scenarios
Small/medium/large profiles create 1k/25k/50k orders plus derived visits, time, parts, costs, SLA, cases and actions. Repairs increase repeats, remote regions raise travel cost, and selected parts raise lead time. A manifest identifies controlled raw defects.

## 16. Data engineering pipeline workflow
```mermaid
flowchart LR
 A[Generate]-->B[Register]-->C[Raw+Hash]-->D[Validate]
 D--invalid-->Q[Quarantine];D--accepted-->V[Validated]-->M[Dimensions/Facts]-->K[Reconcile]-->P[Atomic Publish]-->X[Alert/Audit]
```
The portable snapshot is functional. Full transactional PostgreSQL orchestration remains unverified.

## 17. Source-to-target transformation mapping
`docs/data-model/source-to-target-mapping.md` documents source/target fields, conversions, business rules, nulls, validation and historical behavior, including completion, SLA, utilization and cost examples.

## 18. Data quality governance framework
Executable checks cover completeness, uniqueness, validity, consistency, references and freshness. Rule-level applicable/passed/failed counts produce a documented score. PostgreSQL quarantine and result tables are defined.

## 19. KPI catalog and metric definitions
The 18 governed definitions are in `docs/kpi-catalog/kpis.md`. Six headline KPIs are executable through the shared contract. Zero denominators return null and KPI values are reused by Streamlit, API, React and AI evidence.

## 20. Power BI dashboard pages and features
PBIR metadata defines Executive, Operations, Cost, Lean and Data Quality pages. Visual authoring/rendering, interactions and accessibility require Windows Desktop validation and are not claimed complete.

## 21. AI Performance Analyst architecture
```mermaid
flowchart LR
 Q[Authorized question]-->I[Intent]-->T[Allowlisted tool]-->E[Verified evidence]-->L[Mock/Gemini/Ollama]-->O[Observation/Hypothesis/Recommendation]
```
Deterministic mock mode is implemented and labels hypotheses. Arbitrary SQL is not accepted; Gemini/Ollama adapters remain planned.

## 22. Process digitization and automation
Models cover pipeline runs, alerts, audits, approvals, cases and actions. Public Streamlit is deliberately read-only. Operational mutations belong behind API roles and audit events.

## 23. Lean continuous improvement workflow
Generated DMAIC cases/actions are displayed read-only. Lifecycle: Define → Measure → Analyze → manager-approved Improve → Control → Complete. KPI movement is not treated as causal proof.

## 24. What-if simulation methodology
A deterministic directional capacity model combines technicians/scheduling with demand, parts, travel and cost assumptions to estimate SLA, backlog, utilization, resolution time and cost. Outputs are explicitly estimates and are unit-tested.

## 25. Role-based access control
FastAPI enforces administrator, manager, analyst and coordinator permissions server-side; tests prove denied analyst access. Header roles are development-only and must become OIDC/JWT in production.

## 26. API architecture and endpoints
`GET /health`, `/api/kpis`, `/api/quality`, `/api/improvements`, `/api/reports/management.pdf`; `POST /api/ai/analyze`, `/api/simulations`. OpenAPI is served at `/docs`.

## 27. Local installation on macOS
```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,streamlit]'
python -m scripts.build_demo_data --profile small
```

## 28. Docker Compose startup
Run `docker compose up --build` for PostgreSQL 16 and the demo API.

## 29. Database initialization and migrations
```bash
export DATABASE_URL='postgresql+psycopg://fieldops:fieldops@localhost:5432/fieldops'
alembic -c backend/migrations/alembic.ini upgrade head
```
Verified against an isolated PostgreSQL 16 instance: revision `0001_enterprise_baseline`, 43 tables and 45 foreign keys.

## 30. Synthetic data generation commands
Use `python -m data.generators.generate --profile medium --output data/synthetic` and `python -m scripts.build_demo_data --profile small --output data/demo`.

## 31. Pipeline execution commands
Portable publication: `python -m scripts.build_demo_data --profile small`. Database-backed checkpoint orchestration remains a known gap.

## 32. Backend and frontend startup
```bash
uvicorn backend.app.main:app --reload
streamlit run streamlit_app/app.py
cd frontend && npm install && npm run dev
```

## 33. Power BI PBIP/PBIR/TMDL setup
Configure `FIELDOPS_PBI_HOST`/`FIELDOPS_PBI_DATABASE`, run `python -m scripts.validate_powerbi`, then open the PBIP in compatible Windows Power BI Desktop.

## 34. Power BI Desktop validation on Windows
Verify source parsing, credentials, refresh, relationships, DAX reconciliation, five pages, interactions, navigation and formats. Status: **requires external validation**.

## 35. Testing and verification
Commands: `ruff check .`, `pytest -q`, `python -m scripts.validate_powerbi`, `python -m compileall backend analytics streamlit_app scripts`, `npm run build`. Latest: 12 Python tests, lint, Power BI structure, React build and Streamlit startup passed; production npm audit found zero vulnerabilities.

## 36. Performance and scalability
Vectorized generation supports 1k/25k/50k profiles. No database size, timing or query benchmark is claimed until reproducibly measured. Indexes cover major foreign keys and filters.

## 37. Security and data privacy
All data is synthetic; secrets are environment-only; `.env` is ignored; public mode is read-only; Fabric scripts print no tokens and delete no unrelated items. Demo auth is not production authentication.

## 38. GitHub Actions and CI/CD
CI runs Python lint/tests, data generation, Power BI checks, compilation, frontend build and dependency audit. Fabric deployment is manual, environment-gated and secret-backed.

## 39. Deployment options
Streamlit Community Cloud is deployed and consumes the checked-in Parquet snapshot: [public FieldOps demo](https://fieldops-intelligence-mirza019.streamlit.app/). FastAPI/PostgreSQL use Docker or native PostgreSQL; Fabric uses `fabric-cicd` 1.4-compatible scripts. Runbooks live in `docs/deployment/`.

## 40. Complete end-to-end demo walkthrough
Generate snapshot → start Streamlit → review/filter KPIs → inspect quality → ask AI → inspect evidence/DMAIC → run simulation → inspect pipeline → start API/React → validate Power BI → open PBIP on Windows when available.

## 41. Project structure
`data/` generation; `analytics/` contracts; `backend/` API/models/migrations; `frontend/` React; `streamlit_app/` public client; `powerbi/` BI source; `scripts/` build/validate/deploy; `docs/` design/runbooks; `.github/` CI.

## 42. Known limitations
- PostgreSQL migration is verified; transactional ingestion/pipeline row loading remains pending.
- Full PBIR visuals require Desktop authoring/validation.
- Gemini/Ollama adapters, production OIDC, mutation workflows, scheduler, email and PDF export are incomplete.
- Fabric deployment, Power BI refresh and Windows Desktop checks still require external Microsoft tenant/Windows access.

## 43. Future enhancements
Complete transactional ingestion, KPI SQL views, PBIR visuals, OIDC/mutations/audit, Gemini/Ollama, APScheduler, PDF reports, measured performance tests, screenshots and external deployments.

## 44. License and disclaimer
Educational portfolio project using fictional data. No Siemens Energy branding, confidential information, proprietary schema or internal process is included. Power BI/Fabric features and licensing depend on the account and tenant.
