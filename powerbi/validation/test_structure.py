from scripts.validate_powerbi import validate


def test_powerbi_structure() -> None:
    assert len(validate()) == 7
