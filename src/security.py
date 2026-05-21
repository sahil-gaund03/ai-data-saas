"""
security.py — Privacy-first security utilities.

Responsibilities:
  • PII detection (email, phone, Aadhaar, PAN, SSN, credit card, API keys)
  • PII masking before any LLM call
  • Secure session state helpers
  • Safe temporary file management
  • API-key loading via dotenv / Streamlit secrets

NEVER logs or stores raw user data.
"""

import re
import os
import uuid
import hashlib
import tempfile
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# ── PII regex patterns ───────────────────────────────────────────────────────
_PII_PATTERNS = {
    "email":       re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE),
    "phone_in":    re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}"),
    "phone_us":    re.compile(r"\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}"),
    "ssn":         re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ \-]?){13,16}\b"),
    "aadhaar":     re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "pan":         re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "api_key":     re.compile(r"(?:api[_\-]?key|token|secret|password)\s*[=:]\s*\S+", re.IGNORECASE),
    "ipv4":        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}


def detect_pii_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Scan a dataframe and return a dict mapping column names →
    list of PII type names detected in that column.
    Only samples up to 100 values per column for speed.
    """
    hits: dict[str, list[str]] = {}
    sample = df.sample(min(100, len(df)), random_state=42)

    for col in df.select_dtypes(include="object").columns:
        col_hits: list[str] = []
        text_blob = " ".join(sample[col].dropna().astype(str).tolist())
        for pii_type, pattern in _PII_PATTERNS.items():
            if pattern.search(text_blob):
                col_hits.append(pii_type)
        if col_hits:
            hits[col] = col_hits
    return hits


def mask_pii_value(value: str, pii_type: str) -> str:
    """Mask a single string value for the given PII type."""
    if pii_type == "email":
        try:
            local, domain = value.split("@", 1)
            masked_local = local[0] + "***"
            return f"{masked_local}@{domain}"
        except Exception:
            return "***@***.***"

    if pii_type in ("phone_in", "phone_us"):
        digits = re.sub(r"\D", "", value)
        return digits[:2] + ("*" * (len(digits) - 4)) + digits[-2:] if len(digits) > 4 else "****"

    if pii_type == "credit_card":
        digits = re.sub(r"\D", "", value)
        return "**** **** **** " + digits[-4:] if len(digits) >= 4 else "****"

    if pii_type in ("aadhaar", "ssn"):
        clean = re.sub(r"\D", "", value)
        return ("*" * (len(clean) - 4)) + clean[-4:] if len(clean) > 4 else "****"

    if pii_type == "pan":
        return value[:2] + "***" + value[-1] if len(value) >= 3 else "***"

    # Generic fallback
    return value[:2] + "***" if len(value) > 2 else "***"


def mask_pii_dataframe(df: pd.DataFrame, pii_columns: dict[str, list[str]]) -> pd.DataFrame:
    """Return a copy of df with PII columns masked."""
    masked = df.copy()
    for col, types in pii_columns.items():
        if col not in masked.columns:
            continue
        primary_type = types[0]
        masked[col] = masked[col].astype(str).apply(
            lambda v: mask_pii_value(v, primary_type)
        )
    return masked


def safe_llm_context(df: pd.DataFrame, max_rows: int = 5) -> dict:
    """
    Build a minimal, privacy-safe context dict to send to the LLM.
    NEVER includes full data. Only schema + stats + tiny sample.
    """
    pii_cols = detect_pii_columns(df)
    safe_df = mask_pii_dataframe(df, pii_cols) if pii_cols else df

    context = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "numeric_stats": {},
        "sample_rows": safe_df.head(max_rows).to_dict(orient="records"),
        "pii_detected": list(pii_cols.keys()),
    }

    # Numeric summary — safe aggregates only
    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        desc = num_df.describe().to_dict()
        context["numeric_stats"] = {
            col: {k: round(v, 4) for k, v in stats.items()}
            for col, stats in desc.items()
        }

    return context


# ── Session isolation ────────────────────────────────────────────────────────

def init_session() -> None:
    """Initialise an isolated session state for the current user."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "df_raw" not in st.session_state:
        st.session_state.df_raw = None
    if "df_cleaned" not in st.session_state:
        st.session_state.df_cleaned = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None
    if "cleaning_log" not in st.session_state:
        st.session_state.cleaning_log = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "insights_cache" not in st.session_state:
        st.session_state.insights_cache = {}


def session_has_data() -> bool:
    """True if a dataset is loaded in this session."""
    return st.session_state.get("df_raw") is not None


# ── API key loading ──────────────────────────────────────────────────────────

def load_api_key() -> Optional[str]:
    """
    Load Gemini API key safely:
      1. Streamlit Secrets (deployment)
      2. .env / environment variable (local dev)
    Returns None if not configured.
    """
    # Streamlit Secrets (Streamlit Cloud deployment)
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # .env / system environment (local development)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    key = os.getenv("GEMINI_API_KEY")
    return key if key else None


# ── Temporary file helpers ───────────────────────────────────────────────────

def write_temp_file(data: bytes, suffix: str) -> Path:
    """
    Write bytes to a secure named temp file and return its Path.
    Caller is responsible for deleting it when done.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


def delete_temp_file(path: Path) -> None:
    """Silently delete a temporary file."""
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def file_fingerprint(data: bytes) -> str:
    """SHA-256 fingerprint of raw file bytes — for dedup / integrity checks."""
    return hashlib.sha256(data).hexdigest()
