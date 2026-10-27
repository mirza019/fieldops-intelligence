from __future__ import annotations

import pandas as pd


def evaluate_orders(
    raw: pd.DataFrame, valid_customers: set[str], valid_technicians: set[str]
) -> pd.DataFrame:
    checks = {
        "DQ-001 technician required": raw.technician_id.notna(),
        "DQ-002 order key unique": ~raw.service_order_id.duplicated(keep=False),
        "DQ-003 status valid": raw.status.isin(
            {"completed", "in_progress", "scheduled", "cancelled"}
        ),
        "DQ-004 customer reference": raw.customer_id.isin(valid_customers),
        "DQ-005 technician reference": raw.technician_id.isin(valid_technicians),
        "DQ-006 completion ordering": raw.completed_at.isna()
        | (raw.completed_at >= raw.created_at),
        "DQ-007 region valid": raw.region_code.isin({"DACH", "NORDICS", "AMERICAS", "APAC"}),
        "DQ-008 freshness": raw.created_at >= raw.created_at.max() - pd.Timedelta(days=760),
    }
    return pd.DataFrame(
        [
            {
                "rule": rule,
                "dimension": dimension,
                "applicable_count": len(result),
                "passed_count": int(result.sum()),
                "failed_count": int((~result).sum()),
                "score": float(result.mean()),
            }
            for (rule, result), dimension in zip(
                checks.items(),
                [
                    "completeness",
                    "uniqueness",
                    "validity",
                    "referential_integrity",
                    "referential_integrity",
                    "consistency",
                    "validity",
                    "freshness",
                ],
                strict=True,
            )
        ]
    )
