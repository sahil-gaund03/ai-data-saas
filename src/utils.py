"""
utils.py — Shared helper utilities used across all modules.
"""

import io
import re
import logging
from typing import Optional

import pandas as pd
import numpy as np
import streamlit as st

from src.config import COLORS, PLOTLY_TEMPLATE

logger = logging.getLogger(__name__)


# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_number(n: float | int, decimals: int = 2) -> str:
    """Format a number with thousands separators."""
    if isinstance(n, float):
        return f"{n:,.{decimals}f}"
    return f"{int(n):,}"


def fmt_pct(n: float, decimals: int = 1) -> str:
    """Format a ratio [0-1] as a percentage string."""
    return f"{n * 100:.{decimals}f}%"


def human_bytes(size_bytes: int) -> str:
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ── DataFrame utilities ───────────────────────────────────────────────────────

def get_numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def get_datetime_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()


def infer_column_role(series: pd.Series) -> str:
    """Classify a column as numeric | categorical | datetime | boolean | text."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    n_unique = series.nunique()
    if n_unique <= 20 or n_unique / max(len(series), 1) < 0.05:
        return "categorical"
    return "text"


def memory_usage(df: pd.DataFrame) -> int:
    """Return dataframe memory footprint in bytes."""
    return int(df.memory_usage(deep=True).sum())


# ── Data quality score ───────────────────────────────────────────────────────

def data_quality_score(df: pd.DataFrame) -> float:
    """
    Return a quality score 0–100 based on:
      • % complete values (no nulls)
      • % duplicate rows
      • % columns with correct dtypes inferred
    """
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0

    completeness = 1 - (df.isnull().sum().sum() / total_cells)
    uniqueness = 1 - (df.duplicated().sum() / max(len(df), 1))
    score = (completeness * 0.6 + uniqueness * 0.4) * 100
    return round(min(score, 100.0), 1)


def quality_label(score: float) -> tuple[str, str]:
    """Return (label, colour) for a quality score."""
    if score >= 85:
        return "Excellent", COLORS["success"]
    if score >= 65:
        return "Good", COLORS["primary"]
    if score >= 45:
        return "Fair", COLORS["tertiary"]
    return "Poor", COLORS["error"]


# ── Export helpers ────────────────────────────────────────────────────────────

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


# ── Streamlit CSS injection ───────────────────────────────────────────────────

def inject_global_css() -> None:
    """
    Inject the premium glassmorphism CSS that matches the DESIGN.md spec.
    Called once at app startup.
    """
    st.markdown("""
<style>
/* ── Google Fonts ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ── CSS Tokens ─────────────────────────────────────────────── */
:root {
    --surface:          #13121b;
    --surface-low:      #1b1b24;
    --surface-mid:      #1f1f28;
    --surface-high:     #2a2933;
    --surface-highest:  #35343e;
    --on-surface:       #e4e1ee;
    --on-surface-var:   #c7c4d8;
    --primary:          #c4c0ff;
    --primary-dim:      #8781ff;
    --secondary:        #d0bcff;
    --tertiary:         #ffb785;
    --outline:          #918fa1;
    --outline-var:      #464555;
    --error:            #ffb4ab;
    --success:          #6ee7b7;
    --glass-bg:         rgba(31, 31, 40, 0.80);
    --glass-border:     rgba(248, 250, 252, 0.08);
    --glow-primary:     rgba(196, 192, 255, 0.15);
}

/* ── Base overrides ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Geist', sans-serif !important;
    background-color: var(--surface) !important;
    color: var(--on-surface) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--surface-low) !important;
    border-right: 1px solid var(--glass-border) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: var(--on-surface-var) !important;
    font-size: 14px !important;
    transition: color .2s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--primary) !important;
}

/* ── Glass card container ───────────────────────────────────── */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 1.25rem;
    padding: 1.5rem;
    transition: border-color .3s, box-shadow .3s;
}
.glass-card:hover {
    border-color: rgba(196, 192, 255, 0.25);
    box-shadow: 0 0 24px var(--glow-primary);
}

/* ── KPI metric widget ──────────────────────────────────────── */
.kpi-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: border-color .3s;
}
.kpi-card:hover { border-color: rgba(196, 192, 255, 0.3); }
.kpi-value { font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--primary); }
.kpi-label { font-size: 0.75rem; color: var(--on-surface-var); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px; }
.kpi-delta { font-size: 0.8rem; margin-top: 6px; }

/* ── Section header ─────────────────────────────────────────── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: var(--outline);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Page title ─────────────────────────────────────────────── */
.page-title {
    font-size: 2.25rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: var(--on-surface);
    line-height: 1.1;
}
.gradient-text {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Status chip ────────────────────────────────────────────── */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.chip-primary   { background: rgba(196,192,255,.15); color: var(--primary); }
.chip-success   { background: rgba(110,231,183,.15); color: var(--success); }
.chip-warning   { background: rgba(255,183,133,.15); color: var(--tertiary); }
.chip-error     { background: rgba(255,180,171,.15); color: var(--error); }

/* ── AI response container ──────────────────────────────────── */
.ai-response {
    background: rgba(135,129,255,.08);
    border: 1px solid rgba(135,129,255,.25);
    border-top: 2px solid var(--primary-dim);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    font-size: 0.9rem;
    line-height: 1.7;
}
.ai-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: var(--primary);
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* ── Upload zone ────────────────────────────────────────────── */
.upload-zone {
    border: 2px dashed var(--outline-var);
    border-radius: 1.25rem;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--surface-mid);
    transition: border-color .3s, background .3s;
}
.upload-zone:hover {
    border-color: var(--primary);
    background: rgba(196,192,255,.04);
}

/* ── Chat bubbles ───────────────────────────────────────────── */
.chat-user {
    background: rgba(196,192,255,.12);
    border: 1px solid rgba(196,192,255,.2);
    border-radius: 1rem 1rem 0.25rem 1rem;
    padding: 0.75rem 1rem;
    margin-left: 2rem;
    font-size: 0.9rem;
}
.chat-ai {
    background: rgba(31,31,40,.9);
    border: 1px solid var(--glass-border);
    border-radius: 1rem 1rem 1rem 0.25rem;
    padding: 0.75rem 1rem;
    margin-right: 2rem;
    font-size: 0.9rem;
    border-left: 3px solid var(--primary-dim);
}

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--outline-var); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--outline); }

/* ── Streamlit widget overrides ─────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div input {
    background: var(--surface-mid) !important;
    border: 1px solid var(--outline-var) !important;
    border-radius: 0.5rem !important;
    color: var(--on-surface) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #8781ff, #571bc1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0.75rem !important;
    font-weight: 600 !important;
    font-family: 'Geist', sans-serif !important;
    transition: opacity .2s, box-shadow .2s !important;
}
.stButton > button:hover {
    opacity: .9 !important;
    box-shadow: 0 0 16px rgba(135,129,255,.35) !important;
}
.stDataFrame { border-radius: 0.75rem; overflow: hidden; }
div[data-testid="stMetricValue"] { color: var(--primary) !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", colour: str = "") -> str:
    """Return HTML for a KPI metric card."""
    delta_html = ""
    if delta:
        delta_colour = COLORS["success"] if not delta.startswith("-") else COLORS["error"]
        if colour:
            delta_colour = colour
        delta_html = f'<div class="kpi-delta" style="color:{delta_colour}">{delta}</div>'
    return f"""
<div class="kpi-card">
    <div class="kpi-value" style="color:{colour or COLORS['primary']}">{value}</div>
    <div class="kpi-label">{label}</div>
    {delta_html}
</div>
"""


def section_header(label: str, title: str, subtitle: str = "") -> None:
    """Render a consistent page-section header."""
    subtitle_html = f'<p style="color:var(--on-surface-var);font-size:.95rem;margin-top:.4rem">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div style="margin-bottom:1.5rem">
    <div class="section-label">{label}</div>
    <div class="page-title">{title}</div>
    {subtitle_html}
</div>
""", unsafe_allow_html=True)
