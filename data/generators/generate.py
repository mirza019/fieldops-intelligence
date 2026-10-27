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

    @classmethod
    def profile(cls, name: str, seed: int = 20261027) -> GeneratorConfig:
        sizes = {
            "small": {"customers": 40, "technicians": 30, "equipment": 150, "orders": 1_000},
            "medium": {"customers": 400, "technicians": 300, "equipment": 1_500, "orders": 25_000},
            "large": {"customers": 800, "technicians": 500, "equipment": 3_000, "orders": 50_000},
        }
        if name not in sizes:
            raise ValueError(f"Unknown profile: {name}")
        return cls(seed=seed, **sizes[name])


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
    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_name": [f"{fake.company()} Industrial" for _ in customer_ids],
            "region_code": customer_regions,
            "country_code": [rng.choice(REGIONS[r]) for r in customer_regions],
        }
    )
    sites = customers.assign(
        site_id=_ids("SITE", config.customers),
        site_name=[f"{fake.city()} Works" for _ in customer_ids],
        remote_site=rng.random(config.customers) < 0.18,
    )[["site_id", "customer_id", "site_name", "region_code", "country_code", "remote_site"]]

    tech_regions = rng.choice(region_names, config.technicians, p=[0.32, 0.17, 0.30, 0.21])
    technicians = pd.DataFrame(
        {
            "technician_id": technician_ids,
            "technician_name": [fake.name() for _ in technician_ids],
            "region_code": tech_regions,
            "skill_level": rng.choice(
                ["junior", "qualified", "senior", "expert"],
                config.technicians,
                p=[0.15, 0.45, 0.3, 0.1],
            ),
            "weekly_capacity_hours": rng.choice(
                [32, 36, 40], config.technicians, p=[0.1, 0.15, 0.75]
            ),
        }
    )
    equipment_customer_idx = rng.integers(0, config.customers, config.equipment)
    equipment = pd.DataFrame(
        {
            "equipment_id": equipment_ids,
            "customer_id": [customer_ids[i] for i in equipment_customer_idx],
            "site_id": [f"SITE-{i + 1:06d}" for i in equipment_customer_idx],
            "equipment_type": rng.choice(
                EQUIPMENT_TYPES, config.equipment, p=[0.22, 0.18, 0.20, 0.15, 0.25]
            ),
            "commissioned_date": pd.Timestamp(config.end_date)
            - pd.to_timedelta(rng.integers(365, 7300, config.equipment), unit="D"),
        }
    )

    end = pd.Timestamp(config.end_date)
    start = end - pd.DateOffset(months=config.months) + pd.offsets.Day(1)
    span = (end - start).days + 1
    created = start + pd.to_timedelta(rng.integers(0, span, config.orders), unit="D")
    seasonal_weight = np.where(pd.DatetimeIndex(created).month.isin([1, 2, 11, 12]), 1.25, 1.0)
    # Re-sample some winter-biased dates so demand seasonality is visible.
    resample = rng.random(config.orders) < (seasonal_weight - 1) / seasonal_weight
    created = pd.DatetimeIndex(created).to_numpy(copy=True)
    created[resample] = (
        start + pd.to_timedelta(rng.integers(0, span, resample.sum()), unit="D")
    ).to_numpy()
    equipment_idx = rng.integers(0, config.equipment, config.orders)
    order_regions = (
        equipment.iloc[equipment_idx]
        .merge(customers[["customer_id", "region_code"]], on="customer_id")["region_code"]
        .to_numpy()
    )
    service_type = rng.choice(SERVICE_TYPES, config.orders, p=[0.31, 0.08, 0.22, 0.29, 0.10])
    status = rng.choice(STATUSES, config.orders, p=[0.78, 0.09, 0.08, 0.05])
    resolution_hours = rng.lognormal(mean=3.55, sigma=0.75, size=config.orders)
    resolution_hours *= np.where(service_type == "repair", 1.5, 1.0)
    resolution_hours *= np.where(order_regions == "APAC", 1.18, 1.0)
    due = pd.to_datetime(created) + pd.to_timedelta(
        np.where(service_type == "repair", 72, 120), unit="h"
    )
    completed = pd.to_datetime(created) + pd.to_timedelta(resolution_hours, unit="h")
    completed = pd.Series(completed).where(status == "completed", pd.NaT)
    orders = pd.DataFrame(
        {
            "service_order_id": order_ids,
            "customer_id": equipment.iloc[equipment_idx]["customer_id"].to_numpy(),
            "equipment_id": [equipment_ids[i] for i in equipment_idx],
            "technician_id": rng.choice(technician_ids, config.orders),
            "region_code": order_regions,
            "service_type": service_type,
            "status": status,
            "priority": rng.choice(
                ["low", "normal", "high", "critical"], config.orders, p=[0.12, 0.55, 0.25, 0.08]
            ),
            "created_at": pd.to_datetime(created),
            "sla_due_at": due,
            "completed_at": pd.to_datetime(completed),
            "budget_cost": np.round(rng.lognormal(8.5, 0.55, config.orders), 2),
        }
    )
    related = generate_related_entities(orders, technicians, equipment, rng)
    raw_orders, manifest = inject_order_defects(orders, config, rng)
    clean = {
        "customers": customers,
        "sites": sites,
        "technicians": technicians,
        "equipment": equipment,
        "service_orders": orders,
        **related,
    }
    return clean, raw_orders, manifest


def generate_related_entities(
    orders: pd.DataFrame,
    technicians: pd.DataFrame,
    equipment: pd.DataFrame,
    rng: np.random.Generator,
) -> dict[str, pd.DataFrame]:
    """Derive visits, time, parts, costs, SLAs and workflow rows from relationships."""
    completed = orders[orders.status == "completed"].reset_index(drop=True)
    complex_order = completed.service_type.eq("repair") | completed.equipment_id.map(
        equipment.set_index("equipment_id").equipment_type
    ).isin(["Gas Turbine", "Steam Turbine"])
    repeat_probability = np.where(complex_order, 0.28, 0.10)
    visit_counts = 1 + (rng.random(len(completed)) < repeat_probability).astype(int)
    visit_order_idx = np.repeat(np.arange(len(completed)), visit_counts)
    visits = completed.iloc[visit_order_idx][
        ["service_order_id", "technician_id", "created_at", "completed_at"]
    ].reset_index(drop=True)
    visits["visit_id"] = _ids("VIS", len(visits))
    visits["sequence_number"] = visits.groupby("service_order_id").cumcount() + 1
    visits["visit_start"] = visits.created_at + pd.to_timedelta(
        rng.integers(8, 72, len(visits)), unit="h"
    )
    visits["duration_hours"] = np.round(rng.uniform(2, 12, len(visits)), 2)
    visits["visit_end"] = visits.visit_start + pd.to_timedelta(visits.duration_hours, unit="h")
    max_sequence = visits.groupby("service_order_id").sequence_number.transform("max")
    visits["successful_fix"] = visits.sequence_number.eq(max_sequence)

    time_entries = visits[
        ["visit_id", "service_order_id", "technician_id", "visit_start", "duration_hours"]
    ].copy()
    time_entries.insert(0, "time_entry_id", _ids("TIM", len(time_entries)))
    time_entries["activity_type"] = "productive_service"
    time_entries["available_hours"] = 8.0
    time_entries["approved"] = True

    has_parts = completed.service_type.eq("repair") & (rng.random(len(completed)) < 0.72)
    part_orders = completed[has_parts].reset_index(drop=True)
    parts = pd.DataFrame(
        {
            "parts_request_id": _ids("PRT", len(part_orders)),
            "service_order_id": part_orders.service_order_id,
            "part_code": rng.choice(
                ["BEARING", "SEAL", "FILTER", "SENSOR", "CONTROL-MODULE"], len(part_orders)
            ),
            "quantity": rng.integers(1, 5, len(part_orders)),
            "requested_at": part_orders.created_at
            + pd.to_timedelta(rng.integers(1, 24, len(part_orders)), unit="h"),
        }
    )
    parts["required_by"] = parts.requested_at + pd.to_timedelta(48, unit="h")
    lead_hours = rng.lognormal(3.4, 0.65, len(parts))
    lead_hours *= np.where(parts.part_code.eq("CONTROL-MODULE"), 1.8, 1.0)
    parts["fulfilled_at"] = parts.requested_at + pd.to_timedelta(lead_hours, unit="h")
    parts["delayed"] = parts.fulfilled_at > parts.required_by

    cost_order_idx = np.repeat(np.arange(len(completed)), 3)
    cost_orders = completed.iloc[cost_order_idx].reset_index(drop=True)
    cost_types = np.tile(["labor", "travel", "materials"], len(completed))
    remote = cost_orders.region_code.isin(["APAC", "AMERICAS"])
    base = np.where(cost_types == "labor", 2800, np.where(cost_types == "travel", 900, 1600))
    base = base * np.where((cost_types == "travel") & remote, 1.65, 1.0)
    costs = pd.DataFrame(
        {
            "cost_transaction_id": _ids("CST", len(cost_orders)),
            "service_order_id": cost_orders.service_order_id,
            "cost_type": cost_types,
            "amount": np.round(base * rng.lognormal(0, 0.35, len(cost_orders)), 2),
            "currency_code": "EUR",
            "transaction_at": cost_orders.completed_at,
            "approved": True,
        }
    )

    sla = orders[["customer_id", "service_type"]].drop_duplicates().reset_index(drop=True)
    sla.insert(0, "sla_contract_id", _ids("SLA", len(sla)))
    sla["resolution_hours"] = np.where(sla.service_type.eq("repair"), 72, 120)
    sla["valid_from"] = orders.created_at.min().normalize()
    sla["valid_to"] = pd.NaT

    case_orders = (
        completed.assign(breached=completed.completed_at > completed.sla_due_at)
        .query("breached")
        .head(max(5, len(completed) // 500))
    )
    cases = pd.DataFrame(
        {
            "case_id": _ids("IMP", len(case_orders)),
            "title": "Improve SLA performance for " + case_orders.region_code.astype(str),
            "related_kpi": "KPI-001",
            "baseline_value": 0.82,
            "target_value": 0.95,
            "dmaic_stage": rng.choice(
                ["define", "measure", "analyze", "improve", "control"], len(case_orders)
            ),
            "status": rng.choice(
                ["open", "approved", "in_progress", "completed"], len(case_orders)
            ),
        }
    )
    actions = cases[["case_id"]].copy()
    actions.insert(0, "action_id", _ids("ACT", len(actions)))
    actions["title"] = "Reduce material and scheduling delay"
    actions["status"] = rng.choice(["open", "in_progress", "completed"], len(actions))
    return {
        "service_visits": visits,
        "time_entries": time_entries,
        "parts_requests": parts,
        "cost_transactions": costs,
        "sla_contracts": sla,
        "improvement_cases": cases,
        "improvement_actions": actions,
    }


def inject_order_defects(
    orders: pd.DataFrame, config: GeneratorConfig, rng: np.random.Generator
) -> tuple[pd.DataFrame, list[dict]]:
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
        selected = available[cursor : cursor + per_type]
        cursor += per_type
        for idx in selected:
            raw.at[idx, field] = value
            manifest.append(
                {
                    "defect_type": defect_type,
                    "row_index": int(idx),
                    "record_id": raw.at[idx, "service_order_id"],
                    "field": field,
                }
            )
    duplicate_rows = raw.iloc[available[cursor : cursor + per_type]].copy()
    for idx in duplicate_rows.index:
        manifest.append(
            {
                "defect_type": "duplicate_record",
                "row_index": int(idx),
                "record_id": raw.at[idx, "service_order_id"],
                "field": "service_order_id",
            }
        )
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
    metadata = {
        "config": asdict(config),
        "sha256": checksums,
        "ground_truth": "service_orders.csv",
        "raw_feed": "raw_service_orders.csv",
    }
    (output / "generation_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return checksums


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic FieldOps data")
    parser.add_argument("--output", type=Path, default=Path("data/synthetic"))
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument("--orders", type=int, default=GeneratorConfig.orders)
    parser.add_argument("--profile", choices=["small", "medium", "large"])
    args = parser.parse_args()
    config = (
        GeneratorConfig.profile(args.profile, args.seed)
        if args.profile
        else GeneratorConfig(seed=args.seed, orders=args.orders)
    )
    write_dataset(args.output, config)


if __name__ == "__main__":
    main()
