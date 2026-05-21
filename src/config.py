"""
config.py — Global configuration constants for Stitch AI Data Suite.
All tweakable settings live here; no magic numbers scattered in the codebase.
"""

import os

# ── App identity ────────────────────────────────────────────────────────────
APP_NAME = "Stitch"
APP_TAGLINE = "AI-Powered Data Intelligence Platform"
APP_VERSION = "1.0.0"

# ── File upload limits ───────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 200          # maximum upload size
SUPPORTED_EXTENSIONS = ["csv", "xlsx", "xls", "json"]
PREVIEW_ROWS = 50               # rows shown in dataset preview table

# ── Data cleaning thresholds ─────────────────────────────────────────────────
MISSING_VALUE_DROP_THRESHOLD = 0.60   # drop column if >60 % values missing
IQR_OUTLIER_MULTIPLIER = 1.5          # standard IQR fence multiplier
HIGH_CARDINALITY_THRESHOLD = 50       # unique values above this → not auto-encoded

# ── LLM / Gemini ─────────────────────────────────────────────────────────────
# ── LLM / Gemini ─────────────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.5-flash"     # Updated to stable production model
LLM_MAX_SAMPLE_ROWS = 5              # rows sent to LLM (privacy guard)
LLM_MAX_OUTPUT_TOKENS = 1024

# ── AutoML ───────────────────────────────────────────────────────────────────
AUTOML_CV_FOLDS = 3
AUTOML_TEST_SIZE = 0.2
AUTOML_RANDOM_STATE = 42
AUTOML_MAX_FEATURES_SHOWN = 15        # feature importance chart cap

# ── Report generation ────────────────────────────────────────────────────────
REPORT_OUTPUT_DIR = "reports"
REPORTS_LOGO_SIZE = 12                # pt for header text in PDF

# ── Security / PII ───────────────────────────────────────────────────────────
PII_MASK_CHAR = "*"

# ── Colour palette (mirrors DESIGN.md tokens) ────────────────────────────────
COLORS = {
    "primary":    "#c4c0ff",
    "secondary":  "#d0bcff",
    "tertiary":   "#ffb785",
    "surface":    "#13121b",
    "surface_container": "#1f1f28",
    "on_surface": "#e4e1ee",
    "outline":    "#918fa1",
    "error":      "#ffb4ab",
    "success":    "#6ee7b7",
}

# Plotly chart template matching dark design
PLOTLY_TEMPLATE = "plotly_dark"
CHART_COLORS = [
    "#c4c0ff", "#d0bcff", "#ffb785", "#6ee7b7",
    "#f9a8d4", "#93c5fd", "#fde68a", "#a5b4fc",
]
