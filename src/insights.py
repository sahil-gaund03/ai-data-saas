"""
insights.py — AI Insights page.

Calls Gemini via llm_engine for:
  • Dataset overview insights
  • Cleaning recommendations
  • Trend analysis
  • Anomaly explanations

Results are cached in session_state to avoid repeated API calls.
"""

import streamlit as st

from src.llm_engine import (
    generate_dataset_insights,
    generate_cleaning_recommendations,
    is_llm_available,
)
from src.utils import section_header, data_quality_score, quality_label, kpi_card
from src.config import COLORS
from src.security import detect_pii_columns


def render_insights_page() -> None:
    section_header(
        "AI INSIGHTS",
        "Neural Intelligence Engine",
        "Gemini-powered business insights from your dataset schema and statistics.",
    )

    # Explicitly check for None to avoid Pandas ambiguous truth value evaluation
    df = st.session_state.get("df_cleaned")
    if df is None:
        df = st.session_state.get("df_raw")

    if df is None:
        st.info("⬆️ Upload a dataset first.")
        return

    if not is_llm_available():
        st.warning(
            "⚠️ **Gemini API key not configured.** "
            "Add `GEMINI_API_KEY` to your `.env` file or Streamlit Secrets to enable AI insights."
        )
        _render_static_insights(df)
        return

    _render_ai_insights(df)


def _render_ai_insights(df) -> None:
    cache = st.session_state.get("insights_cache", {})

    tab1, tab2, tab3 = st.tabs(["💡 Dataset Insights", "🔧 Preprocessing Guide", "🔒 PII Audit"])

    with tab1:
        st.markdown("#### 💡 AI Dataset Analysis")
        if "dataset_insights" not in cache:
            if st.button("✨ Generate AI Insights", use_container_width=True, key="gen_insights"):
                with st.spinner("Gemini is analysing your dataset…"):
                    result = generate_dataset_insights(df)
                    cache["dataset_insights"] = result
                    st.session_state.insights_cache = cache
        if "dataset_insights" in cache:
            insight_text = cache["dataset_insights"]
            if insight_text.startswith("__"):
                st.error("AI engine returned an error. Check your API key and quota.")
            else:
                st.markdown(
                    f'<div class="ai-response"><div class="ai-badge">🤖 Gemini Analysis</div>{insight_text}</div>',
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("#### 🔧 Preprocessing Recommendations")
        if "cleaning_recs" not in cache:
            if st.button("🔧 Generate Recommendations", use_container_width=True, key="gen_recs"):
                with st.spinner("Generating preprocessing guide…"):
                    result = generate_cleaning_recommendations(df)
                    cache["cleaning_recs"] = result
                    st.session_state.insights_cache = cache
        if "cleaning_recs" in cache:
            recs_text = cache["cleaning_recs"]
            if recs_text.startswith("__"):
                st.error("AI engine returned an error.")
            else:
                st.markdown(
                    f'<div class="ai-response"><div class="ai-badge">🔧 Engineering Recommendations</div>{recs_text}</div>',
                    unsafe_allow_html=True,
                )

    with tab3:
        _render_pii_audit(df)


def _render_static_insights(df) -> None:
    """Show computed (non-LLM) insights when AI is offline."""
    score, (label, colour) = data_quality_score(df), quality_label(data_quality_score(df))
    null_pct = df.isnull().mean().mean() * 100
    dupe_pct = df.duplicated().mean() * 100

    st.markdown("### 📊 Statistical Insights (No AI required)")

    cols = st.columns(3)
    cols[0].markdown(kpi_card("Quality Score", f"{score}", colour=colour), unsafe_allow_html=True)
    cols[1].markdown(kpi_card("Missing Data", f"{null_pct:.1f}%"), unsafe_allow_html=True)
    cols[2].markdown(kpi_card("Duplicate Rows", f"{dupe_pct:.1f}%"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 Describe")
    st.dataframe(df.describe(include="all").T, use_container_width=True)


def _render_pii_audit(df) -> None:
    st.markdown("#### 🔒 PII Detection Audit")
    st.caption("Scans column content for personally identifiable information. Data never leaves your session.")

    with st.spinner("Scanning for PII…"):
        pii_findings = detect_pii_columns(df)

    if not pii_findings:
        st.success("✅ No PII detected in the dataset columns.")
        return

    st.warning(f"⚠️ Potential PII found in **{len(pii_findings)}** column(s).")
    for col, types in pii_findings.items():
        st.markdown(
            f'<span class="chip chip-error">🔴 {col}</span> — '
            f'PII types: {", ".join(types)}',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.info(
        "💡 **Recommendation:** Consider masking or removing these columns before sharing "
        "the dataset or sending it to any external service."
    )
