"""
eda.py — Exploratory Data Analysis (EDA) engine.

Pure Pandas / NumPy / Plotly. No LLMs.

Charts generated:
  • Distribution (histogram) for numeric columns
  • Box plots for outlier visualisation
  • Correlation heatmap
  • Missing value chart
  • Scatter plot (numeric × numeric)
  • Pie / bar chart for categorical columns
  • Skewness & kurtosis table
"""

import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import streamlit as st

from src.config import PLOTLY_TEMPLATE, CHART_COLORS, COLORS
from src.utils import get_numeric_cols, get_categorical_cols, section_header

logger = logging.getLogger(__name__)

# ── Shared Plotly layout settings ─────────────────────────────────────────────

_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Geist, sans-serif", color="#e4e1ee"),
    margin=dict(t=40, b=40, l=40, r=20),
    colorway=CHART_COLORS,
)


def _apply(fig) -> go.Figure:
    fig.update_layout(**_LAYOUT)
    return fig


# ── Individual chart builders ─────────────────────────────────────────────────

def histogram(df: pd.DataFrame, col: str, bins: int = 30) -> go.Figure:
    fig = px.histogram(
        df, x=col, nbins=bins,
        color_discrete_sequence=[COLORS["primary"]],
        title=f"Distribution — {col}",
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="rgba(0,0,0,0.2)")
    return _apply(fig)


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
    fig.update_layout(title="Box Plots — Numeric Columns", **_LAYOUT)
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num_df = df[get_numeric_cols(df)].dropna()
    if num_df.shape[1] < 2:
        return go.Figure().update_layout(title="Not enough numeric columns for correlation", **_LAYOUT)

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
    fig.update_layout(title="Correlation Heatmap", **_LAYOUT)
    return fig


def missing_value_chart(df: pd.DataFrame) -> go.Figure:
    null_pct = (df.isnull().mean() * 100).sort_values(ascending=False)
    null_pct = null_pct[null_pct > 0]

    if null_pct.empty:
        fig = go.Figure()
        fig.update_layout(title="✅ No missing values detected", **_LAYOUT)
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
        **_LAYOUT,
    )
    return fig


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None) -> go.Figure:
    kwargs = dict(
        data_frame=df, x=x_col, y=y_col,
        opacity=0.65,
        color_discrete_sequence=CHART_COLORS,
        title=f"Scatter — {x_col} vs {y_col}",
    )
    if color_col and color_col in df.columns:
        kwargs["color"] = color_col
    fig = px.scatter(**kwargs)
    return _apply(fig)


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
    return _apply(fig)


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
        **_LAYOUT,
    )
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
        "Explore your dataset with AI-grade visualisations powered by Plotly.",
    )

    df = st.session_state.get("df_cleaned") if st.session_state.get("df_cleaned") is not None else st.session_state.get("df_raw")
    if df is None:
        st.info("⬆️ Upload a dataset first.")
        return

    num_cols = get_numeric_cols(df)
    cat_cols = get_categorical_cols(df)

    tabs = st.tabs([
        "📊 Distributions", "📦 Box Plots", "🔥 Correlation",
        "❓ Missing Values", "🔵 Scatter", "🥧 Categorical", "📐 Statistics",
    ])

    # ── Tab 0: Distributions ──
    with tabs[0]:
        if not num_cols:
            st.warning("No numeric columns found.")
        else:
            selected = st.selectbox("Select numeric column", num_cols, key="hist_col")
            bins = st.slider("Bins", 10, 100, 30, key="hist_bins")
            st.plotly_chart(histogram(df, selected, bins), use_container_width=True)

    # ── Tab 1: Box Plots ──
    with tabs[1]:
        if not num_cols:
            st.warning("No numeric columns found.")
        else:
            selected_box = st.multiselect(
                "Select columns for box plot", num_cols,
                default=num_cols[:min(5, len(num_cols))],
                key="box_cols",
            )
            if selected_box:
                st.plotly_chart(boxplot(df, selected_box), use_container_width=True)

    # ── Tab 2: Correlation ──
    with tabs[2]:
        if len(num_cols) < 2:
            st.warning("Need at least 2 numeric columns.")
        else:
            st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    # ── Tab 3: Missing Values ──
    with tabs[3]:
        st.plotly_chart(missing_value_chart(df), use_container_width=True)
        null_df = pd.DataFrame({
            "Column": df.columns,
            "Missing Count": df.isnull().sum().values,
            "Missing %": (df.isnull().mean() * 100).round(2).values,
        }).sort_values("Missing %", ascending=False)
        st.dataframe(null_df[null_df["Missing %"] > 0], use_container_width=True, hide_index=True)

    # ── Tab 4: Scatter ──
    with tabs[4]:
        if len(num_cols) < 2:
            st.warning("Need at least 2 numeric columns.")
        else:
            c1, c2, c3 = st.columns(3)
            x_col = c1.selectbox("X axis", num_cols, key="scatter_x")
            y_col = c2.selectbox("Y axis", num_cols, index=min(1, len(num_cols)-1), key="scatter_y")
            color_col = c3.selectbox("Colour by (optional)", ["None"] + cat_cols, key="scatter_c")
            fig = scatter_plot(df, x_col, y_col, None if color_col == "None" else color_col)
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 5: Categorical ──
    with tabs[5]:
        if not cat_cols:
            st.warning("No categorical columns found.")
        else:
            selected_cat = st.selectbox("Select categorical column", cat_cols, key="cat_col")
            chart_type = st.radio("Chart type", ["Bar", "Pie"], horizontal=True, key="cat_chart")
            top_n = st.slider("Top N values", 5, 30, 10, key="cat_topn")
            if chart_type == "Bar":
                st.plotly_chart(bar_chart(df, selected_cat, top_n), use_container_width=True)
            else:
                st.plotly_chart(pie_chart(df, selected_cat, top_n), use_container_width=True)

    # ── Tab 6: Statistics ──
    with tabs[6]:
        if not num_cols:
            st.warning("No numeric columns found.")
        else:
            st.markdown("#### 📐 Descriptive Statistics")
            st.dataframe(skewness_table(df), use_container_width=True, hide_index=True)
            st.markdown("#### 📋 Full Describe")
            st.dataframe(df.describe(include="all").T, use_container_width=True)
