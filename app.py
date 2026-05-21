"""
app.py — Stitch AI Data Suite
Main Streamlit entrypoint.
Page routing, sidebar navigation, global CSS injection, and session initialisation.
"""

import streamlit as st

# ── Page config must be the FIRST Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="Stitch — AI Data Suite",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Module imports (after page config) ───────────────────────────────────────
import concurrent.futures.thread
import concurrent.futures.process
import sklearn  # Pre-loads hooks on the main thread to prevent shutdown errors

from src.security import init_session
from src.utils import inject_global_css, section_header
from src.llm_engine import llm_status_badge
from src.config import APP_NAME, APP_TAGLINE, APP_VERSION, COLORS

from src.upload import render_upload_page
from src.cleaner import render_cleaning_page
from src.eda import render_eda_page
from src.insights import render_insights_page
from src.chatbot import render_chat_page
from src.automl import render_automl_page
from src.report_generator import render_reports_page


# ── Init Design Engine System ────────────────────────────────────────────────
init_session()
inject_global_css()

# ── Sidebar Navigation Blueprint ──────────────────────────────────────────────

with st.sidebar:
    # Brand Typography Segment
    st.markdown(f"""
<div style="padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid rgba(196,192,255,0.08); margin-bottom: 1.2rem;">
    <div style="font-family: 'Space Grotesk', sans-serif; font-size:1.8rem; font-weight:700; letter-spacing:-0.03em; color:#ffffff">
        {APP_NAME}<span style="color:var(--primary)">.</span>
    </div>
    <div style="font-size:0.68rem; color:var(--outline); letter-spacing:0.08em; margin-top:4px; font-weight:600; text-transform:uppercase">
        {APP_TAGLINE}
    </div>
</div>
""", unsafe_allow_html=True)

    # Core AI Infrastructure Badges
    llm_status_badge()
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Active Workspace Memory Indicators
    df_raw = st.session_state.get("df_raw")
    if df_raw is not None:
        file_name = st.session_state.get("file_name", "dataset")
        st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(196,192,255,0.05) 0%, rgba(31,31,40,0.3) 100%); border: 1px solid rgba(196,192,255,0.15); border-radius: 12px; padding: 12px 16px; margin-bottom: 1.5rem;">
    <div style="font-size:0.65rem; color:var(--outline); font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px">Active Workspace Context</div>
    <div style="font-size:.85rem; font-weight:600; color:#ffffff; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">{file_name}</div>
    <div style="font-size:.72rem; color:var(--primary); font-weight:500; margin-top:4px; font-family: 'JetBrains Mono', monospace;">{df_raw.shape[0]:,} rows × {df_raw.shape[1]} cols</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-bottom: 10px; color: var(--outline);">Platform Modules</div>', unsafe_allow_html=True)

    pages = {
        "🏠   Upload Ingestion":     "upload",
        "🧹   Data Sanitization":     "clean",
        "📊   Exploratory Metrics":   "eda",
        "💡   Neural Insights":       "insights",
        "💬   Context Chat Engine":   "chat",
        "🤖   AutoML Workspace":      "automl",
        "📄   Executive Reports":     "reports",
    }

    current_page = st.session_state.get("current_page", "upload")
    selected_label = st.radio(
        "Navigate",
        list(pages.keys()),
        index=list(pages.values()).index(current_page) if current_page in pages.values() else 0,
        label_visibility="collapsed",
    )
    st.session_state.current_page = pages[selected_label]

    # Clean Footer
    st.markdown(f"""
<div style="position:fixed; bottom:1.2rem; left:1rem; right:1rem; font-size:.65rem; color:var(--outline); text-align:center; letter-spacing:.05em; font-weight:500;">
    STITCH PLATFORM v{APP_VERSION} &nbsp;|&nbsp; Isolated Context
</div>
""", unsafe_allow_html=True)


# ── Core Component Router ────────────────────────────────────────────────────

page = st.session_state.current_page

if page == "upload":
    render_upload_page()
elif page == "clean":
    render_cleaning_page()
elif page == "eda":
    render_eda_page()
elif page == "insights":
    render_insights_page()
elif page == "chat":
    render_chat_page()
elif page == "automl":
    render_automl_page()
elif page == "reports":
    render_reports_page()
else:
    render_upload_page()