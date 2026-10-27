from __future__ import annotations


def simulate(
    baseline: dict[str, float],
    technicians_pct: float,
    demand_pct: float,
    parts_pct: float,
    scheduling_pct: float,
    travel_pct: float,
    cost_pct: float,
) -> dict[str, float]:
    capacity_ratio = (
        (1 + technicians_pct / 100) * (1 + scheduling_pct / 200) / max(0.1, 1 + demand_pct / 100)
    )
    return {
        "SLA compliance": min(
            0.995, max(0.0, baseline["sla"] + 0.12 * (capacity_ratio - 1) - 0.06 * parts_pct / 100)
        ),
        "Backlog": max(0.0, baseline["backlog"] / capacity_ratio),
        "Utilization": min(1.2, max(0.0, baseline["utilization"] / capacity_ratio)),
        "Resolution hours": max(
            1.0, baseline["resolution"] / capacity_ratio * (1 + parts_pct / 250)
        ),
        "Cost per order": max(
            0.0, baseline["cost"] * (1 + cost_pct / 100) * (1 + travel_pct / 500)
        ),
    }
