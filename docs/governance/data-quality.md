# Data quality governance

Each active rule has an ID, name, description, dataset, target field, dimension, severity, owner, executable configuration, and run statistics. Initial rules cover required identifiers, unique source keys, allowed statuses/regions, nonnegative costs, chronological dates, existing references, and freshness.

For a rule, `pass_rate = passed applicable checks / applicable checks`. A dimension score is the applicable-check-weighted pass rate of its active rules. The overall score is `sum(passed applicable checks) / sum(applicable checks) * 100`; informational rules and non-applicable checks are excluded. Severity changes triage, not the mathematics, preventing arbitrary weighting.

Rejected records retain the source batch, record key, rule/version, offending field/value (redacted when sensitive), reason, detection time, owner, status, and resolution history. Critical structural failures stop publishing; record-level failures are quarantined while valid rows continue according to dataset policy.

Lineage metadata links source dataset and column to validation rules, validated fields, warehouse columns, KPI IDs, DAX measures, and report visuals.

