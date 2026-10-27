# FieldOps Intelligence

AI-Powered Field Service Performance & Digital Transformation Platform — a synthetic, portfolio-grade implementation for industrial maintenance, commissioning, inspection, repair, and technical support.

The repository is being delivered in verified phases. Phase 1 architecture, KPI governance, data-quality design, and conventions are complete. The first Phase 2 vertical slice provides a deterministic generator with clean ground truth, a corrupted raw order feed, and a machine-readable defect manifest. See [TASKS.md](TASKS.md) for exact status; unchecked capabilities are not claimed as complete.

## Run the current milestone

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m data.generators.generate --orders 25000
pytest
```

Generated CSV/JSON files are written to `data/synthetic/` and intentionally ignored. The clean `service_orders.csv` is the oracle used to verify validation; `raw_service_orders.csv` contains controlled defects described by `defect_manifest.json`.

## Design documentation

- `docs/implementation-plan.md`
- `docs/architecture/system-architecture.md`
- `docs/architecture/data-model.md`
- `docs/business-requirements/requirements.md`
- `docs/kpi-catalog/kpis.md`
- `docs/governance/data-quality.md`

All organizations, people, customers, and operational records are fictional. Power BI Desktop validation will remain marked pending until performed in a compatible Windows environment.
