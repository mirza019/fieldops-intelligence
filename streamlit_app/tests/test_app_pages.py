from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_all_streamlit_pages_render_without_exceptions() -> None:
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15).run()
    pages = [
        "Executive Performance",
        "Operational Analytics",
        "Power BI Analytics",
        "AI Performance Analyst",
        "Data Quality & Governance",
        "Lean Continuous Improvement",
        "What-If Simulation",
        "Pipeline Monitoring",
    ]
    for page in pages:
        app.radio[0].set_value(page).run()
        assert not app.exception, f"{page}: {app.exception}"
