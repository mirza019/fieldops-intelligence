# ADR 002: Safe AI evidence pattern

## Status

Accepted.

## Context

AI systems can easily overstep into unsupported workflows or fabricate operational conclusions. The project must show an evidence-grounded, safe approach for performance analysis.

## Decision

AI analysis receives only allowlisted KPI values, performs no unrestricted SQL, and returns a structured observation-hypothesis-recommendation payload. A deterministic mock remains the default and a Gemini adapter is optional when a valid key is configured.

## Consequences

- AI output is explainable and auditable.
- The project remains safe for public demo use.
- The system stays aligned with synthetic-data-only constraints.
- Real model access depends on external credentials and validation.
