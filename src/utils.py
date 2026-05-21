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
    """
    Return a quality score 0–100 based on:
      • % complete values (no nulls)
      • % duplicate rows
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
    df_clean = df.copy()
    
    # Regex matching illegal XML characters (ASCII 0-31 except tab 9, newline 10, carriage return 13)
    illegal_xml_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')
    
    # Sanitize object and string columns cleanly without corrupting null/NaN values
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        df_clean[col] = df_clean[col].apply(
            lambda x: illegal_xml_re.sub('', str(x)) if pd.notnull(x) else x
        )
        
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_clean.to_excel(writer, index=False)
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

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
    --glass-bg:         rgba(31, 31, 40, 0.75);
    --glass-border:     rgba(196, 192, 255, 0.08);
    --glow-primary:     rgba(196, 192, 255, 0.12);
}

/* ── Base overrides ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--surface) !important;
    color: var(--on-surface) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #16151f 0%, #111016 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: var(--on-surface-var) !important;
    font-size: 14px !important;
    font-weight: 500;
    padding: 8px 12px;
    border-radius: 8px;
    transition: all .2s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--primary) !important;
    background: rgba(196, 192, 255, 0.05);
}

/* ── Glass card container ───────────────────────────────────── */
.glass-card {
    background: linear-gradient(145deg, rgba(31, 31, 40, 0.8), rgba(22, 21, 31, 0.85));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(196, 192, 255, 0.12);
    border-radius: 14px;
    padding: 1.75rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: border-color .3s, box-shadow .3s, transform .2s;
}
.glass-card:hover {
    border-color: rgba(196, 192, 255, 0.3);
    box-shadow: 0 12px 40px var(--glow-primary);
    transform: translateY(-2px);
}

/* ── KPI metric widget ──────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(145deg, #1f1f28, #16151f) !important;
    border: 1px solid rgba(196, 192, 255, 0.15) !important;
    border-radius: 14px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    text-align: left;
    transition: transform 0.2s ease, border-color 0.3s ease;
}
.kpi-card:hover { 
    border-color: rgba(196, 192, 255, 0.35) !important;
    transform: translateY(-2px);
}
.kpi-value { 
    font-size: 2.2rem; 
    font-weight: 700; 
    letter-spacing: -0.03em; 
    color: var(--primary); 
    font-variant-numeric: tabular-nums;
}
.kpi-label { 
    font-size: 0.8rem; 
    color: var(--outline); 
    font-weight: 600;
    text-transform: uppercase; 
    letter-spacing: 0.5px; 
    margin-top: 6px; 
}
.kpi-delta { font-size: 0.85rem; margin-top: 6px; font-weight: 500; }

/* ── Section header ─────────────────────────────────────────── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: var(--tertiary);
    text-transform: uppercase;
    background: rgba(255, 183, 133, 0.08);
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 0.75rem;
}

/* ── Page title ─────────────────────────────────────────────── */
.page-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #ffffff;
    line-height: 1.1;
    margin-top: 4px;
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
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 4px;
}
.chip-primary   { background: rgba(196,192,255,.12) !important; color: var(--primary) !important; border: 1px solid rgba(196,192,255,.25); }
.chip-success   { background: rgba(110,231,183,.12) !important; color: var(--success) !important; border: 1px solid rgba(110,231,183,.25); }
.chip-warning   { background: rgba(255,183,133,.12) !important; color: var(--tertiary) !important; border: 1px solid rgba(255,183,133,.25); }
.chip-error     { background: rgba(255,180,171,.12) !important; color: var(--error) !important; border: 1px solid rgba(255,180,171,.25); }

/* ── AI response container ──────────────────────────────────── */
.ai-response {
    background: linear-gradient(135deg, rgba(31, 31, 40, 0.7) 0%, rgba(19, 18, 27, 0.9) 100%) !important;
    border-left: 4px solid var(--primary) !important;
    border-top: 1px solid rgba(196, 192, 255, 0.1);
    border-right: 1px solid rgba(196, 192, 255, 0.1);
    border-bottom: 1px solid rgba(196, 192, 255, 0.1);
    border-radius: 0 12px 12px 0;
    padding: 22px !important;
    margin: 18px 0 !important;
    color: var(--on-surface) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25) !important;
    line-height: 1.7;
}
.ai-badge {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(196, 192, 255, 0.15) !important;
    color: var(--primary) !important;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(196, 192, 255, 0.2);
}

/* ── Upload zone ────────────────────────────────────────────── */
.upload-zone {
    border: 2px dashed rgba(196, 192, 255, 0.2) !important;
    border-radius: 16px;
    padding: 3.5rem 2rem;
    text-align: center;
    background: #1b1b24;
    transition: border-color .3s, background .3s;
}
.upload-zone:hover {
    border-color: var(--primary) !important;
    background: rgba(196, 192, 255, .03);
}

/* ── Chat bubbles ───────────────────────────────────────────── */
.chat-user {
    background: rgba(196, 192, 255, .1) !important;
    border: 1px solid rgba(196, 192, 255, .15) !important;
    border-radius: 12px 12px 4px 12px !important;
    padding: 1rem 1.25rem !important;
    margin-left: 3rem;
    font-size: 0.95rem;
    color: #ffffff !important;
}
.chat-ai {
    background: rgba(27, 27, 36, 0.85) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px 12px 12px 4px !important;
    padding: 1rem 1.25rem !important;
    margin-right: 3rem;
    font-size: 0.95rem;
    border-left: 3px solid var(--primary) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
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
    border: 1px solid rgba(196, 192, 255, 0.15) !important;
    border-radius: 8px !important;
    color: var(--on-surface) !important;
    padding: 2px 4px;
}
.stSelectbox > div > div:hover, .stMultiSelect > div > div:hover {
    border-color: var(--primary) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1f1f28 0%, #13121b 100%) !important;
    color: var(--on-surface) !important;
    border: 1px solid rgba(196, 192, 255, 0.3) !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    border-color: var(--primary) !important;
    color: #ffffff !important;
    box-shadow: 0 0 16px rgba(196, 192, 255, 0.2) !important;
    transform: translateY(-1px);
}
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid var(--glass-border); }
div[data-testid="stMetricValue"] { color: var(--primary) !important; font-weight: 700; }
div[data-testid="stExpander"] {
    background-color: #1f1f28 !important;
    border: 1px solid rgba(196, 192, 255, 0.1) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
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
    subtitle_html = f'<p style="color:var(--on-surface-var); font-size:1.05rem; margin-top:0.5rem; line-height:1.5;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div style="margin-bottom: 2rem; mt: 0.5rem;">
    <div class="section-label">{label}</div>
    <div class="page-title">{title}</div>
    {subtitle_html}
</div>
<hr style="border-color: rgba(196, 192, 255, 0.12); margin-bottom: 2rem; margin-top: 1.5rem;">
""", unsafe_allow_html=True)