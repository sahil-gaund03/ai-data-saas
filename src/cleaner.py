"""
cleaner.py — Intelligent data cleaning engine.

Pure Pandas / NumPy — no LLM involvement.

Capabilities:
  • Missing value handling (drop / fill strategies)
  • Duplicate removal
  • Data-type inference & conversion
  • Outlier detection using IQR
  • Column normalisation (min-max, z-score)
  • Text cleaning (strip, lowercase, whitespace)
  • Null percentage analysis
  • Full cleaning audit log
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.config import (
    MISSING_VALUE_DROP_THRESHOLD,
    IQR_OUTLIER_MULTIPLIER,
    COLORS,
)
from src.utils import (
    get_numeric_cols, get_categorical_cols,
    data_quality_score, quality_label,
    fmt_number, fmt_pct, kpi_card, section_header,
)

logger = logging.getLogger(__name__)


# ── Core cleaning functions ───────────────────────────────────────────────────

def drop_high_null_columns(df: pd.DataFrame, threshold: float = MISSING_VALUE_DROP_THRESHOLD) -> tuple[pd.DataFrame, list[str]]:
    """Drop columns where missing-value fraction exceeds threshold."""
    null_frac = df.isnull().mean()
    to_drop = null_frac[null_frac > threshold].index.tolist()
    return df.drop(columns=to_drop), to_drop


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows. Returns (clean_df, n_removed)."""
    before = len(df)
    df = df.drop_duplicates()
    return df, before - len(df)


def fill_missing_values(df: pd.DataFrame, strategy: str = "auto") -> tuple[pd.DataFrame, dict]:
    """
    Fill missing values:
      • numeric: median (robust to outliers)
      • categorical: mode (most frequent)
      • datetime: forward-fill
    Returns (filled_df, fill_summary).
    """
    summary: dict = {}
    df = df.copy()

    for col in df.columns:
        n_null = int(df[col].isnull().sum())
        if n_null == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median()
            df[col] = df[col].fillna(fill_val)
            summary[col] = {"n_filled": n_null, "method": "median", "value": round(float(fill_val), 4)}

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].ffill().bfill()
            summary[col] = {"n_filled": n_null, "method": "forward-fill"}

        else:
            mode_vals = df[col].mode()
            if not mode_vals.empty:
                df[col] = df[col].fillna(mode_vals[0])
                summary[col] = {"n_filled": n_null, "method": "mode", "value": str(mode_vals[0])}

    return df, summary


def convert_dtypes(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Attempt smart dtype conversions:
      • String columns that look numeric → float/int
      • String columns that look like dates → datetime
    Returns (converted_df, conversion_log).
    """
    df = df.copy()
    log: dict = {}

    for col in df.select_dtypes(include="object").columns:
        original_dtype = str(df[col].dtype)
        sample = df[col].dropna().head(200)

        # Try numeric
        converted = pd.to_numeric(sample, errors="coerce")
        if converted.notna().mean() > 0.85:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            log[col] = {"from": original_dtype, "to": str(df[col].dtype)}
            continue

        # Try datetime
        try:
            pd.to_datetime(sample, infer_datetime_format=True, errors="raise")
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            log[col] = {"from": original_dtype, "to": "datetime64[ns]"}
        except Exception:
            pass  # Keep as object

    return df, log


def detect_outliers_iqr(df: pd.DataFrame, multiplier: float = IQR_OUTLIER_MULTIPLIER) -> dict:
    """
    Detect outliers in numeric columns using IQR method.
    Returns {col: {"n_outliers": int, "pct": float, "lower": float, "upper": float}}.
    """
    result: dict = {}
    for col in get_numeric_cols(df):
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        n_out = int(mask.sum())
        if n_out > 0:
            result[col] = {
                "n_outliers": n_out,
                "pct": round(n_out / len(df) * 100, 2),
                "lower": round(float(lower), 4),
                "upper": round(float(upper), 4),
            }
    return result


def clip_outliers(df: pd.DataFrame, outlier_info: dict) -> pd.DataFrame:
    """Clip outlier values to IQR fences (Winsorization)."""
    df = df.copy()
    for col, info in outlier_info.items():
        if col in df.columns:
            df[col] = df[col].clip(lower=info["lower"], upper=info["upper"])
    return df


def normalise_columns(df: pd.DataFrame, method: str = "minmax", columns: Optional[list] = None) -> tuple[pd.DataFrame, list]:
    """
    Normalise numeric columns.
    method: 'minmax' or 'zscore'
    Returns (normalised_df, list_of_normalised_cols).
    """
    df = df.copy()
    cols = columns or get_numeric_cols(df)
    normalised: list = []

    for col in cols:
        if col not in df.columns:
            continue
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            if method == "minmax":
                vmin, vmax = s.min(), s.max()
                if vmax - vmin > 0:
                    df[col] = (s - vmin) / (vmax - vmin)
                    normalised.append(col)
            elif method == "zscore":
                mean, std = s.mean(), s.std()
                if std > 0:
                    df[col] = (s - mean) / std
                    normalised.append(col)
    return df, normalised


def clean_text_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    Basic text cleaning for string columns:
      • Strip leading/trailing whitespace
      • Collapse multiple spaces
      • Title-case very low-cardinality columns (likely categories)
    """
    df = df.copy()
    cleaned_cols: list = []
    for col in get_categorical_cols(df):
        before = df[col].copy()
        df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        if df[col].nunique() <= 30:
            df[col] = df[col].str.title()
        if not df[col].equals(before):
            cleaned_cols.append(col)
    return df, cleaned_cols


# ── Full pipeline ─────────────────────────────────────────────────────────────

class CleaningResult:
    """Container for a full cleaning run result."""

    def __init__(self):
        self.df_before: Optional[pd.DataFrame] = None
        self.df_after: Optional[pd.DataFrame] = None
        self.rows_before: int = 0
        self.rows_after: int = 0
        self.cols_before: int = 0
        self.cols_after: int = 0
        self.score_before: float = 0.0
        self.score_after: float = 0.0
        self.log: list[str] = []
        self.fill_summary: dict = {}
        self.dtype_log: dict = {}
        self.outlier_info: dict = {}
        self.dropped_cols: list[str] = []
        self.duplicates_removed: int = 0
        self.normalised_cols: list[str] = []
        self.text_cleaned_cols: list[str] = []


def run_cleaning_pipeline(
    df: pd.DataFrame,
    *,
    drop_high_null: bool = True,
    remove_dupes: bool = True,
    fill_missing: bool = True,
    fix_dtypes: bool = True,
    handle_outliers: bool = False,  # conservative: off by default
    normalise: bool = False,
    normalise_method: str = "minmax",
    clean_text: bool = True,
) -> CleaningResult:
    """
    Run the full configurable cleaning pipeline on a DataFrame.
    Returns a CleaningResult with before/after stats and audit log.
    """
    result = CleaningResult()
    result.df_before = df.copy()
    result.rows_before = len(df)
    result.cols_before = len(df.columns)
    result.score_before = data_quality_score(df)
    working = df.copy()

    if drop_high_null:
        working, dropped = drop_high_null_columns(working)
        result.dropped_cols = dropped
        if dropped:
            result.log.append(f"🗑️ Dropped {len(dropped)} high-null column(s): {', '.join(dropped)}")

    if remove_dupes:
        working, n_dupes = remove_duplicates(working)
        result.duplicates_removed = n_dupes
        if n_dupes:
            result.log.append(f"♻️ Removed {n_dupes:,} duplicate row(s)")

    if fill_missing:
        working, fill_sum = fill_missing_values(working)
        result.fill_summary = fill_sum
        if fill_sum:
            result.log.append(f"🔧 Filled missing values in {len(fill_sum)} column(s)")

    if fix_dtypes:
        working, dtype_log = convert_dtypes(working)
        result.dtype_log = dtype_log
        if dtype_log:
            result.log.append(f"🔄 Converted dtypes for {len(dtype_log)} column(s)")

    if clean_text:
        working, txt_cols = clean_text_columns(working)
        result.text_cleaned_cols = txt_cols
        if txt_cols:
            result.log.append(f"✏️ Cleaned text in {len(txt_cols)} column(s)")

    outlier_info = detect_outliers_iqr(working)
    result.outlier_info = outlier_info

    if handle_outliers and outlier_info:
        working = clip_outliers(working, outlier_info)
        result.log.append(f"📌 Clipped outliers in {len(outlier_info)} column(s)")

    if normalise:
        working, norm_cols = normalise_columns(working, method=normalise_method)
        result.normalised_cols = norm_cols
        if norm_cols:
            result.log.append(f"📐 Normalised {len(norm_cols)} column(s) using {normalise_method}")

    if not result.log:
        result.log.append("✅ Dataset was already clean — no changes needed.")

    result.df_after = working
    result.rows_after = len(working)
    result.cols_after = len(working.columns)
    result.score_after = data_quality_score(working)

    return result


# ── UI ────────────────────────────────────────────────────────────────────────

def render_cleaning_page() -> None:
    """Full data cleaning page UI."""
    section_header("DATA CLEANING", "Automated Cleaning Engine",
                   "Intelligent data cleansing powered by Pandas & NumPy. Zero LLM involvement.")

    if st.session_state.get("df_raw") is None:
        st.info("⬆️ Upload a dataset first using the **Upload Dataset** page.")
        return

    df = st.session_state.df_raw

    # ── Cleaning options ──
    with st.expander("⚙️ Cleaning Options", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            drop_high_null = st.checkbox("Drop high-null columns (> 60 %)", value=True)
            remove_dupes = st.checkbox("Remove duplicate rows", value=True)
            fill_missing = st.checkbox("Fill missing values (median/mode)", value=True)
            fix_dtypes = st.checkbox("Auto-convert data types", value=True)
        with c2:
            clean_text = st.checkbox("Clean text columns", value=True)
            handle_outliers = st.checkbox("Clip outliers (IQR Winsorization)", value=False)
            normalise = st.checkbox("Normalise numeric columns", value=False)
            normalise_method = st.selectbox("Normalisation method", ["minmax", "zscore"],
                                            disabled=not normalise)

    if st.button("🚀 Run Cleaning Pipeline", use_container_width=True):
        with st.spinner("Running cleaning pipeline…"):
            result = run_cleaning_pipeline(
                df,
                drop_high_null=drop_high_null,
                remove_dupes=remove_dupes,
                fill_missing=fill_missing,
                fix_dtypes=fix_dtypes,
                handle_outliers=handle_outliers,
                normalise=normalise,
                normalise_method=normalise_method,
                clean_text=clean_text,
            )

        # Save cleaned df
        st.session_state.df_cleaned = result.df_after
        st.session_state.cleaning_log = result.log

        _render_cleaning_results(result)
    elif st.session_state.get("cleaning_log"):
        st.info("✅ Dataset has been cleaned. Results shown below.")
        if st.session_state.get("df_cleaned") is not None:
            _render_quick_summary()


def _render_cleaning_results(result: CleaningResult) -> None:
    st.success("✅ Cleaning complete!")
    st.markdown("<br>", unsafe_allow_html=True)

    # Before / After KPIs
    cols = st.columns(4)
    deltas = [
        ("Rows Before", fmt_number(result.rows_before)),
        ("Rows After", fmt_number(result.rows_after)),
        ("Quality Before", f"{result.score_before}"),
        ("Quality After", f"{result.score_after}"),
    ]
    colours = ["", "", COLORS["tertiary"], COLORS["success"]]
    for col, (lbl, val), clr in zip(cols, deltas, colours):
        col.markdown(kpi_card(lbl, val, colour=clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Audit log
    st.markdown("#### 📋 Cleaning Audit Log")
    for entry in result.log:
        st.markdown(f"- {entry}")

    # Outlier report
    if result.outlier_info:
        st.markdown("---")
        st.markdown("#### ⚠️ Outlier Detection Report")
        outlier_df = pd.DataFrame([
            {
                "Column": col,
                "Outliers": info["n_outliers"],
                "% of Rows": f"{info['pct']}%",
                "Lower Fence": info["lower"],
                "Upper Fence": info["upper"],
            }
            for col, info in result.outlier_info.items()
        ])
        st.dataframe(outlier_df, use_container_width=True, hide_index=True)

    # Cleaned preview
    st.markdown("---")
    st.markdown("#### 🔍 Cleaned Dataset Preview")
    st.dataframe(result.df_after.head(50), use_container_width=True)


def _render_quick_summary() -> None:
    """Show a quick summary when the page re-renders after cleaning."""
    df_c = st.session_state.df_cleaned
    st.markdown("#### 📋 Cleaning Log")
    for entry in st.session_state.cleaning_log:
        st.markdown(f"- {entry}")
    st.dataframe(df_c.head(50), use_container_width=True)
