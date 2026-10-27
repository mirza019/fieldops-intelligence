from __future__ import annotations

from analytics.kpis import KPI_CATALOG


def mock_answer(question: str, values: dict[str, float | None]) -> dict:
    below = []
    for code, value in values.items():
        if value is None or code not in KPI_CATALOG:
            continue
        kpi = KPI_CATALOG[code]
        unfavorable = value < kpi.target if kpi.better == "higher" else value > kpi.target
        if unfavorable:
            below.append(
                f"{kpi.name} ({value:.1%} vs {kpi.target:.1%})"
                if kpi.unit == "%"
                else f"{kpi.name} ({value:.1f} vs {kpi.target:.1f})"
            )
    observation = "Below-target metrics: " + (
        ", ".join(below) if below else "none in the current snapshot"
    )
    return {
        "provider": "deterministic mock",
        "question": question,
        "observation": observation,
        "hypothesis": "Regional capacity, repeat visits, and part lead times should be investigated; this is a hypothesis, not a causal claim.",
        "recommendation": "Review the regional and delay Pareto views, then create a manager-approved DMAIC case for the largest verified contributor.",
        "evidence": [{"kpi_id": code, "value": value} for code, value in values.items()],
    }
