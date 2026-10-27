from pathlib import Path

from analytics.reporting import build_management_report


def test_pdf_is_created(tmp_path: Path) -> None:
    path = tmp_path / "report.pdf"
    payload = build_management_report({"KPI-001": 0.9, "KPI-005": 600.0}, path)
    assert payload.startswith(b"%PDF-")
    assert len(payload) > 2_000
