from streamlit_app.services.ai import answer, mock_answer
from streamlit_app.services.simulation import simulate


def test_mock_ai_cites_each_metric() -> None:
    values = {"KPI-001": 0.8, "KPI-005": 600.0}
    result = mock_answer("why", values)
    assert {item["kpi_id"] for item in result["evidence"]} == set(values)
    assert result["provider"] == "deterministic mock"


def test_answer_uses_gemini_when_api_key_exists(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

    import streamlit_app.services.ai as ai_module

    def fake_call(api_key: str, model_name: str, prompt: str) -> str:
        assert api_key == "test-key"
        assert model_name == "gemini-test"
        assert "KPI-001" in prompt
        return '{"provider":"gemini","question":"why","observation":"Below target","hypothesis":"Capacity","recommendation":"Review","evidence":[{"kpi_id":"KPI-001","value":0.8}]}'

    monkeypatch.setattr(ai_module, "_call_gemini_api", fake_call)

    result = answer("why", {"KPI-001": 0.8})
    assert result["provider"] == "gemini"
    assert result["observation"] == "Below target"


def test_answer_falls_back_to_mock_without_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    result = answer("why", {"KPI-001": 0.8})
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
