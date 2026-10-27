from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class KPI:
    id: str
    name: str
    unit: str
    target: float
    better: str


KPI_CATALOG: Mapping[str, KPI] = {
    "KPI-001": KPI("KPI-001", "SLA Compliance Rate", "%", 0.95, "higher"),
    "KPI-002": KPI("KPI-002", "First-Time Fix Rate", "%", 0.85, "higher"),
    "KPI-003": KPI("KPI-003", "Technician Utilization", "%", 0.80, "higher"),
    "KPI-004": KPI("KPI-004", "Average Resolution Time", "hours", 72.0, "lower"),
    "KPI-005": KPI("KPI-005", "Service Order Backlog", "orders", 500.0, "lower"),
    "KPI-008": KPI("KPI-008", "Average Service Cost", "EUR/order", 8000.0, "lower"),
}


def safe_divide(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else float(numerator / denominator)


def calculate_kpis(tables: Mapping[str, pd.DataFrame]) -> dict[str, float | None]:
    orders = tables["service_orders"].copy()
    visits = tables["service_visits"]
    time = tables["time_entries"]
    costs = tables["cost_transactions"]
    completed = orders[orders.status.eq("completed") & orders.completed_at.notna()]
    eligible_sla = completed[completed.sla_due_at.notna()]
    sla = safe_divide(
        (eligible_sla.completed_at <= eligible_sla.sla_due_at).sum(), len(eligible_sla)
    )
    counts = visits.groupby("service_order_id").size()
    eligible_ftf = completed.service_order_id.isin(counts.index)
    ftf = safe_divide(
        completed.loc[eligible_ftf, "service_order_id"].map(counts).eq(1).sum(), eligible_ftf.sum()
    )
    productive = time.loc[time.approved, "duration_hours"].sum()
    available = time.loc[time.approved, "available_hours"].sum()
    resolution = (completed.completed_at - completed.created_at).dt.total_seconds().div(3600).mean()
    backlog = orders.status.isin(["in_progress", "scheduled"]).sum()
    approved_cost = costs[costs.approved].groupby("service_order_id").amount.sum()
    average_cost = approved_cost.mean() if len(approved_cost) else None
    return {
        "KPI-001": sla,
        "KPI-002": ftf,
        "KPI-003": safe_divide(productive, available),
        "KPI-004": None if pd.isna(resolution) else float(resolution),
        "KPI-005": float(backlog),
        "KPI-008": None if average_cost is None else float(average_cost),
    }


def monthly_performance(orders: pd.DataFrame) -> pd.DataFrame:
    completed = orders[orders.status.eq("completed") & orders.completed_at.notna()].copy()
    completed["month"] = completed.completed_at.dt.to_period("M").dt.to_timestamp()
    completed["sla_compliant"] = completed.completed_at <= completed.sla_due_at
    return (
        completed.groupby("month", as_index=False)
        .agg(
            service_orders=("service_order_id", "nunique"),
            sla_compliance=("sla_compliant", "mean"),
            average_resolution_hours=("completed_at", lambda x: 0.0),
        )
        .assign(
            average_resolution_hours=lambda frame: (
                completed.groupby("month")
                .apply(
                    lambda group: (
                        (group.completed_at - group.created_at).dt.total_seconds().mean() / 3600
                    ),
                    include_groups=False,
                )
                .to_numpy()
            )
        )
    )
