"""
eda.py — Exploratory Data Analysis (EDA) engine.
Pure Pandas / NumPy / Plotly. No LLMs.
Fully integrated with the unified brand theme engine.
"""

import logging
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import CHART_COLORS, COLORS
from src.utils import (
    get_numeric_cols, 
    get_categorical_cols, 
    section_header, 
    style_plotly_chart, 
    saas_callout
)

logger = logging.getLogger(__name__)


# ── Individual chart builders ─────────────────────────────────────────────────

def histogram(df: pd.DataFrame, col: str, bins: int = 30) -> go.Figure:
    fig = px.histogram(
        df, x=col, nbins=bins,
        color_discrete_sequence=[COLORS["primary"]],
        title=f"Distribution — {col}",
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="rgba(0,0,0,0.2)")
    style_plotly_chart(fig)
    return fig


def boxplot(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(cols):
        clr = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Box(
            y=df[col].dropna(), name=col,
            marker_color=clr,
            line_color=clr,
            fillcolor=f"rgba({int(clr[1:3],16)},{int(clr[3:5],16)},{int(clr[5:7],16)},0.15)",
        ))
    fig.update_layout(title="Box Plots — Numeric Columns")
    style_plotly_chart(fig)
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num_df = df[get_numeric_cols(df)].dropna()
    if num_df.shape[1] < 2:
        fig = go.Figure()
        fig.update_layout(title="Not enough numeric columns for correlation")
        style_plotly_chart(fig)
        return fig

    corr = num_df.corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[
            [0.0, "#3622ca"],
            [0.5, "#1f1f28"],
            [1.0, "#c4c0ff"],
        ],
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(title="Correlation Matrix")
    style_plotly_chart(fig)
    return fig


def missing_value_chart(df: pd.DataFrame) -> go.Figure:
    null_pct = (df.isnull().mean() * 100).sort_values(ascending=False)
    null_pct = null_pct[null_pct > 0]

    if null_pct.empty:
        fig = go.Figure()
        fig.update_layout(title="✅ No missing values detected in dataset")
        style_plotly_chart(fig)
        return fig

    clrs = [COLORS["error"] if v > 40 else COLORS["tertiary"] if v > 15 else COLORS["primary"]
            for v in null_pct.values]
    fig = go.Figure(go.Bar(
        x=null_pct.index.tolist(),
        y=null_pct.values,
        marker_color=clrs,
        text=[f"{v:.1f}%" for v in null_pct.values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Missing Values by Column (%)",
        xaxis_title="Column", yaxis_title="% Missing",
        yaxis_range=[0, min(null_pct.max() * 1.25, 105)],
    )
    style_plotly_chart(fig)
    return fig


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    kwargs = dict(
        data_frame=df, x=x_col, y=y_col,
        opacity=0.65,
        color_discrete_sequence=CHART_COLORS,
        title=f"Scatter Summary — {x_col} vs {y_col}",
    )
    if color_col and color_col in df.columns:
        kwargs["color"] = color_col
    fig = px.scatter(**kwargs)
    style_plotly_chart(fig)
    return fig


def pie_chart(df: pd.DataFrame, col: str, top_n: int = 10) -> go.Figure:
    counts = df[col].value_counts().head(top_n)
    fig = px.pie(
        names=counts.index.tolist(),
        values=counts.values.tolist(),
        color_discrete_sequence=CHART_COLORS,
        title=f"Value Distribution — {col}",
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    style_plotly_chart(fig)
    return fig


def bar_chart(df: pd.DataFrame, col: str, top_n: int = 15) -> go.Figure:
    counts = df[col].value_counts().head(top_n).sort_values()
    fig = go.Figure(go.Bar(
        y=counts.index.tolist(),
        x=counts.values.tolist(),
        orientation="h",
        marker_color=COLORS["primary"],
        text=counts.values.tolist(),
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Top {top_n} Values — {col}",
        xaxis_title="Count", yaxis_title="",
    )
    style_plotly_chart(fig)
    return fig


def skewness_table(df: pd.DataFrame) -> pd.DataFrame:
    num_df = df[get_numeric_cols(df)]
    rows = []
    for col in num_df.columns:
        s = num_df[col].dropna()
        rows.append({
            "Column": col,
            "Mean": round(float(s.mean()), 4),
            "Median": round(float(s.median()), 4),
            "Std Dev": round(float(s.std()), 4),
            "Skewness": round(float(s.skew()), 4),
            "Kurtosis": round(float(s.kurt()), 4),
            "Min": round(float(s.min()), 4),
            "Max": round(float(s.max()), 4),
        })
    return pd.DataFrame(rows)


# ── Page UI ────────────────────────────────────────────────────────────────────

def render_eda_page() -> None:
    section_header(
        "ANALYTICS",
        "Interactive EDA Dashboard",
        "Explore your dataset with AI-grade visualisations powered by the stylized Plotly engine.",
    )

    df = st.session_state.get("df_cleaned") if st.session_state.get("df_cleaned") is not None else st.session_state.get("df_raw")
    if df is None:
        saas_callout("Please upload a raw dataset first to unlock the analytics workspace views.", type="info")
        return

    num_cols = get_numeric_cols(df)
    cat_cols = get_categorical_cols(df)

    tabs = st.tabs([
        "📊 Distributions", "📦 Box Plots", "🔥 Correlation Matrix",
        "❓ Missing Density", "🔵 Scatter Canvas", "🥧 Categorical Splits", "📐 Core Statistics",
    ])

    # ── Tab 0: Distributions ──
    with tabs[0]:
        if not num_cols:
            saas_callout("No valid numeric features found in this active workspace frame.", type="warning")
        else:
            selected = st.selectbox("Select numeric column", num_cols, key="hist_col")
            bins = st.slider("Bins Density count", 10, 100, 30, key="hist_bins")
            st.plotly_chart(histogram(df, selected, bins), use_container_width=True)

    # ── Tab 1: Box Plots ──
    with tabs[1]:
        if not num_cols:
            saas_callout("No valid numeric features found in this active workspace frame.", type="warning")
        else:
            selected_box = st.multiselect(
                "Select variables for bounding-box plotting", num_cols,
                default=num_cols[:min(5, len(num_cols))],
                key="box_cols",
            )
            if selected_box:
                st.plotly_chart(boxplot(df, selected_box), use_container_width=True)

    # ── Tab 2: Correlation ──
    with tabs[2]:
        if len(num_cols) < 2:
            saas_callout("Ecosystem requires at least 2 numeric variables to construct matrices.", type="warning")
        else:
            st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    # ── Tab 3: Missing Values ──
    with tabs[3]:
        st.plotly_chart(missing_value_chart(df), use_container_width=True)
        null_df = pd.DataFrame({
            "Column Matrix Field": df.columns,
            "Missing Records (Count)": df.isnull().sum().values,
            "Missing Proportion %": (df.isnull().mean() * 100).round(2).values,
        }).sort_values("Missing Proportion %", ascending=False)
        st.dataframe(null_df[null_df["Missing Proportion %"] > 0], use_container_width=True, hide_index=True)

    # ── Tab 4: Scatter ──
    with tabs[4]:
        if len(num_cols) < 2:
            saas_callout("Ecosystem requires at least 2 numeric variables to construct scatter trends.", type="warning")
        else:
            c1, c2, c3 = st.columns(3)
            x_col = c1.selectbox("X axis target mapping", num_cols, key="scatter_x")
            y_col = c2.selectbox("Y axis target mapping", num_cols, index=min(1, len(num_cols)-1), key="scatter_y")
            color_col = c3.selectbox("Categorical splitting (optional)", ["None"] + cat_cols, key="scatter_c")
            fig = scatter_plot(df, x_col, y_col, None if color_col == "None" else color_col)
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 5: Categorical ──
    with tabs[5]:
        if not cat_cols:
            saas_callout("No categoric labels/objects available inside this active sheet context.", type="warning")
        else:
            selected_cat = st.selectbox("Select target categoric dimension", cat_cols, key="cat_col")
            chart_type = st.radio("Chart display type", ["Bar Layout", "Pie Configuration"], horizontal=True, key="cat_chart")
            top_n = st.slider("Top N structural constraints", 5, 30, 10, key="cat_topn")
            if "Bar" in chart_type:
                st.plotly_chart(bar_chart(df, selected_cat, top_n), use_container_width=True)
            else:
                st.plotly_chart(pie_chart(df, selected_cat, top_n), use_container_width=True)

    # ── Tab 6: Statistics ──
    with tabs[6]:
        if not num_cols:
            saas_callout("No valid numeric features found in this active workspace frame.", type="warning")
        else:
            st.markdown("#### 📐 Mathematical Summary Metrics")
            st.dataframe(skewness_table(df), use_container_width=True, hide_index=True)
            st.markdown("#### 📋 Full Frame Distribution Describe")
            st.dataframe(df.describe(include="all").T, use_container_width=True)