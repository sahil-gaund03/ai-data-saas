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
    mean_squared_error, r2_score,
)
from sklearn.pipeline import Pipeline

from src.config import (
    AUTOML_CV_FOLDS, AUTOML_TEST_SIZE, AUTOML_RANDOM_STATE,
    AUTOML_MAX_FEATURES_SHOWN, CHART_COLORS, COLORS,
)
from src.utils import (
    get_numeric_cols, 
    get_categorical_cols, 
    section_header,
    style_plotly_chart,
    saas_callout
)
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
    """Run AutoML training and evaluation pipeline."""
    df = df.dropna(subset=[target_col]).copy()
    if len(df) < 20:
        raise ValueError("Dataset matrix size insufficient for pipeline splitting (< 20 records remaining).")

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
            logger.warning("Model evaluation drop encountered on component %s: %s", name, exc)
            cv_scores[name] = {"mean": float("nan"), "std": 0.0}

    best_name = max(cv_scores, key=lambda k: cv_scores[k]["mean"] if not np.isnan(cv_scores[k]["mean"]) else -999)
    best_model = models[best_name]
    best_model.fit(X_train, y_train)
    y_pred = best_model.predict(X_test)

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

    if task == "classification":
        metrics = {
            "Accuracy Evaluation": round(float(accuracy_score(y_test, y_pred)), 4),
            "F1 Param (weighted)": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        }
    else:
        metrics = {
            "R² Variance Score": round(float(r2_score(y_test, y_pred)), 4),
            "MAE Metric": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "RMSE Deviation": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
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
        title="Model Cross-Validation Comparison Matrix",
        xaxis_title="Evaluated Baseline Models", yaxis_title="Mean Score Target",
    )
    style_plotly_chart(fig)
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
        title="Feature Contribution Weighting (Best Predictive Model)",
        xaxis_title="Calculated Structural Importance Weight", yaxis_title="",
    )
    style_plotly_chart(fig)
    return fig


# ── Page UI ───────────────────────────────────────────────────────────────────

def render_automl_page() -> None:
    section_header(
        "AUTOML",
        "Automated ML Workspace",
        "Auto-detect validation task structures, compete models, and fetch feature importance summaries.",
    )

    # FIX: Explicit None-check to avoid ambiguous truth value evaluation exceptions
    df = st.session_state.get("df_cleaned")
    if df is None:
        df = st.session_state.get("df_raw")

    if df is None:
        saas_callout("Please upload a raw dataset first to unlock the model hyper-tuning workspaces.", type="info")
        return

    all_cols = list(df.columns)
    suggested = _suggest_target(df)

    with st.expander("⚙️ AutoML Pipeline Hyper-Configuration", expanded=True):
        c1, c2 = st.columns(2)
        target_col = c1.selectbox(
            "Select target output variable",
            all_cols,
            index=all_cols.index(suggested) if suggested in all_cols else len(all_cols) - 1,
        )
        feature_cols = c2.multiselect(
            "Select training feature vectors",
            [c for c in all_cols if c != target_col],
            default=[c for c in all_cols if c != target_col],
        )

    if st.button("🚀 Execute Parallel Training Model Run", use_container_width=True):
        if not feature_cols:
            st.error("Hyper-configuration requires a minimum of 1 input feature vector.")
            return

        with st.spinner("Initializing models, compiling pipelines, and iterating cross-validation splits..."):
            try:
                results = run_automl(df, target_col, feature_cols)
                st.session_state["automl_results"] = results
            except Exception as exc:
                st.error(f"AutoML model execution run mapping aborted: {exc}")
                return

    results = st.session_state.get("automl_results")
    if results is None:
        return

    _render_automl_results(results)


def _render_automl_results(results: dict) -> None:
    saas_callout(f"AutoML modeling run successfully completed. Top algorithmic performer: {results['best_model']}", type="success")
    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Task info chips
    task_chip = "🎯 Classification Workspace" if results["task"] == "classification" else "📈 Regression Workspace"
    st.markdown(
        f'<span class="chip chip-primary">{task_chip}</span> &nbsp; '
        f'<span class="chip chip-success">Top Model: {results["best_model"]}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Test metrics
    st.markdown("#### 📊 Isolated Out-of-Sample Test Set Metrics")
    metric_cols = st.columns(len(results["test_metrics"]))
    for col, (metric, val) in zip(metric_cols, results["test_metrics"].items()):
        col.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-value">{val:.4f}</div>
                <div class="kpi-label">{metric}</div>
            </div>""", 
            unsafe_allow_html=True
        )

    # Model comparison chart
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.plotly_chart(_model_comparison_chart(results["cv_scores"]), use_container_width=True)

    # Feature importance
    if results["feature_importance"]:
        st.plotly_chart(_feature_importance_chart(results["feature_importance"]), use_container_width=True)

    # AI interpretation
    if is_llm_available():
        st.markdown("<hr style='border-color: rgba(196, 192, 255, 0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 🤖 Neural Engine Analytics Interpretation")
        if st.button("✨ Extract Comprehensive Insights For This Model Run", key="automl_ai", use_container_width=True):
            with st.spinner("Gemini is interpreting validation telemetry profiles..."):
                interp = generate_automl_reasoning(
                    results["task"],
                    results["target"],
                    results["cv_scores"],
                    results["feature_importance"],
                )
            st.markdown(
                f'<div class="ai-response"><div class="ai-badge">🤖 AutoML Telemetry Analysis</div>{interp}</div>',
                unsafe_allow_html=True,
            )

