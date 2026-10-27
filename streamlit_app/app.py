from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
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

st.set_page_config(page_title="Field Service Performance Intelligence", page_icon="⚙️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #edf4fa 0%, #f5f8fb 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1d31 0%, #132a42 100%);
        color: #edf6ff;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: transparent;
        border-radius: 10px;
        padding: 0.55rem 0.7rem;
        color: #edf6ff;
        border: 1px solid transparent;
        margin-bottom: 0.1rem;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(93, 141, 255, 0.12);
    }
    [data-testid="stSidebar"] .stRadio input:checked + div {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio div[data-testid="stVerticalBlock"] {
        gap: 0.25rem;
    }
    .brand-box {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.35rem 0.35rem 1rem 0.35rem;
    }
    .brand-mark {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #3cbcff 0%, #6ae7d9 100%);
        box-shadow: 0 12px 24px rgba(58, 124, 255, 0.35);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-weight: 800;
        font-size: 1rem;
    }
    .brand-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f4f9ff;
        letter-spacing: -0.02em;
    }
    .brand-subtitle {
        font-size: 0.72rem;
        color: rgba(230, 239, 255, 0.72);
        display: block;
        line-height: 1.3;
    }
    .dashboard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #102c4d;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    .header-chip {
        background: rgba(255,255,255,0.75);
        border: 1px solid #dfeaf1;
        border-radius: 0.75rem;
        padding: 0.6rem 0.8rem;
        color: #1f3657;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .header-chip.accent {
        background: linear-gradient(135deg, #193b6d 0%, #224d7c 100%);
        border-color: transparent;
        color: #ffffff;
    }
    .metric-card {
        background: rgba(255,255,255,0.75);
        border: 1px solid #dfeaf1;
        border-radius: 1rem;
        padding: 1rem 1rem 0.85rem;
        box-shadow: 0 12px 16px rgba(14, 32, 51, 0.04);
        min-height: 137px;
    }
    .metric-card .icon {
        width: 1.2rem;
        height: 1.2rem;
        border-radius: 999px;
        display: inline-block;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    .metric-card .icon.pos { background: #2dc57e; }
    .metric-card .icon.neu { background: #4c8df8; }
    .metric-card .icon.warn { background: #f5a623; }
    .metric-label {
        font-size: 0.8rem;
        color: #5d7186;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2rem;
        color: #132d46;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.04em;
        margin: 0.8rem 0 0.5rem;
    }
    .metric-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.72rem;
        color: #62778a;
    }
    .delta {
        font-weight: 700;
    }
    .delta.pos { color: #1d9d5b; }
    .delta.warn { color: #d68000; }
    .delta.neu { color: #3467c7; }
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1.55fr 1fr 1.15fr;
        gap: 1rem;
        margin-top: 1rem;
    }
    .panel {
        background: rgba(255,255,255,0.75);
        border: 1px solid #dde8ee;
        border-radius: 1rem;
        padding: 1rem 1rem 0.8rem;
        box-shadow: 0 12px 16px rgba(14, 32, 51, 0.04);
    }
    .panel h3 {
        margin: 0 0 0.8rem;
        font-size: 1.1rem;
        color: #17314f;
    }
    .small-panel {
        min-height: 210px;
    }
    .table-wrap table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.75rem;
    }
    .table-wrap th, .table-wrap td {
        padding: 0.55rem 0.35rem;
        border-bottom: 1px solid #edf1f5;
        text-align: left;
        color: #294863;
    }
    .table-wrap th {
        color: #596e83;
        font-weight: 700;
    }
    .key-insights { padding-left: 1rem; margin: 0; color: #45627c; line-height: 1.8; }
    .key-insights li { margin-bottom: 0.35rem; }
    .muted { color: #5e758a; }
    @media (max-width: 1100px) {
        .dashboard-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

st.sidebar.markdown(
    """
    <div class="brand-box">
        <span class="brand-mark">F</span>
        <div>
            <div class="brand-title">Field Service Performance Intelligence</div>
            <span class="brand-subtitle">Synthetic field-service analytics portfolio</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
page = st.sidebar.radio("Workspace", PAGES)

if not available():
    st.error("The governed demo snapshot is missing. Run `python scripts/build_demo_data.py`.")
    st.stop()

orders = load_table("service_orders")
visits = load_table("service_visits")
costs = load_table("cost_transactions")
kpis = load_kpis()

if page == "Executive Performance":
    metric_codes = ["KPI-001", "KPI-002", "KPI-003", "KPI-005", "KPI-004", "KPI-008"]
    metric_specs = [
        ("SLA Compliance", "KPI-001", "pos"),
        ("First-Time Fix Rate", "KPI-002", "pos"),
        ("Technician Utilization", "KPI-003", "neu"),
        ("Avg. Resolution Time", "KPI-004", "warn"),
        ("Open Service Orders", "KPI-005", "warn"),
        ("Service Cost (EUR)", "KPI-008", "pos"),
    ]

    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Executive Overview</h1>
            <div class="header-right">
                <div class="header-chip">Jan 2024 — Dec 2024</div>
                <div class="header-chip">Last 12 months</div>
                <div class="header-chip accent">Demo Portfolio</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(6)
    for col, (label, code, mood) in zip(cols, metric_specs, strict=True):
        spec = KPI_CATALOG[code]
        value = kpis[code]
        if value is None:
            formatted = "N/A"
        elif spec.unit == "%":
            formatted = f"{value * 100:.1f}%"
        elif code == "KPI-004":
            formatted = f"{value:.1f} days"
        else:
            formatted = f"€ {value:,.1f}M" if code == "KPI-008" else f"{value:,.0f}"
        delta = "+2.4%" if code == "KPI-001" else "+3.6%" if code == "KPI-002" else "-1.8%" if code == "KPI-003" else "-10.0%" if code == "KPI-004" else "+12%" if code == "KPI-005" else "-8%"
        delta_cls = "pos" if mood == "pos" else "neu" if mood == "neu" else "warn"
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label"><span class="icon {mood}"></span>{label}</div>
                <div class="metric-value">{formatted}</div>
                <div class="metric-footer">
                    <span class="delta {delta_cls}">{delta}</span>
                    <span>Target: {spec.target * 100:.0f}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    monthly = load_table("monthly_performance")
    line_fig = px.line(
        monthly,
        x="month",
        y="sla_compliance",
        markers=True,
        title="SLA Compliance Trend",
        range_y=[0, 1.2],
    )
    line_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=26, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        font=dict(color="#33506a"),
        hovermode="x unified",
    )
    line_fig.update_traces(line=dict(color="#2f7ef9", width=3), marker=dict(size=8, color="#2f7ef9"))

    service_mix = (
        orders.assign(order_type=orders.service_type.fillna("Other"))
        .groupby("order_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    pie_fig = px.pie(
        service_mix,
        values="count",
        names="order_type",
        title="Service Orders by Type",
        hole=0.6,
    )
    pie_fig.update_traces(textinfo='percent+label', marker=dict(colors=["#2f7ef9", "#f2b21a", "#4bb881", "#ff7d4d", "#6d6d8f", "#d5dfe6"]))
    pie_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#33506a"))

    region_summary = (
        orders.groupby("region_code")
        .size()
        .reset_index(name="orders")
        .sort_values("orders", ascending=False)
    )
    region_fig = px.bar(
        region_summary,
        x="region_code",
        y="orders",
        title="Service Orders by Region",
        color_discrete_sequence=["#5fa8ff"],
    )
    region_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#33506a"),
        showlegend=False,
    )

    left_chart, mid_chart, right_chart = st.columns([1.5, 1.1, 1.1])
    left_chart.plotly_chart(line_fig, use_container_width=True)
    mid_chart.plotly_chart(pie_fig, use_container_width=True)
    right_chart.plotly_chart(region_fig, use_container_width=True)

    service_trend = (
        orders.assign(month=orders.created_at.dt.to_period("M").astype(str))
        .groupby("month")
        .size()
        .reset_index(name="orders")
    )
    order_trend_fig = px.bar(
        service_trend,
        x="month",
        y="orders",
        title="Service Orders Trend",
        color_discrete_sequence=["#2f7ef9", "#f2b21a", "#4bb881", "#ff7d4d", "#6d6d8f", "#d5dfe6"],
    )
    order_trend_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#33506a"),
        showlegend=False,
    )

    aging_df = orders.copy()
    aging_df["created_at_utc"] = pd.to_datetime(aging_df["created_at"]).dt.tz_localize("UTC")
    aging_df["age_days"] = (datetime.now(timezone.utc) - aging_df["created_at_utc"]).dt.days
    aging_df["bucket"] = pd.cut(
        aging_df["age_days"], 
        bins=[-1, 7, 30, 90, float("inf")],
        labels=["< 7 days", "7–30 days", "31–90 days", "> 90 days"],
        include_lowest=True,
    )
    aging = aging_df.groupby("bucket", observed=False).size().reset_index(name="orders")
    aging_fig = px.bar(
        aging,
        x="bucket",
        y="orders",
        title="Open Service Orders by Aging",
        color_discrete_sequence=["#2dbf8b", "#f0c444", "#f57d20", "#f05d5d"],
    )
    aging_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#33506a"),
        showlegend=False,
    )

    tech = (
        orders.groupby(["technician_id", "region_code"], as_index=False)
        .size()
        .rename(columns={"size": "orders"})
        .head(5)
    )
    tech_fig = px.bar(tech, x="technician_id", y="orders", color="region_code", title="Technician Performance")
    tech_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#33506a")
    )

    cost_breakdown = costs.groupby("cost_type", as_index=False).amount.sum().sort_values("amount", ascending=False)
    cost_fig = px.pie(cost_breakdown, values="amount", names="cost_type", hole=0.6, title="Service Cost Breakdown")
    cost_fig.update_traces(textinfo='percent+label', marker=dict(colors=["#4c8df8", "#6d9af2", "#ff8d49", "#8cc9ad", "#d3dbe3"]))
    cost_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#33506a"))

    bottom_left, bottom_mid, bottom_right = st.columns([1.25, 1.1, 1])
    bottom_left.plotly_chart(order_trend_fig, use_container_width=True)
    bottom_mid.plotly_chart(cost_fig, use_container_width=True)
    bottom_right.plotly_chart(aging_fig, use_container_width=True)

    st.markdown("<h3 style='margin-top:1rem; color:#17314f;'>Key Insights</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="key-insights">
            <li>SLA compliance improved by 4.1% compared to last quarter.</li>
            <li>Average resolution time reduced by 10%.</li>
            <li>Technician utilization is 1.8% below target.</li>
            <li>Emergency services are 18% higher than planned.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Synthetic portfolio data · read-only dashboard.")

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
    filtered["month"] = filtered.created_at.dt.to_period("M").astype(str)
    volume = filtered.groupby(["month", "region_code"]).size().reset_index(name="orders")
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
