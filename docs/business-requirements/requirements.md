# Business requirements

The product gives a fictional multinational field-service organization one governed path from raw operations data to approved improvement action. It must make performance exceptions explainable, expose data-quality risk, and keep business definitions consistent across SQL, APIs, Power BI, and reports.

## Roles

| Role | Primary permissions |
|---|---|
| Administrator | Users/roles, rules, schedules, thresholds, and audit review |
| Performance Manager | Performance investigation, recommendation review, approvals, assignments |
| Data Analyst | Analytical exploration, quality investigation, proposals, reports |
| Field Service Coordinator | Assigned actions, progress updates, root-cause input, exceptions |

Authorization is enforced by the backend. Approval and administration actions are never inferred from UI visibility.

## Non-functional requirements

- Reproducible synthetic data only; Apple Silicon-compatible local stack.
- Explainable validation and metrics, complete audit history, safe retries, and transactional publishing.
- Application works without an LLM key using deterministic analytics/mock mode.
- Accessible responsive interface and actionable error/empty/loading states.
- Power BI source is versioned; Windows desktop validation is recorded honestly and separately.

