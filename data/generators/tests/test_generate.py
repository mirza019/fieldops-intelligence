from pathlib import Path

from data.generators.generate import GeneratorConfig, generate, write_dataset


def test_generation_is_reproducible(tmp_path: Path) -> None:
    config = GeneratorConfig(customers=12, technicians=10, equipment=30, orders=200)
    first = write_dataset(tmp_path / "first", config)
    second = write_dataset(tmp_path / "second", config)
    assert first == second


def test_references_and_ground_truth_are_valid() -> None:
    config = GeneratorConfig(customers=12, technicians=10, equipment=30, orders=200)
    clean, _, _ = generate(config)
    orders = clean["service_orders"]
    assert set(orders.customer_id) <= set(clean["customers"].customer_id)
    assert set(orders.equipment_id) <= set(clean["equipment"].equipment_id)
    assert set(orders.technician_id) <= set(clean["technicians"].technician_id)
    completed = orders[orders.status == "completed"]
    assert completed.completed_at.notna().all()


def test_defect_manifest_matches_corruption() -> None:
    config = GeneratorConfig(customers=12, technicians=10, equipment=30, orders=500, defect_rate=.06)
    clean, raw, manifest = generate(config)
    types = {item["defect_type"] for item in manifest}
    assert types == {"missing_technician", "unknown_status", "inconsistent_region", "missing_customer", "invalid_completion_date", "duplicate_record"}
    assert len(raw) > len(clean["service_orders"])
    assert raw.technician_id.isna().any()
    assert "UNKNOWN" in set(raw.status)

