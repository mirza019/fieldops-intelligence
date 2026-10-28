# Requirements traceability matrix

## Role competency mapping

| Competency | Requirement area | Evidence in repo | Status |
| --- | --- | --- | --- |
| Power BI / PL-300 | PBIP source, semantic model conventions, dashboard patterns | `powerbi/`, `README.md`, `docs/architecture/system-architecture.md` | Implemented baseline |
| Lean Six Sigma | DMAIC case workflow and improvement governance | `streamlit_app/app.py`, `docs/implementation-plan.md` | Implemented demo flow |
| AI-enabled solution design | grounded KPI analysis and optional Gemini provider | `streamlit_app/services/ai.py` | Implemented |
| Field-service analytics | KPI contract and operational views | `analytics/`, `streamlit_app/` | Implemented |
| Data engineering | deterministic synthetic generation and validation flow | `data/`, `backend/` | Partial |
| Process digitization | FastAPI analytics API and role-based access | `backend/app/main.py` | Implemented |
| Quality assurance | pytest suite and logic checks | `streamlit_app/tests/`, `backend/tests/` | Implemented |

## Requirement-to-feature mapping

- KPI governance -> `analytics/kpis` and documentation
- Streamlit dashboard -> `streamlit_app/app.py`
- Power BI source -> `powerbi/`
- API exposure -> `backend/app/main.py`
- Improvement management -> `streamlit_app/app.py` read-only workflow
- AI assistance -> `streamlit_app/services/ai.py`
- Demo data -> `data/demo/` and generator scripts

## Verification evidence

- `pytest -q` passes in the project environment.
- Streamlit pages render without exceptions in the app test harness.
- KPI and simulation logic are covered by unit tests.
- Power BI source validation runs locally, while final visual validation remains Windows-only and external.
