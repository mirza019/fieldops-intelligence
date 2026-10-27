from pathlib import Path

from analytics.reporting import build_management_report
from streamlit_app.services.data import load_kpis

OUTPUT = Path("output/pdf/fieldops-management-report.pdf")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
build_management_report(load_kpis(), OUTPUT)
print(OUTPUT.resolve())
