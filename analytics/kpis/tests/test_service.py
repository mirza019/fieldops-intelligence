from analytics.kpis import calculate_kpis
from data.generators.generate import GeneratorConfig, generate


def test_kpis_are_grounded_and_bounded() -> None:
    clean, _, _ = generate(GeneratorConfig(customers=20, technicians=15, equipment=50, orders=500))
    values = calculate_kpis(clean)
    assert 0 <= values["KPI-001"] <= 1
    assert 0 <= values["KPI-002"] <= 1
    assert 0 <= values["KPI-003"] <= 2
    assert values["KPI-004"] > 0
    assert values["KPI-005"] >= 0
    assert values["KPI-008"] > 0
