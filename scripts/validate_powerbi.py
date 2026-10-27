from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "powerbi"


def validate() -> list[str]:
    required = [
        ROOT / "FieldOpsIntelligence.pbip",
        ROOT / "FieldOpsIntelligence.Report/definition.pbir",
        ROOT / "FieldOpsIntelligence.Report/definition/report.json",
        ROOT / "FieldOpsIntelligence.Report/definition/pages/pages.json",
        ROOT / "FieldOpsIntelligence.SemanticModel/definition.pbism",
        ROOT / "FieldOpsIntelligence.SemanticModel/definition/model.tmdl",
        ROOT / "FieldOpsIntelligence.SemanticModel/definition/tables.tmdl",
    ]
    missing = [str(path) for path in required if not path.exists()]
    for path in required:
        if path.suffix in {".json", ".pbip", ".pbir", ".pbism"} and path.exists():
            json.loads(path.read_text())
    if missing:
        raise SystemExit("Missing Power BI source: " + ", ".join(missing))
    model = (ROOT / "FieldOpsIntelligence.SemanticModel/definition/tables.tmdl").read_text()
    for name in ["SLA Compliance", "Service Orders"]:
        if name not in model:
            raise SystemExit(f"Missing measure: {name}")
    return [str(path.relative_to(ROOT)) for path in required]


if __name__ == "__main__":
    print(f"Validated {len(validate())} Power BI artifacts; desktop validation is separate.")
