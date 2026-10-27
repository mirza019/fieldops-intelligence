# Architecture workflows

## Incremental pipeline

```mermaid
flowchart LR
  A[Generate source] --> B[Register batch]
  B --> C[Land raw + hash]
  C --> D[Schema validation]
  D --> E{Quality rules}
  E -->|reject| Q[Quarantine + incident]
  E -->|accept| V[Validated records]
  V --> S[SCD dimensions]
  S --> F[Load facts]
  F --> R[KPI reconciliation]
  R --> P[Atomic publication]
  P --> X[Quality results + alerts + audit]
```

Unchanged business-key/content-hash pairs are not reinserted. Duplicate events are identified before validation. Late-arriving facts use an inferred/unknown dimension key only where explicitly configured, then are restated after the dimension arrives. Critical failure rolls back the publication transaction while retaining batch diagnostics and a retryable checkpoint.

## Data-quality validation

```mermaid
flowchart TD
  R[Raw record] --> C[Completeness and schema]
  C --> U[Uniqueness]
  U --> V[Validity and date ordering]
  V --> I[References and consistency]
  I --> S{Severity}
  S -->|warning| A[Accept with result]
  S -->|record error| Q[Quarantine record]
  S -->|critical batch error| B[Stop publication]
```

## AI analytics

```mermaid
flowchart LR
  U[Authorized question] --> I[Intent classifier]
  I --> T[Allowlisted parameterized tool]
  T --> K[Governed KPI/query result]
  K --> E[Evidence envelope]
  E --> L[Mock, Gemini, or Ollama provider]
  L --> O[Observation + hypothesis + recommendation]
  O --> H[Human review]
```

## Improvement workflow

```mermaid
stateDiagram-v2
  [*] --> Define
  Define --> Measure
  Measure --> Analyze
  Analyze --> Improve: manager approves
  Improve --> Control
  Control --> Completed
  Analyze --> Rejected: manager rejects
```

## Deployment

```mermaid
flowchart LR
  G[GitHub] --> CI[Tests and source validation]
  G --> SC[Streamlit Community Cloud]
  G --> FC[fabric-cicd manual workflow]
  FC --> W[Authorized Fabric workspace]
  W --> PB[Power BI report and semantic model]
  P[(PostgreSQL local)] --> API[FastAPI]
  D[(Parquet/DuckDB snapshot)] --> SC
```
