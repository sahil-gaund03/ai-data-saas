"""
chatbot.py — Chat with Dataset module.

Architecture:
  1. User asks a natural language question
  2. We attempt to resolve it via pandas operations (fast, free, no LLM)
  3. If resolution succeeds, we show the result + ask LLM to narrate
  4. If resolution fails, LLM answers from schema/stats context
  5. Conversation history persisted in session_state
"""

import re
import logging
from typing import Optional

import pandas as pd
import streamlit as st
import plotly.express as px

from src.llm_engine import answer_chat_question, is_llm_available
from src.utils import section_header, get_numeric_cols, get_categorical_cols
from src.config import CHART_COLORS, PLOTLY_TEMPLATE, COLORS

logger = logging.getLogger(__name__)

# ── Pandas resolver — handles simple questions without LLM ─────────────────────

def _try_pandas_resolve(df: pd.DataFrame, question: str) -> Optional[dict]:
    """
    Attempt to answer the question via pattern-matched pandas operations.
    Returns {"text": str, "chart": fig_or_None} or None if unresolvable.
    """
    q = question.lower().strip()
    num_cols = get_numeric_cols(df)
    cat_cols = get_categorical_cols(df)

    # ── Row / column count ──
    if re.search(r"how many (rows|records)", q):
        return {"text": f"The dataset has **{len(df):,} rows**.", "chart": None}
    if re.search(r"how many (columns|features|fields)", q):
        return {"text": f"The dataset has **{len(df.columns)} columns**: {', '.join(df.columns[:10])}{'…' if len(df.columns) > 10 else ''}.", "chart": None}

    # ── Missing values ──
    if re.search(r"missing|null|nan|empty", q):
        null_counts = df.isnull().sum()
        null_pct = (df.isnull().mean() * 100).round(2)
        top = null_pct[null_pct > 0].sort_values(ascending=False)
        if top.empty:
            return {"text": "✅ **No missing values** found in this dataset.", "chart": None}
        rows = "\n".join([f"- **{col}**: {pct}% missing ({null_counts[col]:,} rows)" for col, pct in top.items()])
        return {"text": f"**Missing values detected:**\n{rows}", "chart": None}

    # ── Duplicate rows ──
    if re.search(r"duplicate", q):
        n = df.duplicated().sum()
        pct = n / len(df) * 100
        return {"text": f"There are **{n:,} duplicate rows** ({pct:.1f}% of the dataset).", "chart": None}

    # ── Average / mean ──
    m = re.search(r"(average|mean)\s+(?:of\s+)?(.+)", q)
    if m:
        target = m.group(2).strip()
        matched = _find_col(df, target, num_cols)
        if matched:
            val = df[matched].mean()
            return {"text": f"The **mean of `{matched}`** is **{val:,.4f}**.", "chart": None}

    # ── Sum ──
    m = re.search(r"(total|sum)\s+(?:of\s+)?(.+)", q)
    if m:
        target = m.group(2).strip()
        matched = _find_col(df, target, num_cols)
        if matched:
            val = df[matched].sum()
            return {"text": f"The **total of `{matched}`** is **{val:,.2f}**.", "chart": None}

    # ── Max / Min ──
    m = re.search(r"(highest|maximum|max|largest)\s+(.+)", q)
    if m:
        target = m.group(2).strip()
        matched = _find_col(df, target, num_cols)
        if matched:
            val = df[matched].max()
            idx = df[matched].idxmax()
            return {"text": f"**Maximum `{matched}`**: {val:,.4f} (row {idx}).", "chart": None}

    m = re.search(r"(lowest|minimum|min|smallest)\s+(.+)", q)
    if m:
        target = m.group(2).strip()
        matched = _find_col(df, target, num_cols)
        if matched:
            val = df[matched].min()
            idx = df[matched].idxmin()
            return {"text": f"**Minimum `{matched}`**: {val:,.4f} (row {idx}).", "chart": None}

    # ── Value counts / top values ──
    m = re.search(r"(top|most common|frequent).+(values?|categories?)\s+(?:in|of|for)?\s*(.+)", q)
    if m:
        target = m.group(3).strip()
        matched = _find_col(df, target, cat_cols + num_cols)
        if matched:
            vc = df[matched].value_counts().head(10)
            rows = "\n".join([f"- **{k}**: {v:,}" for k, v in vc.items()])
            fig = px.bar(
                x=vc.index.astype(str).tolist(), y=vc.values.tolist(),
                color_discrete_sequence=[COLORS["primary"]],
                labels={"x": matched, "y": "Count"},
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e4e1ee"),
            )
            return {"text": f"**Top values in `{matched}`:**\n{rows}", "chart": fig}

    # ── Correlation between two columns ──
    m = re.search(r"corr(?:elation)?\s+(?:between\s+)?(.+?)\s+and\s+(.+)", q)
    if m:
        c1_name, c2_name = m.group(1).strip(), m.group(2).strip()
        c1 = _find_col(df, c1_name, num_cols)
        c2 = _find_col(df, c2_name, num_cols)
        if c1 and c2:
            corr = df[c1].corr(df[c2])
            strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
            direction = "positive" if corr > 0 else "negative"
            return {
                "text": f"The **correlation** between `{c1}` and `{c2}` is **{corr:.4f}** ({strength} {direction}).",
                "chart": None,
            }

    return None  # Could not resolve with pandas


def _find_col(df: pd.DataFrame, target: str, pool: list[str]) -> Optional[str]:
    """Find the best matching column name for a target string."""
    target_lower = target.lower().strip()
    # Exact match
    for col in pool:
        if col.lower() == target_lower:
            return col
    # Partial match
    for col in pool:
        if target_lower in col.lower() or col.lower() in target_lower:
            return col
    return None


# ── Page UI ────────────────────────────────────────────────────────────────────

def render_chat_page() -> None:
    section_header(
        "CHAT",
        "Conversational Dataset Assistant",
        "Ask anything about your data in plain English. Powered by Gemini + Pandas.",
    )

    # Explicitly check for None to prevent ambiguous DataFrame truth value evaluation
    df = st.session_state.get("df_cleaned")
    if df is None:
        df = st.session_state.get("df_raw")

    if df is None:
        st.info("⬆️ Upload a dataset first.")
        return

    if not is_llm_available():
        st.warning("⚠️ Gemini API key not set. Only Pandas-resolvable questions will be answered.")

    # Render chat history
    history: list = st.session_state.get("chat_history", [])

    # Example prompts
    st.markdown("#### 💬 Suggested Questions")
    suggestions = [
        "How many missing values are there?",
        "What are the top 5 most frequent values?",
        "Show the correlation between numeric columns",
        "How many duplicate rows?",
        "What is the average of each numeric column?",
    ]
    cols = st.columns(len(suggestions))
    for i, (col, sug) in enumerate(zip(cols, suggestions)):
        if col.button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state["chat_input_prefill"] = sug
            st.rerun()

    st.markdown("---")

    # Chat input
    prefill = st.session_state.pop("chat_input_prefill", "")
    question = st.chat_input("Ask a question about your dataset…")
    if question is None and prefill:
        question = prefill

    if question:
        # Attempt pandas resolution
        pandas_result = _try_pandas_resolve(df, question)

        if pandas_result:
            answer_text = pandas_result["text"]
            chart = pandas_result.get("chart")
        elif is_llm_available():
            with st.spinner("Gemini is thinking…"):
                answer_text = answer_chat_question(df, question, history)
            chart = None
        else:
            answer_text = (
                "❓ I couldn't resolve this question with Pandas alone and the AI engine is offline.\n\n"
                "Try questions like:\n"
                "- 'How many missing values?'\n"
                "- 'Average of [column name]'\n"
                "- 'Top values in [column name]'"
            )
            chart = None

        history.append({"question": question, "answer": answer_text, "chart": chart})
        st.session_state.chat_history = history

    # Render conversation
    for turn in history:
        with st.chat_message("user"):
            st.markdown(turn["question"])
        with st.chat_message("assistant"):
            st.markdown(turn["answer"])
            if turn.get("chart"):
                st.plotly_chart(turn["chart"], use_container_width=True)

    # Clear button
    if history:
        if st.button("🗑️ Clear Conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
