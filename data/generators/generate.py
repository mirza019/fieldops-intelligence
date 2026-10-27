from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

REGIONS = {
    "DACH": ["DE", "AT", "CH"],
    "NORDICS": ["SE", "NO", "DK", "FI"],
    "AMERICAS": ["US", "CA", "BR"],
    "APAC": ["AU", "SG", "JP"],
}
EQUIPMENT_TYPES = ["Gas Turbine", "Steam Turbine", "Generator", "Compressor", "Pump"]
SERVICE_TYPES = ["maintenance", "commissioning", "inspection", "repair", "technical_support"]
STATUSES = ["completed", "in_progress", "scheduled", "cancelled"]


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int = 20261027
    customers: int = 400
    technicians: int = 300
    equipment: int = 1500
    orders: int = 25_000
    months: int = 24
    defect_rate: float = 0.01
    end_date: str = "2026-09-30"


def _ids(prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{number:06d}" for number in range(1, count + 1)]


def generate(config: GeneratorConfig) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, list[dict]]:
    """Return clean entities, corrupted raw orders, and an exact defect manifest."""
    rng = np.random.default_rng(config.seed)
    fake = Faker("en_US")
    fake.seed_instance(config.seed)
    customer_ids = _ids("CUS", config.customers)
    technician_ids = _ids("TEC", config.technicians)
    equipment_ids = _ids("EQP", config.equipment)
    order_ids = _ids("SO", config.orders)
    region_names = np.array(list(REGIONS))

    customer_regions = rng.choice(region_names, config.customers, p=[0.34, 0.18, 0.28, 0.20])
    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": [f"{fake.company()} Industrial" for _ in customer_ids],
        "region_code": customer_regions,
        "country_code": [rng.choice(REGIONS[r]) for r in customer_regions],
    })
    sites = customers.assign(
        site_id=_ids("SITE", config.customers),
        site_name=[f"{fake.city()} Works" for _ in customer_ids],
        remote_site=rng.random(config.customers) < 0.18,
    )[["site_id", "customer_id", "site_name", "region_code", "country_code", "remote_site"]]

    tech_regions = rng.choice(region_names, config.technicians, p=[0.32, 0.17, 0.30, 0.21])
    technicians = pd.DataFrame({
        "technician_id": technician_ids,
        "technician_name": [fake.name() for _ in technician_ids],
        "region_code": tech_regions,
        "skill_level": rng.choice(["junior", "qualified", "senior", "expert"], config.technicians, p=[.15, .45, .3, .1]),
        "weekly_capacity_hours": rng.choice([32, 36, 40], config.technicians, p=[.1, .15, .75]),
    })
    equipment_customer_idx = rng.integers(0, config.customers, config.equipment)
    equipment = pd.DataFrame({
        "equipment_id": equipment_ids,
        "customer_id": [customer_ids[i] for i in equipment_customer_idx],
        "site_id": [f"SITE-{i + 1:06d}" for i in equipment_customer_idx],
        "equipment_type": rng.choice(EQUIPMENT_TYPES, config.equipment, p=[.22, .18, .20, .15, .25]),
        "commissioned_date": pd.Timestamp(config.end_date) - pd.to_timedelta(rng.integers(365, 7300, config.equipment), unit="D"),
    })

    end = pd.Timestamp(config.end_date)
    start = end - pd.DateOffset(months=config.months) + pd.offsets.Day(1)
    span = (end - start).days + 1
    created = start + pd.to_timedelta(rng.integers(0, span, config.orders), unit="D")
    seasonal_weight = np.where(pd.DatetimeIndex(created).month.isin([1, 2, 11, 12]), 1.25, 1.0)
    # Re-sample some winter-biased dates so demand seasonality is visible.
    resample = rng.random(config.orders) < (seasonal_weight - 1) / seasonal_weight
    created = pd.DatetimeIndex(created).to_numpy(copy=True)
    created[resample] = (start + pd.to_timedelta(rng.integers(0, span, resample.sum()), unit="D")).to_numpy()
    equipment_idx = rng.integers(0, config.equipment, config.orders)
    order_regions = equipment.iloc[equipment_idx].merge(customers[["customer_id", "region_code"]], on="customer_id")["region_code"].to_numpy()
    service_type = rng.choice(SERVICE_TYPES, config.orders, p=[.31, .08, .22, .29, .10])
    status = rng.choice(STATUSES, config.orders, p=[.78, .09, .08, .05])
    resolution_hours = rng.lognormal(mean=3.55, sigma=.75, size=config.orders)
    resolution_hours *= np.where(service_type == "repair", 1.5, 1.0)
    resolution_hours *= np.where(order_regions == "APAC", 1.18, 1.0)
    due = pd.to_datetime(created) + pd.to_timedelta(np.where(service_type == "repair", 72, 120), unit="h")
    completed = pd.to_datetime(created) + pd.to_timedelta(resolution_hours, unit="h")
    completed = pd.Series(completed).where(status == "completed", pd.NaT)
    orders = pd.DataFrame({
        "service_order_id": order_ids,
        "customer_id": equipment.iloc[equipment_idx]["customer_id"].to_numpy(),
        "equipment_id": [equipment_ids[i] for i in equipment_idx],
        "technician_id": rng.choice(technician_ids, config.orders),
        "region_code": order_regions,
        "service_type": service_type,
        "status": status,
        "priority": rng.choice(["low", "normal", "high", "critical"], config.orders, p=[.12, .55, .25, .08]),
        "created_at": pd.to_datetime(created),
        "sla_due_at": due,
        "completed_at": pd.to_datetime(completed),
        "budget_cost": np.round(rng.lognormal(8.5, .55, config.orders), 2),
    })
    raw_orders, manifest = inject_order_defects(orders, config, rng)
    clean = {"customers": customers, "sites": sites, "technicians": technicians, "equipment": equipment, "service_orders": orders}
    return clean, raw_orders, manifest


def inject_order_defects(orders: pd.DataFrame, config: GeneratorConfig, rng: np.random.Generator) -> tuple[pd.DataFrame, list[dict]]:
    raw = orders.copy(deep=True)
    manifest: list[dict] = []
    defect_specs = [
        ("missing_technician", "technician_id", None),
        ("unknown_status", "status", "UNKNOWN"),
        ("inconsistent_region", "region_code", "EU-CENTRAL"),
        ("missing_customer", "customer_id", "CUS-999999"),
        ("invalid_completion_date", "completed_at", pd.Timestamp("1990-01-01")),
    ]
    per_type = max(1, round(len(raw) * config.defect_rate / len(defect_specs)))
    available = np.arange(len(raw))
    rng.shuffle(available)
    cursor = 0
    for defect_type, field, value in defect_specs:
        selected = available[cursor:cursor + per_type]
        cursor += per_type
        for idx in selected:
            raw.at[idx, field] = value
            manifest.append({"defect_type": defect_type, "row_index": int(idx), "record_id": raw.at[idx, "service_order_id"], "field": field})
    duplicate_rows = raw.iloc[available[cursor:cursor + per_type]].copy()
    for idx in duplicate_rows.index:
        manifest.append({"defect_type": "duplicate_record", "row_index": int(idx), "record_id": raw.at[idx, "service_order_id"], "field": "service_order_id"})
    raw = pd.concat([raw, duplicate_rows], ignore_index=True)
    return raw, manifest


def write_dataset(output: Path, config: GeneratorConfig) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    clean, raw_orders, manifest = generate(config)
    checksums: dict[str, str] = {}
    for name, frame in {**clean, "raw_service_orders": raw_orders}.items():
        path = output / f"{name}.csv"
        frame.to_csv(path, index=False, date_format="%Y-%m-%dT%H:%M:%S")
        checksums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "defect_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    metadata = {"config": asdict(config), "sha256": checksums, "ground_truth": "service_orders.csv", "raw_feed": "raw_service_orders.csv"}
    (output / "generation_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return checksums


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic FieldOps data")
    parser.add_argument("--output", type=Path, default=Path("data/synthetic"))
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument("--orders", type=int, default=GeneratorConfig.orders)
    args = parser.parse_args()
    write_dataset(args.output, GeneratorConfig(seed=args.seed, orders=args.orders))


if __name__ == "__main__":
    main()
