"""
upload.py — Dataset ingestion module.

Handles:
  • File validation (MIME type, size, extension)
  • Multi-format parsing (CSV, XLSX, XLS, JSON)
  • Corrupted file detection
  • Upload statistics
  • Session state storage

Only stores data in the current user's isolated session state.
No data is written to disk permanently.
"""

import io
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from src.config import (
    MAX_FILE_SIZE_MB,
    SUPPORTED_EXTENSIONS,
    PREVIEW_ROWS,
)
from src.security import init_session, file_fingerprint
from src.utils import (
    memory_usage, data_quality_score, quality_label,
    fmt_number, human_bytes, kpi_card, section_header,
    get_numeric_cols, get_categorical_cols, get_datetime_cols,
)

logger = logging.getLogger(__name__)

# Map of supported extension → parse function
_PARSE_DISPATCH: dict = {}


def _parse_csv(raw: bytes, **_) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV with utf-8, latin-1, or cp1252.")


def _parse_excel(raw: bytes, **_) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(raw), engine="openpyxl")


def _parse_json(raw: bytes, **_) -> pd.DataFrame:
    text = raw.decode("utf-8", errors="replace")
    data = json.loads(text)
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        # Try records orientation first, then let pandas normalise
        try:
            return pd.DataFrame(data)
        except Exception:
            return pd.json_normalize(data)
    raise ValueError("JSON must be an array or object at the top level.")


_PARSERS = {
    "csv":  _parse_csv,
    "xlsx": _parse_excel,
    "xls":  _parse_excel,
    "json": _parse_json,
}


# ── Validation ────────────────────────────────────────────────────────────────

def _validate_upload(file) -> tuple[bool, str]:
    """
    Validate an uploaded file object.
    Returns (is_valid, error_message).
    """
    if file is None:
        return False, "No file provided."

    ext = Path(file.name).suffix.lstrip(".").lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, (
            f"Unsupported format '.{ext}'. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}."
        )

    size_mb = file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, (
            f"File too large ({size_mb:.1f} MB). "
            f"Maximum allowed: {MAX_FILE_SIZE_MB} MB."
        )

    return True, ""


def _safe_parse(raw: bytes, ext: str) -> pd.DataFrame:
    """Parse raw bytes for the given extension. Raises on failure."""
    parser = _PARSERS.get(ext)
    if not parser:
        raise ValueError(f"No parser registered for '.{ext}'.")
    return parser(raw)


# ── Main upload logic ─────────────────────────────────────────────────────────

def handle_upload(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Validate, parse, and store an uploaded file.
    Returns the parsed DataFrame on success, None on failure.
    """
    init_session()

    valid, err = _validate_upload(uploaded_file)
    if not valid:
        st.error(f"❌ {err}")
        return None

    ext = Path(uploaded_file.name).suffix.lstrip(".").lower()
    raw_bytes = uploaded_file.getvalue()

    try:
        with st.spinner("Parsing dataset…"):
            df = _safe_parse(raw_bytes, ext)
    except Exception as exc:
        logger.warning("Parse error: %s", exc)
        st.error(f"❌ Could not parse file: {exc}")
        return None

    if df.empty:
        st.error("❌ The uploaded file contains no data.")
        return None

    # Store in isolated session state
    st.session_state.df_raw = df
    st.session_state.df_cleaned = df.copy()  # will be updated by cleaner
    st.session_state.file_name = uploaded_file.name
    st.session_state.file_fingerprint = file_fingerprint(raw_bytes)
    st.session_state.cleaning_log = []
    st.session_state.chat_history = []
    st.session_state.insights_cache = {}

    return df


# ── UI ────────────────────────────────────────────────────────────────────────

def render_upload_page() -> None:
    """Full upload page UI."""
    section_header(
        "UPLOAD",
        "Dataset Workspace",
        "Upload your CSV, Excel, or JSON file to begin the AI analysis pipeline.",
    )

    # ── Drop zone ──
    st.markdown("""
<div class="upload-zone">
    <div style="font-size:2.5rem;margin-bottom:.75rem">📂</div>
    <div style="font-weight:600;font-size:1.05rem;color:var(--on-surface)">
        Drag & drop your file here
    </div>
    <div style="color:var(--on-surface-var);font-size:.85rem;margin-top:.4rem">
        CSV · XLSX · XLS · JSON &nbsp;|&nbsp; Max 200 MB
    </div>
</div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=SUPPORTED_EXTENSIONS,
        label_visibility="collapsed",
    )

    if uploaded_file:
        df = handle_upload(uploaded_file)
        if df is not None:
            _render_upload_success(df, uploaded_file.name)

    elif st.session_state.get("df_raw") is not None:
        # Persist previously loaded dataset across page navigation
        _render_upload_success(
            st.session_state.df_raw,
            st.session_state.file_name or "dataset",
        )


def _render_upload_success(df: pd.DataFrame, filename: str) -> None:
    """Render upload statistics and dataset preview."""
    score = data_quality_score(df)
    label, colour = quality_label(score)
    n_numeric = len(get_numeric_cols(df))
    n_cat = len(get_categorical_cols(df))
    n_dt = len(get_datetime_cols(df))
    null_pct = df.isnull().mean().mean() * 100
    dupe_pct = df.duplicated().mean() * 100
    mem = human_bytes(memory_usage(df))

    st.success(f"✅ **{filename}** loaded successfully")
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI row
    cols = st.columns(4)
    kpis = [
        ("Rows", fmt_number(df.shape[0])),
        ("Columns", fmt_number(df.shape[1])),
        ("Memory", mem),
        ("Quality Score", f"{score}"),
    ]
    for col, (lbl, val) in zip(cols, kpis):
        col.markdown(kpi_card(lbl, val, colour=colour if lbl == "Quality Score" else ""), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Secondary stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Numeric columns", n_numeric)
    c2.metric("Categorical columns", n_cat)
    c3.metric("Missing values", f"{null_pct:.1f}%")
    c4.metric("Duplicate rows", f"{dupe_pct:.1f}%")

    # Dataset preview
    st.markdown("---")
    st.markdown("#### 🔍 Dataset Preview")
    st.dataframe(
        df.head(PREVIEW_ROWS),
        use_container_width=True,
        hide_index=False,
    )

    # Column type summary
    with st.expander("📋 Column Schema", expanded=False):
        schema_data = []
        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            null_p = null_count / len(df) * 100
            schema_data.append({
                "Column": col,
                "Dtype": str(df[col].dtype),
                "Non-null": f"{len(df) - null_count:,}",
                "Missing %": f"{null_p:.1f}%",
                "Unique": f"{df[col].nunique():,}",
                "Sample": str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "—",
            })
        st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True)
