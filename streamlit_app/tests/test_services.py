from streamlit_app.services.ai import mock_answer
from streamlit_app.services.simulation import simulate


def test_mock_ai_cites_each_metric() -> None:
    values = {"KPI-001": 0.8, "KPI-005": 600.0}
    result = mock_answer("why", values)
    assert {item["kpi_id"] for item in result["evidence"]} == set(values)
    assert result["provider"] == "deterministic mock"


def test_simulation_is_deterministic_and_capacity_reduces_backlog() -> None:
    baseline = {
        "sla": 0.85,
        "backlog": 500.0,
        "utilization": 0.8,
        "resolution": 80.0,
        "cost": 7000.0,
    }
    scenario = simulate(baseline, 20, 0, 0, 10, 0, 0)
    assert scenario["Backlog"] < baseline["backlog"]
    assert scenario["SLA compliance"] > baseline["sla"]
