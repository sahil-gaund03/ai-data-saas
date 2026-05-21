"""
automl.py — AutoML Workspace.

Uses scikit-learn (+ XGBoost if available) for:
  • Automatic target column detection
  • Task type inference (classification vs regression)
  • Model comparison with cross-validation
  • Evaluation metrics
  • Feature importance chart

Pure ML — no LLM for training/evaluation.
LLM used only for interpreting results (optional).
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, mean_absolute_error,
    mean_squared_error, r2_score, classification_report,
)
from sklearn.pipeline import Pipeline

from src.config import (
    AUTOML_CV_FOLDS, AUTOML_TEST_SIZE, AUTOML_RANDOM_STATE,
    AUTOML_MAX_FEATURES_SHOWN, CHART_COLORS, PLOTLY_TEMPLATE, COLORS,
)
from src.utils import get_numeric_cols, get_categorical_cols, section_header
from src.llm_engine import generate_automl_reasoning, is_llm_available

logger = logging.getLogger(__name__)

# Optional XGBoost
try:
    from xgboost import XGBClassifier, XGBRegressor
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _infer_task(target_series: pd.Series) -> str:
    """Return 'classification' or 'regression'."""
    n_unique = target_series.nunique()
    if pd.api.types.is_numeric_dtype(target_series) and n_unique > 15:
        return "regression"
    return "classification"


def _suggest_target(df: pd.DataFrame) -> Optional[str]:
    """Heuristically suggest a target column."""
    candidates = ["target", "label", "class", "y", "output", "result",
                  "outcome", "price", "salary", "revenue", "churn", "fraud"]
    lower_cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_cols:
            return lower_cols[cand]
    # Last column as fallback
    return df.columns[-1] if len(df.columns) > 1 else None


def _preprocess_features(X: pd.DataFrame) -> pd.DataFrame:
    """Simple preprocessing: encode categoricals, fill nulls."""
    X = X.copy()
    for col in X.select_dtypes(include="object").columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    X = X.fillna(X.median(numeric_only=True))
    return X


def _build_models(task: str) -> dict:
    models = {}

    if task == "classification":
        models["Random Forest"] = RandomForestClassifier(
            n_estimators=100, random_state=AUTOML_RANDOM_STATE, n_jobs=-1
        )
        models["Logistic Regression"] = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, random_state=AUTOML_RANDOM_STATE)),
        ])
        if _HAS_XGB:
            models["XGBoost"] = XGBClassifier(
                n_estimators=100, random_state=AUTOML_RANDOM_STATE,
                eval_metric="logloss", verbosity=0,
            )
    else:
        models["Random Forest"] = RandomForestRegressor(
            n_estimators=100, random_state=AUTOML_RANDOM_STATE, n_jobs=-1
        )
        models["Ridge Regression"] = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", Ridge()),
        ])
        models["Linear Regression"] = LinearRegression()
        if _HAS_XGB:
            models["XGBoost"] = XGBRegressor(
                n_estimators=100, random_state=AUTOML_RANDOM_STATE, verbosity=0,
            )
    return models


def run_automl(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: Optional[list] = None,
) -> dict:
    """
    Run AutoML pipeline. Returns a results dict with:
      model_scores, best_model, feature_importance, task, X_test, y_test, best_estimator
    """
    df = df.dropna(subset=[target_col]).copy()
    if len(df) < 20:
        raise ValueError("Dataset too small for AutoML (< 20 rows after dropping nulls).")

    feature_cols = feature_cols or [c for c in df.columns if c != target_col]
    X = _preprocess_features(df[feature_cols])
    y = df[target_col].copy()
    task = _infer_task(y)

    if task == "classification":
        le = LabelEncoder()
        y = pd.Series(le.fit_transform(y.astype(str)), index=y.index)
        scoring = "accuracy"
    else:
        scoring = "r2"

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=AUTOML_TEST_SIZE, random_state=AUTOML_RANDOM_STATE
    )

    models = _build_models(task)
    cv_scores: dict = {}

    for name, model in models.items():
        try:
            scores = cross_val_score(model, X_train, y_train, cv=AUTOML_CV_FOLDS, scoring=scoring)
            cv_scores[name] = {
                "mean": round(float(scores.mean()), 4),
                "std": round(float(scores.std()), 4),
            }
        except Exception as exc:
            logger.warning("Model %s failed: %s", name, exc)
            cv_scores[name] = {"mean": float("nan"), "std": 0.0}

    # Best model (by mean CV score)
    best_name = max(cv_scores, key=lambda k: cv_scores[k]["mean"] if not np.isnan(cv_scores[k]["mean"]) else -999)
    best_model = models[best_name]
    best_model.fit(X_train, y_train)
    y_pred = best_model.predict(X_test)

    # Feature importance (RF only; skip pipelines for simplicity)
    feature_importance: dict = {}
    try:
        if hasattr(best_model, "feature_importances_"):
            imps = best_model.feature_importances_
            fi = dict(sorted(
                zip(feature_cols, imps), key=lambda x: x[1], reverse=True
            )[:AUTOML_MAX_FEATURES_SHOWN])
            feature_importance = {k: round(float(v), 4) for k, v in fi.items()}
    except Exception:
        pass

    # Test metrics
    if task == "classification":
        metrics = {
            "Accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "F1 (weighted)": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        }
    else:
        metrics = {
            "R²": round(float(r2_score(y_test, y_pred)), 4),
            "MAE": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
        }

    return {
        "task": task,
        "target": target_col,
        "cv_scores": cv_scores,
        "best_model": best_name,
        "test_metrics": metrics,
        "feature_importance": feature_importance,
        "n_features": len(feature_cols),
        "n_samples": len(df),
    }


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _model_comparison_chart(cv_scores: dict) -> go.Figure:
    names = list(cv_scores.keys())
    means = [cv_scores[n]["mean"] for n in names]
    stds = [cv_scores[n]["std"] for n in names]

    fig = go.Figure(go.Bar(
        x=names,
        y=means,
        error_y=dict(type="data", array=stds, visible=True, color=COLORS["outline"]),
        marker_color=CHART_COLORS[:len(names)],
        text=[f"{m:.3f}" for m in means],
        textposition="outside",
    ))
    fig.update_layout(
        title="Model Comparison — CV Score (mean ± std)",
        xaxis_title="Model", yaxis_title="CV Score",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Geist, sans-serif", color="#e4e1ee"),
        margin=dict(t=50, b=40),
    )
    return fig


def _feature_importance_chart(fi: dict) -> go.Figure:
    sorted_fi = dict(sorted(fi.items(), key=lambda x: x[1]))
    fig = go.Figure(go.Bar(
        y=list(sorted_fi.keys()),
        x=list(sorted_fi.values()),
        orientation="h",
        marker_color=COLORS["primary"],
        text=[f"{v:.3f}" for v in sorted_fi.values()],
        textposition="outside",
    ))
    fig.update_layout(
        title="Feature Importance",
        xaxis_title="Importance", yaxis_title="",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Geist, sans-serif", color="#e4e1ee"),
        margin=dict(t=50, b=40, l=150),
    )
    return fig


# ── Page UI ───────────────────────────────────────────────────────────────────

def render_automl_page() -> None:
    section_header(
        "AUTOML",
        "Automated ML Workspace",
        "Auto-detect task type, compare models, and get AI-powered recommendations.",
    )

   # Explicitly check for None to prevent ambiguous DataFrame truth value evaluation
    df = st.session_state.get("df_cleaned")
    if df is None:
        df = st.session_state.get("df_raw")

    if df is None:
        st.info("⬆️ Upload a dataset first.")
        return

    all_cols = list(df.columns)
    suggested = _suggest_target(df)

    with st.expander("⚙️ AutoML Configuration", expanded=True):
        c1, c2 = st.columns(2)
        target_col = c1.selectbox(
            "Target column",
            all_cols,
            index=all_cols.index(suggested) if suggested in all_cols else len(all_cols) - 1,
        )
        feature_cols = c2.multiselect(
            "Feature columns",
            [c for c in all_cols if c != target_col],
            default=[c for c in all_cols if c != target_col],
        )

    if st.button("🚀 Run AutoML", use_container_width=True):
        if not feature_cols:
            st.error("Please select at least one feature column.")
            return

        with st.spinner("Training and evaluating models… this may take a moment."):
            try:
                results = run_automl(df, target_col, feature_cols)
                st.session_state["automl_results"] = results
            except Exception as exc:
                st.error(f"AutoML failed: {exc}")
                return

    results = st.session_state.get("automl_results")
    if results is None:
        return

    _render_automl_results(results)


def _render_automl_results(results: dict) -> None:
    from src.utils import kpi_card, fmt_number

    st.success(f"✅ AutoML complete! Best model: **{results['best_model']}**")
    st.markdown("<br>", unsafe_allow_html=True)

    # Task info
    task_chip = "🎯 Classification" if results["task"] == "classification" else "📈 Regression"
    st.markdown(
        f'<span class="chip chip-primary">{task_chip}</span> &nbsp; '
        f'<span class="chip chip-success">Best: {results["best_model"]}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Test metrics
    st.markdown("#### 📊 Test Set Metrics")
    metric_cols = st.columns(len(results["test_metrics"]))
    for col, (metric, val) in zip(metric_cols, results["test_metrics"].items()):
        col.metric(metric, f"{val:.4f}")

    # Model comparison chart
    st.markdown("---")
    st.plotly_chart(_model_comparison_chart(results["cv_scores"]), use_container_width=True)

    # Feature importance
    if results["feature_importance"]:
        st.plotly_chart(_feature_importance_chart(results["feature_importance"]), use_container_width=True)

    # AI interpretation
    if is_llm_available():
        st.markdown("---")
        st.markdown("#### 🤖 AI Model Interpretation")
        if st.button("✨ Generate AI Insights for These Results", key="automl_ai"):
            with st.spinner("Gemini is interpreting results…"):
                interp = generate_automl_reasoning(
                    results["task"],
                    results["target"],
                    results["cv_scores"],
                    results["feature_importance"],
                )
            st.markdown(
                f'<div class="ai-response"><div class="ai-badge">🤖 AutoML Interpretation</div>{interp}</div>',
                unsafe_allow_html=True,
            )
