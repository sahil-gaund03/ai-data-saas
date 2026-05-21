"""
llm_engine.py — Gemini API integration for AI reasoning.

LLM is ONLY used for:
  • Natural language insights & summaries
  • Preprocessing recommendations
  • Anomaly explanations
  • Chat with dataset (query → pandas intent → AI narration)
  • AutoML model selection reasoning

The LLM NEVER sees raw data — only sanitised schema + stats + ≤ 5 sample rows.
"""

import json
import logging
from typing import Optional

import streamlit as st

from src.config import GEMINI_MODEL, LLM_MAX_OUTPUT_TOKENS
from src.security import load_api_key, safe_llm_context

logger = logging.getLogger(__name__)

# Lazy-load google-generativeai to avoid hard failure if not installed
_genai = None
_model = None


def _get_model():
    global _genai, _model
    if _model is not None:
        return _model

    try:
        import google.generativeai as genai
        _genai = genai
    except ImportError:
        return None

    api_key = load_api_key()
    if not api_key:
        return None

    try:
        _genai.configure(api_key=api_key)
        _model = _genai.GenerativeModel(GEMINI_MODEL)
        return _model
    except Exception as exc:
        logger.warning("Gemini init failed: %s", exc)
        return None


def is_llm_available() -> bool:
    """Return True if the Gemini model is configured and ready."""
    return _get_model() is not None


def _call_gemini(prompt: str) -> str:
    """Internal: call Gemini and return the text response."""
    model = _get_model()
    if model is None:
        return "__NO_LLM__"
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
                "temperature": 0.4,
            },
        )
        return response.text.strip()
    except Exception as exc:
        logger.warning("Gemini call failed: %s", exc)
        return f"__LLM_ERROR__: {exc}"


# ── Insight prompts ────────────────────────────────────────────────────────────

def generate_dataset_insights(df) -> str:
    """
    Generate a business-oriented AI insight summary for the dataset.
    Only a safe context (schema + stats + 5 rows) is sent.
    """
    ctx = safe_llm_context(df)
    prompt = f"""You are a senior data scientist reviewing a dataset for a business stakeholder.
Here is the dataset metadata (NOT the full data):

{json.dumps(ctx, indent=2)}

Write a concise, insightful analysis (around 300 words) covering:
1. What the dataset appears to represent
2. Key data quality observations
3. Most interesting numeric trends or patterns
4. Top 3 business recommendations based on the data profile
5. Potential risks or data issues to address

Use clear business language. Use markdown formatting. Be specific — mention column names and numbers.
"""
    return _call_gemini(prompt)


def generate_cleaning_recommendations(df) -> str:
    ctx = safe_llm_context(df)
    prompt = f"""You are a data engineering expert reviewing a raw dataset before ML modelling.
Dataset profile:

{json.dumps(ctx, indent=2)}

Provide structured preprocessing recommendations:
1. Which columns to drop and why
2. Missing value strategies per column type
3. Encoding suggestions for categorical columns
4. Feature engineering opportunities
5. Potential target variable candidates

Be concise. Use bullet points. Mention column names explicitly.
"""
    return _call_gemini(prompt)


def generate_automl_reasoning(
    task: str,
    target: str,
    scores: dict,
    feature_importance: dict,
) -> str:
    scores_str = json.dumps(scores, indent=2)
    features_str = json.dumps(dict(list(feature_importance.items())[:10]), indent=2)
    prompt = f"""You are an ML engineer reviewing AutoML results.

Task type: {task}
Target column: {target}
Model scores: {scores_str}
Top 10 feature importances: {features_str}

Provide:
1. Which model performed best and why
2. Interpretation of the top 3 features
3. Recommendations to improve performance
4. Potential overfitting or data leakage risks
5. Next steps for production deployment

Keep it to ~200 words. Use markdown.
"""
    return _call_gemini(prompt)


def answer_chat_question(df, question: str, chat_history: list) -> str:
    """
    Answer a natural language question about the dataset.
    The LLM receives schema + stats + 5 rows + question.
    It returns a markdown-formatted answer.
    """
    ctx = safe_llm_context(df)
    history_str = "\n".join(
        [f"User: {h['question']}\nAssistant: {h['answer'][:300]}…" for h in chat_history[-3:]]
    )
    prompt = f"""You are an expert data analyst assistant. A user is asking questions about their dataset.

Dataset profile (NOT the full data):
{json.dumps(ctx, indent=2)}

Recent conversation:
{history_str if history_str else "(none)"}

User's new question: {question}

Answer concisely and helpfully. If you can derive an answer from the statistics and schema, do so.
If the question requires exact aggregation you can't compute, suggest what pandas code to run.
Use markdown formatting. Be specific with numbers when possible.
"""
    return _call_gemini(prompt)


def _no_llm_fallback(message: str) -> str:
    """Render a friendly fallback when LLM is unavailable."""
    return f"""
<div class="ai-response">
<div class="ai-badge">⚠️ AI Engine Offline</div>
<p>{message}</p>
<p>To enable AI features:<br>
1. Get a free Gemini API key at <a href="https://aistudio.google.com" target="_blank">aistudio.google.com</a><br>
2. Create a <code>.env</code> file and add <code>GEMINI_API_KEY=your_key_here</code><br>
3. Restart the app</p>
</div>
"""


def llm_status_badge() -> None:
    """Show an inline LLM status indicator in the sidebar."""
    if is_llm_available():
        st.sidebar.markdown(
            '<span class="chip chip-success">🤖 AI Online</span>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<span class="chip chip-warning">⚠️ AI Offline — Add GEMINI_API_KEY</span>',
            unsafe_allow_html=True,
        )
