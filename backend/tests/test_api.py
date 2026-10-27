from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_and_kpis() -> None:
    assert client.get("/health").status_code == 200
    response = client.get("/api/kpis", headers={"x-demo-role": "performance_manager"})
    assert response.status_code == 200
    assert response.json()[0]["id"].startswith("KPI-")


def test_authorization_is_server_side() -> None:
    denied = client.post(
        "/api/ai/analyze",
        params={"question": "why"},
        headers={"x-demo-role": "field_service_coordinator"},
    )
    assert denied.status_code == 403
    allowed = client.post(
        "/api/ai/analyze", params={"question": "why"}, headers={"x-demo-role": "data_analyst"}
    )
    assert allowed.status_code == 200
    assert allowed.json()["evidence"]


def test_management_report_download() -> None:
    response = client.get("/api/reports/management.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
