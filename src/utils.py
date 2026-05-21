"""
utils.py — Shared helper utilities used across all modules.
Upgraded with modern glassmorphism, responsive metrics grids, and premium micro-UI components.
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
    """Return a quality score 0–100 based on completeness and uniqueness."""
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
    df_clean = df.copy()
    illegal_xml_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        df_clean[col] = df_clean[col].apply(
            lambda x: illegal_xml_re.sub('', str(x)) if pd.notnull(x) else x
        )
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_clean.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


# ── Streamlit Master CSS Injection ───────────────────────────────────────────

def inject_global_css() -> None:
    """Inject premium SaaS dark glassmorphism design tokens."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --surface:          #13121b;
    --surface-low:      #171622;
    --surface-mid:      #1f1f28;
    --surface-high:     #262536;
    --on-surface:       #e4e1ee;
    --on-surface-var:   #c7c4d8;
    --primary:          #c4c0ff;
    --primary-gradient: linear-gradient(135deg, #c4c0ff 0%, #a29bfe 100%);
    --secondary:        #d0bcff;
    --tertiary:         #ffb785;
    --outline:          #79778a;
    --outline-var:      #383747;
    --error:            #ffb4ab;
    --success:          #6ee7b7;
    --glass-card:       rgba(31, 31, 40, 0.45);
    --glass-border:     rgba(196, 192, 255, 0.08);
}

/* ── Base App Architecture ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--surface) !important;
    color: var(--on-surface) !important;
}

#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* Remove block padding spaces */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 94% !important;
}

/* ── Premium Sidebar Navigation Overhaul ────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0d14 0%, #13121b 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
    width: 320px !important;
}

/* Redesign Radio Navigation Options into SaaS App Menus */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 6px !important;
}
section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    color: var(--on-surface-var) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #ffffff !important;
    background: rgba(196, 192, 255, 0.04) !important;
    border-color: rgba(196, 192, 255, 0.08) !important;
}
section[data-testid="stSidebar"] .stRadio [data-checked="true"] label {
    color: #ffffff !important;
    background: linear-gradient(90deg, rgba(196, 192, 255, 0.12) 0%, rgba(208, 188, 255, 0.03) 100%) !important;
    border-color: rgba(196, 192, 255, 0.25) !important;
    box-shadow: inset 0 0 12px rgba(196, 192, 255, 0.05) !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }

/* ── Native Streamlit Component Re-Skinning ───────────────── */

/* 1. Transform Native st.tabs into Segmented Control Toggles */
div[data-testid="stTabBar"] {
    background: #191822 !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid var(--outline-var) !important;
    margin-bottom: 24px !important;
    gap: 4px !important;
}
div[data-testid="stTabBar"] button {
    background: transparent !important;
    color: var(--on-surface-var) !important;
    border: none !important;
    padding: 8px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stTabBar"] button:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.03) !important;
}
div[data-testid="stTabBar"] button[aria-selected="true"] {
    background: var(--surface-high) !important;
    color: var(--primary) !important;
    border: 1px solid rgba(196, 192, 255, 0.15) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}
div[data-testid="stTabBorder"] { display: none !important; }

/* 2. Premium Expanders with Border Glows */
div[data-testid="stExpander"] {
    background: var(--glass-card) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12) !important;
    margin-bottom: 1rem !important;
}
div[data-testid="stExpander"]:hover {
    border-color: rgba(196, 192, 255, 0.2) !important;
}

/* 3. Form Input Elements & Selectboxes */
.stSelectbox > div > div, .stMultiSelect > div > div, .stTextInput > div > div input {
    background: #181720 !important;
    border: 1px solid var(--outline-var) !important;
    border-radius: 10px !important;
    color: var(--on-surface) !important;
    font-size: 14px !important;
    height: 42px !important;
    transition: all 0.2s ease !important;
}
.stSelectbox > div > div:hover, .stMultiSelect > div > div:hover {
    border-color: rgba(196, 192, 255, 0.3) !important;
}

/* 4. Action Buttons Elevation */
.stButton > button {
    background: var(--primary-gradient) !important;
    color: #0f0e15 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    height: 42px !important;
    font-size: 14px !important;
    letter-spacing: -0.01em;
    box-shadow: 0 4px 15px rgba(196, 192, 255, 0.15) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 22px rgba(196, 192, 255, 0.3) !important;
    transform: translateY(-1.5px);
    color: #0f0e15 !important;
}

/* ── Modern Design System Layout Cards ─────────────────────── */
.glass-card {
    background: var(--glass-card);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(196, 192, 255, 0.25);
    box-shadow: 0 12px 40px rgba(196, 192, 255, 0.08);
}

.kpi-card {
    background: linear-gradient(145deg, #181721 0%, #121118 100%) !important;
    border: 1px solid rgba(196, 192, 255, 0.12) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.25s ease;
}
.kpi-card:hover { 
    border-color: rgba(196, 192, 255, 0.3) !important;
    transform: translateY(-2px);
}
.kpi-value { 
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem; 
    font-weight: 700; 
    letter-spacing: -0.02em; 
    color: var(--primary);
}
.kpi-label { 
    font-size: 0.75rem; 
    color: var(--outline); 
    font-weight: 700;
    text-transform: uppercase; 
    letter-spacing: 1px; 
    margin-top: 4px; 
}

/* ── Premium AI Interactive Enclosures ─────────────────────── */
.ai-response {
    background: linear-gradient(150deg, rgba(31, 31, 40, 0.6) 0%, rgba(15, 14, 21, 0.85) 100%) !important;
    border-left: 4px solid var(--primary) !important;
    border-radius: 4px 16px 16px 4px;
    padding: 24px !important;
    margin: 20px 0 !important;
    border-top: 1px solid var(--glass-border);
    border-right: 1px solid var(--glass-border);
    border-bottom: 1px solid var(--glass-border);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.3) !important;
}
.ai-badge {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(196, 192, 255, 0.14) !important;
    color: var(--primary) !important;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 14px;
    border: 1px solid rgba(196, 192, 255, 0.15);
}

.upload-zone {
    border: 2px dashed rgba(196, 192, 255, 0.15) !important;
    border-radius: 16px;
    padding: 4rem 2rem;
    background: #16151e;
    transition: all 0.3s ease;
}
.upload-zone:hover {
    border-color: var(--primary) !important;
    background: rgba(196, 192, 255, .01);
}
</style>
""", unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", colour: str = "") -> str:
    """Return HTML for an upgraded premium KPI metric card."""
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
    """Render a consistent premium page-section header structure."""
    subtitle_html = f'<p style="color:var(--on-surface-var); font-size:1.02rem; margin-top:0.4rem; line-height:1.5;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div style="margin-bottom: 2.2rem;">
    <div class="section-label">{label}</div>
    <div class="page-title" style="font-family: 'Space Grotesk', sans-serif;">{title}</div>
    {subtitle_html}
</div>
<hr style="border-color: rgba(196, 192, 255, 0.1); margin-bottom: 2.5rem; margin-top: 1.5rem;">
""", unsafe_allow_html=True)