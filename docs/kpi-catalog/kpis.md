# Governed KPI catalog — version 1.0

Common exclusions: cancelled/test orders and records quarantined by critical rules. Rates return null (shown as “not available”), not zero, when their denominator is zero. Reporting is monthly unless stated otherwise; owner is Field Service Performance Manager unless noted.

| ID | KPI | Governed formula | Unit | Target / warning |
|---|---|---|---|---|
| KPI-001 | SLA Compliance Rate | Eligible completed orders completed by contractual due time / eligible completed orders with SLA | % | 95 / 90 |
| KPI-002 | First-Time Fix Rate | Eligible resolved, not-reopened orders with exactly one successful completed visit / eligible resolved orders | % | 85 / 78 |
| KPI-003 | Technician Utilization Rate | Approved productive hours / available hours | % | 80 / 70 |
| KPI-004 | Average Resolution Time | Mean hours from accepted timestamp to final resolution, excluding cancelled orders | hours | <=72 / 96 |
| KPI-005 | Service Order Backlog | Non-cancelled orders not terminal at period end | count | <=500 / 650 |
| KPI-006 | Overdue Backlog | Backlog orders whose contractual due time is before period end | count | <=100 / 150 |
| KPI-007 | Repeat Visit Rate | Eligible resolved orders with more than one completed visit / eligible resolved orders | % | <=15 / 22 |
| KPI-008 | Average Service Cost | Approved service costs / distinct eligible serviced orders | currency/order | <=8000 / 9500 |
| KPI-009 | Travel Cost per Service Order | Approved travel costs / distinct eligible serviced orders | currency/order | <=1200 / 1600 |
| KPI-010 | Service Cost Variance | Sum(actual approved cost - order budget) / sum(order budget) | % | <=5 / 10 |
| KPI-011 | On-Time Service Completion Rate | Eligible completed orders completed by planned completion / eligible completed orders with plan | % | 92 / 85 |
| KPI-012 | Technician Productivity | Successfully completed eligible orders / productive technician day (8 productive hours) | orders/day | 0.65 / 0.50 |
| KPI-013 | Spare-Parts Delay Rate | Required part lines fulfilled after required-by time / fulfilled required part lines | % | <=10 / 18 |
| KPI-014 | Customer Satisfaction Score | Mean valid 1–5 survey score for eligible completed orders | score | 4.4 / 4.0 |
| KPI-015 | Data Quality Score | Passed applicable active rule checks / applicable active rule checks | % | 98 / 95 |
| KPI-016 | Open Improvement Actions | Approved actions not completed/cancelled at period end | count | <=25 / 40 |
| KPI-017 | Improvement Action Completion Rate | Actions completed by due time / actions due in period | % | 90 / 80 |
| KPI-018 | Average Improvement Closure Time | Mean calendar days from approved case to completed case | days | <=45 / 60 |

Targets are fictional portfolio defaults, configurable with effective-dated history. Currency KPIs use the reporting-currency amount produced by governed exchange-rate conversion. Reopened orders are excluded from first-time fix and use the final resolution for resolution time. Available hours exclude approved leave, public holidays, and training. Version history is persisted with effective dates, definition changes, owner, and approval metadata.

