"""Authoritative six-schema PostgreSQL model."""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

SCHEMAS = ("ops", "staging", "mart", "governance", "workflow", "platform")
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


def uid():
    return Column(
        "id", UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )


def stamps():
    return (
        Column(
            "created_at",
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        Column(
            "updated_at",
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )


def tbl(schema, name, *cols, purpose):
    return Table(name, metadata, *cols, schema=schema, comment=purpose)


def fk(name, target, nullable=False):
    return Column(name, UUID(as_uuid=True), ForeignKey(target), nullable=nullable)


# ops: current source-aligned operational state
customers = tbl(
    "ops",
    "customers",
    uid(),
    Column("customer_code", String(32), nullable=False, unique=True),
    Column("name", String(200), nullable=False),
    Column("region_code", String(20), nullable=False),
    Column("country_code", String(2), nullable=False),
    Column("source_updated_at", DateTime(timezone=True), nullable=False),
    *stamps(),
    purpose="One fictional industrial customer.",
)
sites = tbl(
    "ops",
    "sites",
    uid(),
    Column("site_code", String(32), nullable=False, unique=True),
    fk("customer_id", "ops.customers.id"),
    Column("name", String(200), nullable=False),
    Column("country_code", String(2), nullable=False),
    Column("is_remote", Boolean, nullable=False, server_default=text("false")),
    *stamps(),
    purpose="One physical customer site.",
)
equipment = tbl(
    "ops",
    "equipment",
    uid(),
    Column("equipment_code", String(32), nullable=False, unique=True),
    fk("site_id", "ops.sites.id"),
    Column("equipment_type", String(50), nullable=False),
    Column("commissioned_date", Date),
    Column("criticality", String(20), nullable=False),
    *stamps(),
    CheckConstraint(
        "criticality IN ('low','medium','high','critical')", name="equipment_criticality"
    ),
    purpose="One maintainable asset at a site.",
)
technicians = tbl(
    "ops",
    "technicians",
    uid(),
    Column("technician_code", String(32), nullable=False, unique=True),
    Column("display_name", String(160), nullable=False),
    Column("region_code", String(20), nullable=False),
    Column("skill_level", String(20), nullable=False),
    Column("weekly_capacity_hours", Numeric(5, 2), nullable=False),
    Column("active", Boolean, nullable=False, server_default=text("true")),
    *stamps(),
    CheckConstraint("weekly_capacity_hours >= 0", name="technician_capacity"),
    purpose="One field-service technician.",
)
sla_contracts = tbl(
    "ops",
    "sla_contracts",
    uid(),
    Column("sla_code", String(32), nullable=False),
    fk("customer_id", "ops.customers.id"),
    Column("service_type", String(40), nullable=False),
    Column("response_hours", Integer, nullable=False),
    Column("resolution_hours", Integer, nullable=False),
    Column("valid_from", Date, nullable=False),
    Column("valid_to", Date),
    *stamps(),
    UniqueConstraint("sla_code", "valid_from"),
    CheckConstraint("response_hours > 0 AND resolution_hours > 0", name="sla_positive_hours"),
    purpose="One effective-dated customer SLA version.",
)
service_orders = tbl(
    "ops",
    "service_orders",
    uid(),
    Column("order_code", String(32), nullable=False, unique=True),
    fk("equipment_id", "ops.equipment.id"),
    fk("sla_contract_id", "ops.sla_contracts.id", True),
    Column("service_type", String(40), nullable=False),
    Column("status", String(30), nullable=False),
    Column("priority", String(20), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("planned_completion_at", DateTime(timezone=True)),
    Column("sla_due_at", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("budget_amount", Numeric(18, 2)),
    Column("currency_code", String(3)),
    Column("source_updated_at", DateTime(timezone=True), nullable=False),
    Column("content_hash", String(64), nullable=False),
    *stamps(),
    CheckConstraint("budget_amount IS NULL OR budget_amount >= 0", name="order_budget_nonnegative"),
    purpose="One service order at current source state.",
)
service_visits = tbl(
    "ops",
    "service_visits",
    uid(),
    Column("visit_code", String(40), nullable=False, unique=True),
    fk("service_order_id", "ops.service_orders.id"),
    Column("sequence_number", Integer, nullable=False),
    Column("status", String(30), nullable=False),
    Column("scheduled_start", DateTime(timezone=True)),
    Column("actual_start", DateTime(timezone=True)),
    Column("actual_end", DateTime(timezone=True)),
    Column("successful_fix", Boolean),
    *stamps(),
    UniqueConstraint("service_order_id", "sequence_number"),
    CheckConstraint("sequence_number > 0", name="visit_sequence_positive"),
    purpose="One planned or performed visit for an order.",
)
visit_technicians = tbl(
    "ops",
    "visit_technicians",
    Column("visit_id", UUID(as_uuid=True), ForeignKey("ops.service_visits.id"), primary_key=True),
    Column("technician_id", UUID(as_uuid=True), ForeignKey("ops.technicians.id"), primary_key=True),
    Column("assignment_role", String(30), nullable=False, server_default="primary"),
    Column(
        "assigned_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    purpose="One technician assignment to one visit.",
)
time_entries = tbl(
    "ops",
    "time_entries",
    uid(),
    Column("entry_code", String(40), nullable=False, unique=True),
    fk("visit_id", "ops.service_visits.id"),
    fk("technician_id", "ops.technicians.id"),
    Column("activity_type", String(40), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("ended_at", DateTime(timezone=True), nullable=False),
    Column("duration_hours", Numeric(8, 2), nullable=False),
    Column("approved", Boolean, nullable=False, server_default=text("false")),
    *stamps(),
    CheckConstraint("duration_hours >= 0", name="time_duration_nonnegative"),
    purpose="One technician activity interval on a visit.",
)
parts_requests = tbl(
    "ops",
    "parts_requests",
    uid(),
    Column("request_code", String(40), nullable=False, unique=True),
    fk("service_order_id", "ops.service_orders.id"),
    Column("part_code", String(50), nullable=False),
    Column("quantity", Numeric(12, 3), nullable=False),
    Column("requested_at", DateTime(timezone=True), nullable=False),
    Column("required_by", DateTime(timezone=True)),
    Column("fulfilled_at", DateTime(timezone=True)),
    Column("status", String(30), nullable=False),
    *stamps(),
    CheckConstraint("quantity > 0", name="part_quantity_positive"),
    purpose="One spare-part line requested for an order.",
)
cost_transactions = tbl(
    "ops",
    "cost_transactions",
    uid(),
    Column("transaction_code", String(40), nullable=False, unique=True),
    fk("service_order_id", "ops.service_orders.id"),
    fk("visit_id", "ops.service_visits.id", True),
    Column("cost_type", String(30), nullable=False),
    Column("amount", Numeric(18, 2), nullable=False),
    Column("currency_code", String(3), nullable=False),
    Column("transaction_at", DateTime(timezone=True), nullable=False),
    Column("approved", Boolean, nullable=False, server_default=text("false")),
    *stamps(),
    CheckConstraint("amount >= 0", name="cost_amount_nonnegative"),
    purpose="One service-related financial transaction.",
)

# staging: immutable ingestion envelopes and record outcomes
ingestion_batches = tbl(
    "staging",
    "ingestion_batches",
    uid(),
    Column("source_name", String(80), nullable=False),
    Column("status", String(30), nullable=False),
    Column("source_watermark", DateTime(timezone=True)),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("record_count", Integer, nullable=False, server_default="0"),
    Column("content_hash", String(64)),
    purpose="One registered source ingestion batch.",
)
raw_records = tbl(
    "staging",
    "raw_records",
    uid(),
    fk("batch_id", "staging.ingestion_batches.id"),
    Column("dataset", String(80), nullable=False),
    Column("business_key", String(120), nullable=False),
    Column("source_updated_at", DateTime(timezone=True)),
    Column("content_hash", String(64), nullable=False),
    Column("payload", JSON, nullable=False),
    Column(
        "ingested_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint("batch_id", "dataset", "business_key", "content_hash"),
    purpose="One immutable raw source record version.",
)
validated_records = tbl(
    "staging",
    "validated_records",
    uid(),
    fk("raw_record_id", "staging.raw_records.id"),
    Column("validated_payload", JSON, nullable=False),
    Column(
        "validated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint("raw_record_id"),
    purpose="One accepted normalized raw record.",
)
quarantined_records = tbl(
    "staging",
    "quarantined_records",
    uid(),
    fk("raw_record_id", "staging.raw_records.id"),
    Column("rule_id", String(50), nullable=False),
    Column("severity", String(20), nullable=False),
    Column("field_name", String(120)),
    Column("reason", Text, nullable=False),
    Column("status", String(20), nullable=False, server_default="open"),
    Column(
        "detected_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    purpose="One rule failure affecting one raw record.",
)

# mart: conformed dimensions
dim_date = tbl(
    "mart",
    "dim_date",
    Column("date_key", Integer, primary_key=True),
    Column("full_date", Date, nullable=False, unique=True),
    Column("year", Integer, nullable=False),
    Column("quarter", Integer, nullable=False),
    Column("month", Integer, nullable=False),
    Column("month_name", String(12), nullable=False),
    Column("week_of_year", Integer, nullable=False),
    Column("day_of_week", Integer, nullable=False),
    Column("is_weekend", Boolean, nullable=False),
    purpose="One calendar date.",
)


def scd(name, bk, *attrs, purpose):
    key = f"{name.removeprefix('dim_')}_key"
    return tbl(
        "mart",
        name,
        Column(key, Integer, primary_key=True, autoincrement=True),
        Column(bk, String(40), nullable=False),
        *attrs,
        Column("effective_from", DateTime(timezone=True), nullable=False),
        Column("effective_to", DateTime(timezone=True)),
        Column("is_current", Boolean, nullable=False, server_default=text("true")),
        UniqueConstraint(bk, "effective_from"),
        purpose=purpose,
    )


dim_customer = scd(
    "dim_customer",
    "customer_code",
    Column("customer_name", String(200), nullable=False),
    Column("region_code", String(20), nullable=False),
    Column("country_code", String(2), nullable=False),
    purpose="One effective-dated customer version.",
)
dim_region = tbl(
    "mart",
    "dim_region",
    Column("region_key", Integer, primary_key=True),
    Column("region_code", String(20), nullable=False, unique=True),
    Column("region_name", String(100), nullable=False),
    purpose="One governed reporting region.",
)
dim_technician = scd(
    "dim_technician",
    "technician_code",
    Column("display_name", String(160), nullable=False),
    Column("region_code", String(20), nullable=False),
    Column("skill_level", String(20), nullable=False),
    purpose="One effective-dated technician version.",
)
dim_equipment = scd(
    "dim_equipment",
    "equipment_code",
    Column("equipment_type", String(50), nullable=False),
    Column("criticality", String(20), nullable=False),
    Column("site_code", String(32), nullable=False),
    purpose="One effective-dated equipment version.",
)
dim_service_type = tbl(
    "mart",
    "dim_service_type",
    Column("service_type_key", Integer, primary_key=True),
    Column("service_type_code", String(40), nullable=False, unique=True),
    Column("service_type_name", String(100), nullable=False),
    Column("productive", Boolean, nullable=False),
    purpose="One governed service type.",
)
dim_status = tbl(
    "mart",
    "dim_status",
    Column("status_key", Integer, primary_key=True),
    Column("status_code", String(30), nullable=False, unique=True),
    Column("status_name", String(100), nullable=False),
    Column("terminal", Boolean, nullable=False),
    purpose="One governed service status.",
)
dim_sla = scd(
    "dim_sla",
    "sla_code",
    Column("response_hours", Integer, nullable=False),
    Column("resolution_hours", Integer, nullable=False),
    purpose="One effective-dated SLA version.",
)


def ikey(name):
    return Column(name, Integer, primary_key=True, autoincrement=True)


def ifk(name, target, nullable=False):
    return Column(name, Integer, ForeignKey(target), nullable=nullable)


run_id = lambda: Column("pipeline_run_id", UUID(as_uuid=True), nullable=False)
fact_service_order = tbl(
    "mart",
    "fact_service_order",
    ikey("service_order_key"),
    Column("order_code", String(32), nullable=False, unique=True),
    ifk("customer_key", "mart.dim_customer.customer_key"),
    ifk("region_key", "mart.dim_region.region_key"),
    ifk("equipment_key", "mart.dim_equipment.equipment_key"),
    ifk("service_type_key", "mart.dim_service_type.service_type_key"),
    ifk("status_key", "mart.dim_status.status_key"),
    ifk("sla_key", "mart.dim_sla.sla_key", True),
    ifk("accepted_date_key", "mart.dim_date.date_key"),
    ifk("completed_date_key", "mart.dim_date.date_key", True),
    ifk("sla_due_date_key", "mart.dim_date.date_key", True),
    Column("resolution_hours", Numeric(12, 2)),
    Column("budget_amount", Numeric(18, 2)),
    Column("reporting_currency", String(3)),
    Column("sla_compliant", Boolean),
    Column("is_backlog", Boolean, nullable=False),
    run_id(),
    purpose="One current analytical service order.",
)
fact_service_visit = tbl(
    "mart",
    "fact_service_visit",
    ikey("service_visit_key"),
    Column("visit_code", String(40), nullable=False, unique=True),
    ifk("service_order_key", "mart.fact_service_order.service_order_key"),
    ifk("visit_date_key", "mart.dim_date.date_key", True),
    Column("sequence_number", Integer, nullable=False),
    Column("successful_fix", Boolean),
    Column("duration_hours", Numeric(10, 2)),
    run_id(),
    purpose="One service visit.",
)
fact_technician_time = tbl(
    "mart",
    "fact_technician_time",
    ikey("technician_time_key"),
    Column("entry_code", String(40), nullable=False, unique=True),
    ifk("technician_key", "mart.dim_technician.technician_key"),
    ifk("date_key", "mart.dim_date.date_key"),
    ifk("service_visit_key", "mart.fact_service_visit.service_visit_key", True),
    Column("productive_hours", Numeric(8, 2), nullable=False, server_default="0"),
    Column("available_hours", Numeric(8, 2), nullable=False, server_default="0"),
    run_id(),
    purpose="One technician time entry.",
)
fact_service_cost = tbl(
    "mart",
    "fact_service_cost",
    ikey("service_cost_key"),
    Column("transaction_code", String(40), nullable=False, unique=True),
    ifk("service_order_key", "mart.fact_service_order.service_order_key"),
    ifk("date_key", "mart.dim_date.date_key"),
    Column("cost_type", String(30), nullable=False),
    Column("amount_reporting", Numeric(18, 2), nullable=False),
    Column("reporting_currency", String(3), nullable=False),
    run_id(),
    purpose="One approved cost transaction in reporting currency.",
)
fact_parts_fulfillment = tbl(
    "mart",
    "fact_parts_fulfillment",
    ikey("parts_fulfillment_key"),
    Column("request_code", String(40), nullable=False, unique=True),
    ifk("service_order_key", "mart.fact_service_order.service_order_key"),
    ifk("requested_date_key", "mart.dim_date.date_key"),
    ifk("fulfilled_date_key", "mart.dim_date.date_key", True),
    Column("quantity", Numeric(12, 3), nullable=False),
    Column("lead_time_hours", Numeric(12, 2)),
    Column("delayed", Boolean),
    run_id(),
    purpose="One requested spare-part line.",
)
fact_sla_event = tbl(
    "mart",
    "fact_sla_event",
    ikey("sla_event_key"),
    ifk("service_order_key", "mart.fact_service_order.service_order_key"),
    ifk("date_key", "mart.dim_date.date_key"),
    Column("event_type", String(40), nullable=False),
    Column("event_at", DateTime(timezone=True), nullable=False),
    Column("within_sla", Boolean),
    run_id(),
    UniqueConstraint("service_order_key", "event_type", "event_at"),
    purpose="One SLA milestone event for an order.",
)
fact_data_quality = tbl(
    "mart",
    "fact_data_quality",
    ikey("data_quality_key"),
    ifk("date_key", "mart.dim_date.date_key"),
    Column("rule_id", String(50), nullable=False),
    Column("dataset", String(80), nullable=False),
    Column("applicable_count", Integer, nullable=False),
    Column("passed_count", Integer, nullable=False),
    Column("failed_count", Integer, nullable=False),
    run_id(),
    CheckConstraint(
        "applicable_count = passed_count + failed_count", name="quality_count_reconciles"
    ),
    purpose="One aggregate rule result per dataset and run.",
)

# governance
kpi_definitions = tbl(
    "governance",
    "kpi_definitions",
    uid(),
    Column("kpi_code", String(20), nullable=False),
    Column("version", Integer, nullable=False),
    Column("name", String(160), nullable=False),
    Column("definition", Text, nullable=False),
    Column("formula", Text, nullable=False),
    Column("unit", String(30), nullable=False),
    Column("owner", String(120), nullable=False),
    Column("effective_from", DateTime(timezone=True), nullable=False),
    Column("effective_to", DateTime(timezone=True)),
    UniqueConstraint("kpi_code", "version"),
    purpose="One governed KPI definition version.",
)
kpi_targets = tbl(
    "governance",
    "kpi_targets",
    uid(),
    fk("kpi_definition_id", "governance.kpi_definitions.id"),
    Column("scope", JSON, nullable=False),
    Column("target_value", Numeric(18, 4), nullable=False),
    Column("warning_value", Numeric(18, 4)),
    Column("effective_from", DateTime(timezone=True), nullable=False),
    Column("effective_to", DateTime(timezone=True)),
    purpose="One effective KPI target for a filter scope.",
)
quality_rules = tbl(
    "governance",
    "quality_rules",
    uid(),
    Column("rule_code", String(50), nullable=False),
    Column("version", Integer, nullable=False),
    Column("name", String(160), nullable=False),
    Column("dataset", String(80), nullable=False),
    Column("target_field", String(120)),
    Column("quality_dimension", String(40), nullable=False),
    Column("severity", String(20), nullable=False),
    Column("configuration", JSON, nullable=False),
    Column("owner", String(120), nullable=False),
    Column("active", Boolean, nullable=False),
    UniqueConstraint("rule_code", "version"),
    purpose="One versioned executable quality rule.",
)
quality_results = tbl(
    "governance",
    "quality_results",
    uid(),
    fk("quality_rule_id", "governance.quality_rules.id"),
    Column("pipeline_run_id", UUID(as_uuid=True), nullable=False),
    Column("applicable_count", Integer, nullable=False),
    Column("passed_count", Integer, nullable=False),
    Column("failed_count", Integer, nullable=False),
    Column("executed_at", DateTime(timezone=True), nullable=False),
    Column("details", JSON),
    purpose="One quality-rule execution result.",
)
data_lineage = tbl(
    "governance",
    "data_lineage",
    uid(),
    Column("source_asset", String(200), nullable=False),
    Column("source_field", String(120)),
    Column("target_asset", String(200), nullable=False),
    Column("target_field", String(120)),
    Column("transformation", Text, nullable=False),
    Column("kpi_code", String(20)),
    Column("report_artifact", String(200)),
    purpose="One source-to-target lineage edge.",
)

# workflow
improvement_cases = tbl(
    "workflow",
    "improvement_cases",
    uid(),
    Column("case_code", String(32), nullable=False, unique=True),
    Column("title", String(200), nullable=False),
    Column("description", Text, nullable=False),
    Column("kpi_code", String(20), nullable=False),
    Column("baseline_value", Numeric(18, 4)),
    Column("target_value", Numeric(18, 4)),
    Column("priority", String(20), nullable=False),
    Column("dmaic_stage", String(20), nullable=False),
    Column("status", String(30), nullable=False),
    Column("owner_user_id", UUID(as_uuid=True)),
    Column("deadline", Date),
    *stamps(),
    purpose="One governed continuous-improvement case.",
)
improvement_actions = tbl(
    "workflow",
    "improvement_actions",
    uid(),
    fk("case_id", "workflow.improvement_cases.id"),
    Column("title", String(200), nullable=False),
    Column("owner_user_id", UUID(as_uuid=True)),
    Column("due_date", Date),
    Column("status", String(30), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    *stamps(),
    purpose="One corrective action in a case.",
)
approvals = tbl(
    "workflow",
    "approvals",
    uid(),
    fk("case_id", "workflow.improvement_cases.id"),
    Column("approver_user_id", UUID(as_uuid=True), nullable=False),
    Column("decision", String(20), nullable=False),
    Column("comment", Text),
    Column("decided_at", DateTime(timezone=True), nullable=False),
    purpose="One human approval decision.",
)
alerts = tbl(
    "workflow",
    "alerts",
    uid(),
    Column("alert_code", String(40), nullable=False, unique=True),
    Column("rule_code", String(50), nullable=False),
    Column("actual_value", Numeric(18, 4)),
    Column("threshold_value", Numeric(18, 4)),
    Column("affected_period", String(30), nullable=False),
    Column("severity", String(20), nullable=False),
    Column("evidence", JSON, nullable=False),
    Column("status", String(20), nullable=False),
    Column("owner_user_id", UUID(as_uuid=True)),
    *stamps(),
    purpose="One threshold or quality alert.",
)

# platform
roles = tbl(
    "platform",
    "roles",
    uid(),
    Column("role_code", String(40), nullable=False, unique=True),
    Column("name", String(100), nullable=False),
    Column("permissions", JSON, nullable=False),
    purpose="One application authorization role.",
)
users = tbl(
    "platform",
    "users",
    uid(),
    Column("email", String(254), nullable=False, unique=True),
    Column("display_name", String(160), nullable=False),
    Column("password_hash", String(255)),
    fk("role_id", "platform.roles.id"),
    Column("active", Boolean, nullable=False, server_default=text("true")),
    *stamps(),
    purpose="One local or federated application user.",
)
pipeline_runs = tbl(
    "platform",
    "pipeline_runs",
    uid(),
    fk("batch_id", "staging.ingestion_batches.id", True),
    Column("status", String(30), nullable=False),
    Column("trigger_type", String(20), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("checkpoint", String(80)),
    Column("processed_rows", Integer, nullable=False, server_default="0"),
    Column("failed_rows", Integer, nullable=False, server_default="0"),
    Column("error_summary", Text),
    purpose="One orchestrated pipeline execution.",
)
audit_events = tbl(
    "platform",
    "audit_events",
    uid(),
    fk("actor_user_id", "platform.users.id", True),
    Column("event_type", String(80), nullable=False),
    Column("entity_type", String(80), nullable=False),
    Column("entity_id", String(80)),
    Column(
        "occurred_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column("details", JSON, nullable=False),
    purpose="One immutable security or business audit event.",
)

for relation, names in {
    sites: ("customer_id",),
    equipment: ("site_id",),
    service_orders: ("equipment_id", "accepted_at", "status"),
    service_visits: ("service_order_id", "actual_start"),
    time_entries: ("visit_id", "technician_id", "started_at"),
    parts_requests: ("service_order_id", "requested_at"),
    cost_transactions: ("service_order_id", "transaction_at"),
    raw_records: ("batch_id", "business_key"),
    quarantined_records: ("raw_record_id", "status"),
}.items():
    for name in names:
        Index(f"ix_{relation.schema}_{relation.name}_{name}", relation.c[name])
