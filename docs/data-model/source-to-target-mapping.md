# Source-to-target mapping

This mapping is the initial analytical contract. All accepted source values pass configured staging validation before dimensional loading. Critical failures are quarantined and excluded; nullable analytical outcomes remain null rather than being coerced to favorable values.

| Source | Target | Transformation and business rule | Null / validation | History |
|---|---|---|---|---|
| `ops.customers.customer_code` | `mart.dim_customer.customer_code` | Stable business key | Required and unique | SCD2 |
| `ops.customers.name` | `mart.dim_customer.customer_name` | Trim and normalize Unicode | Required | SCD2 on change |
| `ops.customers.region_code` | `mart.dim_customer.region_code` | Map governed region code | Reject unknown code | SCD2 on change |
| `ops.equipment.equipment_code` | `mart.dim_equipment.equipment_code` | Stable business key | Required and unique | SCD2 |
| `ops.service_orders.order_code` | `mart.fact_service_order.order_code` | Stable fact business key | Required and unique | Upsert only when content hash changes |
| `ops.service_orders.accepted_at` | `mart.fact_service_order.accepted_date_key` | Convert UTC date to `YYYYMMDD` key | Required; valid date | Current fact version |
| `ops.service_orders.completed_at` | `mart.fact_service_order.completed_date_key` | Convert UTC completion date to key | Null unless completed; must be >= accepted | Current fact version |
| accepted/completed timestamps | `mart.fact_service_order.resolution_hours` | `(completed_at-accepted_at)` in decimal hours | Null for unresolved; reject negative | Recomputed on changed order |
| completion and SLA due timestamps | `mart.fact_service_order.sla_compliant` | Completed, eligible, valid SLA, completion <= due | Null if ineligible/missing SLA | Recomputed on changed order |
| `ops.service_visits.*` | `mart.fact_service_visit.*` | One row per visit; preserve sequence and successful fix | Order reference required | Insert/update by visit code |
| approved `ops.time_entries.duration_hours` | `mart.fact_technician_time.productive_hours` | Sum only allowlisted productive activity entries at reporting grain | Nonnegative; technician/visit required | Insert/update by entry code |
| workforce calendar | `mart.fact_technician_time.available_hours` | Scheduled hours less leave, holiday, training | Nonnegative; zero is valid | Snapshot per time record/date |
| approved `ops.cost_transactions.amount` | `mart.fact_service_cost.amount_reporting` | Convert using governed rate for transaction date | Currency required; nonnegative; missing rate stops row | Immutable transaction/upsert correction |
| `ops.parts_requests` timestamps | `mart.fact_parts_fulfillment.lead_time_hours` | fulfilled minus requested | Null until fulfilled; reject negative | Update on fulfillment |
| staging quality results | `mart.fact_data_quality` | Aggregate applicable/passed/failed by rule, dataset, run | Counts reconcile exactly | Append per run |

## Worked examples

**Service-order completion:** `SO-000123` accepted at 08:00 UTC and completed at 20:00 UTC maps to 12.00 resolution hours and the completion date key. A completion earlier than acceptance is quarantined.

**SLA compliance:** an eligible completed order due at 18:00 and completed at 17:30 has `sla_compliant=true`. Missing contracts or unresolved orders produce null and do not enter the compliance denominator.

**Technician utilization:** approved productive hours are divided by scheduled hours minus leave, holiday, and training. If available hours are zero, the KPI is null.

**Service costs:** an approved EUR 1,000 transaction uses the governed transaction-date exchange rate. Its original amount/currency remain in `ops`; the reporting value and currency enter `mart.fact_service_cost`.

