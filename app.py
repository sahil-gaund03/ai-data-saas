"""
app.py — Stitch AI Data Suite
Main Streamlit entrypoint.

Page routing, sidebar navigation, global CSS injection, and session initialisation.
All data processing stays in isolated per-user session state.
""" 
import concurrent.futures.thread
import concurrent.futures.process
import sklearn  # Pre-loads scikit-learn hooks on the main execution thread

import streamlit as st

# ── Page config must remain the FIRST Streamlit call ──────────────────────────
st.set_page_config(
    page_title="Stitch — AI Data Suite",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ... rest of your imports and application logic continues below unchanged
import streamlit as st

# ── Page config must be the FIRST Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="Stitch — AI Data Suite",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Module imports (after page config) ───────────────────────────────────────
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


# ── Init ─────────────────────────────────────────────────────────────────────
init_session()
inject_global_css()

# ── Sidebar navigation ────────────────────────────────────────────────────────

with st.sidebar:
    # Brand
    st.markdown(f"""
<div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid rgba(248,250,252,0.08); margin-bottom: 1rem;">
    <div style="font-size:1.5rem;font-weight:800;letter-spacing:-0.04em;color:var(--primary)">
        {APP_NAME}
    </div>
    <div style="font-size:0.7rem;color:var(--on-surface-var);letter-spacing:0.06em;margin-top:2px;text-transform:uppercase">
        {APP_TAGLINE}
    </div>
</div>
""", unsafe_allow_html=True)

    # LLM status badge
    llm_status_badge()
    st.markdown("<br>", unsafe_allow_html=True)

    # Dataset quick-status
    df_raw = st.session_state.get("df_raw")
    if df_raw is not None:
        file_name = st.session_state.get("file_name", "dataset")
        st.markdown(f"""
<div style="background:rgba(196,192,255,.08);border:1px solid rgba(196,192,255,.2);border-radius:.75rem;padding:.75rem 1rem;margin-bottom:1rem;">
    <div style="font-size:0.65rem;color:var(--on-surface-var);letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">Active Dataset</div>
    <div style="font-size:.85rem;font-weight:600;color:var(--on-surface);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{file_name}</div>
    <div style="font-size:.7rem;color:var(--outline);margin-top:2px">{df_raw.shape[0]:,} rows × {df_raw.shape[1]} cols</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)

    pages = {
        "🏠  Upload Dataset":       "upload",
        "🧹  Data Cleaning":         "clean",
        "📊  Analytics Dashboard":  "eda",
        "💡  AI Insights":          "insights",
        "💬  Chat with Dataset":    "chat",
        "🤖  AutoML Workspace":     "automl",
        "📄  Reports & Export":     "reports",
    }

    current_page = st.session_state.get("current_page", "upload")
    selected_label = st.radio(
        "Navigate",
        list(pages.keys()),
        index=list(pages.values()).index(current_page) if current_page in pages.values() else 0,
        label_visibility="collapsed",
    )
    st.session_state.current_page = pages[selected_label]

    # Footer
    st.markdown(f"""
<div style="position:fixed;bottom:1rem;left:1rem;right:1rem;font-size:.65rem;color:var(--outline);text-align:center;letter-spacing:.06em;">
    STITCH v{APP_VERSION} &nbsp;|&nbsp; Privacy-first · Session-isolated
</div>
""", unsafe_allow_html=True)


# ── Main page routing ─────────────────────────────────────────────────────────

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
    # Fallback
    render_upload_page()
