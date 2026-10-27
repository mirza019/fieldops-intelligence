from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Response

from analytics.kpis import KPI_CATALOG
from analytics.reporting import build_management_report
from streamlit_app.services.ai import mock_answer
from streamlit_app.services.data import load_kpis, load_table
from streamlit_app.services.simulation import simulate

app = FastAPI(title="FieldOps Intelligence API", version="0.1.0")
ROLE_PERMISSIONS = {
    "administrator": {"read", "manage", "analyze"},
    "performance_manager": {"read", "approve", "analyze"},
    "data_analyst": {"read", "analyze"},
    "field_service_coordinator": {"read", "update_actions"},
}


def current_role(x_demo_role: Annotated[str, Header()] = "data_analyst") -> str:
    if x_demo_role not in ROLE_PERMISSIONS:
        raise HTTPException(401, "Unknown demo role")
    return x_demo_role


def require(permission: str):
    def dependency(role: Annotated[str, Depends(current_role)]) -> str:
        if permission not in ROLE_PERMISSIONS[role]:
            raise HTTPException(403, f"Role {role} lacks {permission}")
        return role

    return dependency


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "read-only-demo"}


@app.get("/api/kpis")
def kpis(_: Annotated[str, Depends(require("read"))]) -> list[dict]:
    values = load_kpis()
    return [
        {
            "id": code,
            "name": KPI_CATALOG[code].name,
            "value": value,
            "unit": KPI_CATALOG[code].unit,
            "target": KPI_CATALOG[code].target,
        }
        for code, value in values.items()
    ]


@app.get("/api/quality")
def quality(_: Annotated[str, Depends(require("read"))]) -> list[dict]:
    return load_table("quality_results").to_dict(orient="records")


@app.post("/api/ai/analyze")
def analyze(question: str, _: Annotated[str, Depends(require("analyze"))]) -> dict:
    return mock_answer(question, load_kpis())


@app.post("/api/simulations")
def simulation(
    parameters: dict[str, float], _: Annotated[str, Depends(require("analyze"))]
) -> dict:
    values = load_kpis()
    baseline = {
        "sla": values["KPI-001"],
        "backlog": values["KPI-005"],
        "utilization": values["KPI-003"],
        "resolution": values["KPI-004"],
        "cost": values["KPI-008"],
    }
    keys = [
        "technicians_pct",
        "demand_pct",
        "parts_pct",
        "scheduling_pct",
        "travel_pct",
        "cost_pct",
    ]
    return simulate(baseline, *(float(parameters.get(key, 0)) for key in keys))


@app.get("/api/improvements")
def improvements(_: Annotated[str, Depends(require("read"))]) -> list[dict]:
    return load_table("improvement_cases").to_dict(orient="records")


@app.get("/api/reports/management.pdf")
def management_report(_: Annotated[str, Depends(require("read"))]) -> Response:
    return Response(
        build_management_report(load_kpis()),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=fieldops-management-report.pdf"},
    )
