from __future__ import annotations

import argparse
import json
from pathlib import Path

from analytics.kpis import calculate_kpis, monthly_performance
from analytics.quality import evaluate_orders
from data.generators.generate import GeneratorConfig, generate


def build(output: Path, profile: str = "small") -> None:
    output.mkdir(parents=True, exist_ok=True)
    clean, raw, manifest = generate(GeneratorConfig.profile(profile))
    clean["monthly_performance"] = monthly_performance(clean["service_orders"])
    clean["quality_results"] = evaluate_orders(
        raw,
        set(clean["customers"].customer_id),
        set(clean["technicians"].technician_id),
    )
    for name, frame in clean.items():
        frame.to_parquet(output / f"{name}.parquet", index=False)
    (output / "kpi_snapshot.json").write_text(json.dumps(calculate_kpis(clean), indent=2) + "\n")
    (output / "defect_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/demo"))
    parser.add_argument("--profile", choices=["small", "medium", "large"], default="small")
    arguments = parser.parse_args()
    build(arguments.output, arguments.profile)
