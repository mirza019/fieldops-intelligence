from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from backend.app.models import SCHEMAS, metadata


def test_schema_inventory() -> None:
    counts = {
        schema: sum(t.schema == schema for t in metadata.tables.values()) for schema in SCHEMAS
    }
    assert counts == {
        "ops": 11,
        "staging": 4,
        "mart": 15,
        "governance": 5,
        "workflow": 4,
        "platform": 4,
    }
    assert len(metadata.tables) == 43


def test_all_tables_have_primary_keys_and_purposes() -> None:
    for relation in metadata.tables.values():
        assert relation.primary_key.columns, relation.fullname
        assert relation.comment, relation.fullname


def test_postgresql_ddl_compiles() -> None:
    ddl = "\n".join(
        str(CreateTable(t).compile(dialect=postgresql.dialect())) for t in metadata.sorted_tables
    )
    assert "NUMERIC(18, 2)" in ddl
    assert "TIMESTAMP WITH TIME ZONE" in ddl
    assert "REFERENCES ops.customers" in ddl
    assert "REFERENCES ops.service_visits" in ddl
