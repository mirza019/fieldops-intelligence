# System architecture

```mermaid
flowchart LR
  G[Synthetic source generator] --> L[Immutable landing files]
  L --> V[Schema and quality validation]
  V -->|accepted| O[Validated operational schema]
  V -->|rejected| Q[Quarantine and incidents]
  O --> W[Dimensional warehouse]
  W --> K[Governed KPI views and snapshots]
  K --> P[Power BI semantic model]
  K --> A[FastAPI analytics tools]
  A --> R[React operations application]
  A --> I[Grounded AI analyst]
  I --> E[Evidence-backed explanation]
  E --> H[Human approval]
  H --> C[Improvement cases and actions]
  C --> W
```

PostgreSQL separates `landing`, `quality`, `core`, `warehouse`, `governance`, and `audit` schemas. Pipeline publishing uses a run-scoped staging area and a single transaction for critical analytical updates. APScheduler persists job state and uses a database advisory lock to prevent overlapping runs.

AI tools expose named analytical operations such as `get_kpi_value`, `compare_periods`, and `pareto_delay_reasons`. They accept validated parameters and return an evidence envelope; they do not accept SQL text.

## Security boundary

FastAPI authenticates users and enforces role permissions on every protected endpoint. The browser never connects directly to PostgreSQL. Power BI receives a read-only database identity. Secrets are environment-only. Audit records capture security-relevant mutations and AI tool use without prompt secrets.

