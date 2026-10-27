from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DEMO_DATA_PATH", ROOT / "data" / "demo"))


def load_table(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Demo snapshot missing: {path}. Run scripts/build_demo_data.py.")
    return pd.read_parquet(path)


def load_kpis() -> dict[str, float | None]:
    return json.loads((DATA_DIR / "kpi_snapshot.json").read_text())


def available() -> bool:
    return (DATA_DIR / "service_orders.parquet").exists()
