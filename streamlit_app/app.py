from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.kpis import KPI_CATALOG
from streamlit_app.services.ai import mock_answer
from streamlit_app.services.data import available, load_kpis, load_table
from streamlit_app.services.simulation import simulate

st.set_page_config(page_title="FieldOps Intelligence", page_icon="⚙️", layout="wide")
st.title("FieldOps Intelligence")
st.caption("Synthetic industrial field-service analytics · read-only portfolio mode")

PAGES = [
    "Executive Performance",
    "Operational Analytics",
    "Power BI Analytics",
    "AI Performance Analyst",
    "Data Quality & Governance",
    "Lean Continuous Improvement",
    "What-If Simulation",
    "Pipeline Monitoring",
]
page = st.sidebar.radio("Workspace", PAGES)

if not available():
    st.error("The governed demo snapshot is missing. Run `python scripts/build_demo_data.py`.")
    st.stop()

orders = load_table("service_orders")
visits = load_table("service_visits")
costs = load_table("cost_transactions")
kpis = load_kpis()

if page == "Executive Performance":
    columns = st.columns(6)
    for column, code in zip(
        columns, ["KPI-001", "KPI-002", "KPI-003", "KPI-005", "KPI-004", "KPI-008"], strict=True
    ):
        spec, value = KPI_CATALOG[code], kpis[code]
        formatted = (
            "N/A" if value is None else (f"{value:.1%}" if spec.unit == "%" else f"{value:,.1f}")
        )
        column.metric(
            spec.name,
            formatted,
            f"Target {spec.target:.0%}" if spec.unit == "%" else f"Target {spec.target:,.0f}",
        )
    monthly = load_table("monthly_performance")
    st.plotly_chart(
        px.line(
            monthly, x="month", y="sla_compliance", markers=True, title="Monthly SLA compliance"
        ),
        use_container_width=True,
    )
    regional = (
        orders.assign(sla=orders.completed_at <= orders.sla_due_at)
        .query("status == 'completed'")
        .groupby("region_code", as_index=False)
        .sla.mean()
    )
    st.plotly_chart(
        px.bar(regional, x="region_code", y="sla", color="sla", title="Regional SLA performance"),
        use_container_width=True,
    )

elif page == "Operational Analytics":
    region = st.multiselect(
        "Region", sorted(orders.region_code.unique()), default=sorted(orders.region_code.unique())
    )
    service = st.multiselect(
        "Service type",
        sorted(orders.service_type.unique()),
        default=sorted(orders.service_type.unique()),
    )
    filtered = orders[orders.region_code.isin(region) & orders.service_type.isin(service)].copy()
    volume = (
        filtered.groupby([filtered.created_at.dt.to_period("M").astype(str), "region_code"])
        .size()
        .rename("orders")
        .reset_index(names=["month", "region_code"])
    )
    st.plotly_chart(
        px.bar(volume, x="month", y="orders", color="region_code", title="Service demand"),
        use_container_width=True,
    )
    repeat = (
        visits.groupby("service_order_id")
        .size()
        .value_counts()
        .sort_index()
        .rename_axis("visits")
        .reset_index(name="orders")
    )
    st.plotly_chart(
        px.bar(repeat, x="visits", y="orders", title="Repeat-visit distribution"),
        use_container_width=True,
    )
    cost_driver = (
        costs.groupby("cost_type", as_index=False)
        .amount.sum()
        .sort_values("amount", ascending=False)
    )
    st.plotly_chart(
        px.bar(cost_driver, x="cost_type", y="amount", title="Cost-driver Pareto"),
        use_container_width=True,
    )

elif page == "Power BI Analytics":
    public_url = os.getenv("POWERBI_PUBLIC_EMBED_URL", "")
    private_url = os.getenv("POWERBI_REPORT_URL", "")
    if public_url:
        st.warning("Public embedding is enabled only for the approved synthetic dataset.")
        st.components.v1.iframe(public_url, height=720)
    elif private_url:
        st.link_button("Open authenticated Power BI report", private_url)
        st.info("Microsoft account permissions are required.")
    else:
        st.info(
            "Portfolio preview mode. No verified screenshots or deployed report are available yet."
        )
        st.code("powerbi/FieldOpsIntelligence.pbip")

elif page == "AI Performance Analyst":
    question = st.text_input(
        "Ask about performance",
        "Which KPIs are below target and what should management investigate?",
    )
    if st.button("Analyze", type="primary"):
        response = mock_answer(question, kpis)
        st.subheader("Observation")
        st.write(response["observation"])
        st.subheader("Hypothesis")
        st.write(response["hypothesis"])
        st.subheader("Recommendation")
        st.write(response["recommendation"])
        st.dataframe(pd.DataFrame(response["evidence"]), use_container_width=True)
        st.caption("Deterministic demo provider. Metrics come from the governed snapshot.")

elif page == "Data Quality & Governance":
    quality = load_table("quality_results")
    score = quality.passed_count.sum() / quality.applicable_count.sum()
    st.metric("Overall data quality", f"{score:.2%}")
    st.plotly_chart(
        px.bar(
            quality,
            x="dimension",
            y="score",
            color="failed_count",
            hover_data=["rule"],
            title="Quality by rule and dimension",
        ),
        use_container_width=True,
    )
    st.dataframe(quality, use_container_width=True)

elif page == "Lean Continuous Improvement":
    cases = load_table("improvement_cases")
    actions = load_table("improvement_actions")
    st.caption("Public demo mode is read-only; approvals and updates are disabled.")
    st.plotly_chart(
        px.histogram(cases, x="dmaic_stage", color="status", title="DMAIC portfolio"),
        use_container_width=True,
    )
    st.dataframe(cases, use_container_width=True)
    st.dataframe(actions, use_container_width=True)

elif page == "What-If Simulation":
    c1, c2, c3 = st.columns(3)
    technicians = c1.slider("Technician capacity %", -20, 30, 10)
    demand = c2.slider("Service demand %", -20, 30, 0)
    parts = c3.slider("Parts lead-time %", -40, 40, -10)
    scheduling = c1.slider("Scheduling efficiency %", -20, 30, 10)
    travel = c2.slider("Travel time %", -30, 30, 0)
    cost = c3.slider("Cost assumption %", -20, 30, 0)
    baseline = {
        "sla": kpis["KPI-001"],
        "backlog": kpis["KPI-005"],
        "utilization": kpis["KPI-003"],
        "resolution": kpis["KPI-004"],
        "cost": kpis["KPI-008"],
    }
    scenario = simulate(baseline, technicians, demand, parts, scheduling, travel, cost)
    comparison = pd.DataFrame(
        {
            "metric": list(scenario),
            "Baseline": [
                baseline["sla"],
                baseline["backlog"],
                baseline["utilization"],
                baseline["resolution"],
                baseline["cost"],
            ],
            "Scenario": list(scenario.values()),
        }
    )
    st.dataframe(comparison, use_container_width=True)
    st.caption("Directional capacity model; outputs are estimates, not forecasts or causal claims.")

else:
    quality = load_table("quality_results")
    stages = pd.DataFrame(
        {
            "stage": [
                "ingestion",
                "schema validation",
                "quality validation",
                "analytical publish",
                "KPI snapshot",
            ],
            "status": ["completed"] * 5,
            "records": [
                len(orders),
                len(orders),
                int(quality.applicable_count.sum()),
                len(orders),
                len(kpis),
            ],
        }
    )
    st.success("Latest saved demo pipeline run completed")
    st.dataframe(stages, use_container_width=True)
    st.caption("Public mode displays verified saved results and cannot trigger pipeline runs.")
