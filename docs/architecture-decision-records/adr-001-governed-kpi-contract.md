# ADR 001: Governed KPI contract

## Status

Accepted.

## Context

The platform serves multiple user-facing surfaces: Streamlit, FastAPI APIs, Power BI, and AI-supported analysis. Without a shared KPI contract, each surface could drift into different logic and produce inconsistent reporting.

## Decision

All KPI values are defined in a single governed catalog and consumed by Python and presentation layers without duplicating metric logic in UI code.

## Consequences

- KPIs are consistent across views.
- AI evidence is limited to real metric values.
- Changes to metric definition are centralized and easier to validate.
- Presentation layers remain simplified and consistent.
