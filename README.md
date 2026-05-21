<div align="center">

# 🔮 Stitch — AI Data Suite

### *Advanced AI-Powered Data Intelligence & Automated Machine Learning Platform*

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.14-c4c0ff?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Model Engine](https://img.shields.io/badge/Gemini%20Engine-2.5--Flash-d0bcff?style=for-the-badge&logo=google-gemini&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-6ee7b7?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Stitch** is a privacy-first, session-isolated data intelligence SaaS ecosystem. It seamlessly bridges the gap between raw datasets, business intelligence insights, and production-grade machine learning pipelines through a premium, dark-mode glassmorphic interface.

[Explore Features](#-workspace-modules) • [Installation](#-quick-start) • [Architecture](#%EF%B8%8F-technical-stack) • [Deployment](#-deployment-handbook)

</div>

---

## 🌟 Key Highlights

* 🛡️ **Privacy-First Design**: Raw datasets never leave your localized memory context. The AI engine receives only sanitized statistical schemas and minimal telemetry.
* 🔮 **Glassmorphism UI/UX**: Outfitted with responsive metric grids, modern neomorphic layout cards, custom scroll tracking, and intuitive dark micro-UI components.
* ⚡ **Hybrid Chat Core**: Uses a dual-engine architecture that pattern-matches queries to deterministic Pandas rules for speed, falling back to Gemini for generative narration.

---

## 🎛️ Workspace Modules

### 1. 🏠 Smart Dataset Ingestion (`upload`)
* Supports rapid intake of unstructured or structured `.csv`, `.xlsx`, `.xls`, and `.json` file formats up to 200MB.
* Generates immediate high-speed structured previews with deep session isolation state variables.

### 2. 🧹 Data Cleaning Engine (`clean`)
* Handles missing values using rule-based strategies, eliminates duplicate records, and applies standard IQR outlier fences ($1.5 \times \text{IQR}$).
* Detects high-cardinality bounds ($>50$ unique entries) to safely protect downstream encoding models from dimensionality explosion.

### 3. 📊 Analytics Dashboard (`eda`)
* Renders descriptive parameter statistics alongside high-performance dark-theme Plotly visualizations.
* Includes built-in automated formatting for numbers and percentages with structured data quality validation.

### 4. 💡 Neural Intelligence Engine (`insights`)
* Generates business-oriented summaries and data quality reports using the `gemini-2.5-flash` model.
* Runs an integrated PII (Personally Identifiable Information) audit scan to identify sensitive structural items.

### 5. 💬 Conversational Dataset Assistant (`chat`)
* Provides natural language querying powered by a combined **Pandas Core + Gemini Execution Pipeline**.
* Features optimized query suggestion grids and rich context retention across active sessions.

### 6. 🤖 Automated Machine Learning Workspace (`automl`)
* Automatically detects task types (Classification vs. Regression) and infers target attributes.
* Trains and evaluates models—including Random Forests, Linear/Ridge implementations, and XGBoost—using stratified $k$-fold cross-validation ($k=3$).

### 7. 📄 Executive Reports & Export (`reports`)
* Compiles analytical telemetry and data processing results into enterprise-ready PDF artifacts.
* Supports full-frame structured exports for both clean `.csv` schemas and Excel workbook sheets.

---

## 🛠️ Technical Stack

```mermaid
graph TD
    A[Data Input: CSV/XLSX/JSON] --> B[Streamlit Core UI]
    B --> C[Data Processing: Pandas & NumPy]
    B --> D[ML Pipeline: Scikit-Learn & XGBoost]
    B --> E[Neural Layer: Gemini 2.5 API]
    C --> F[Visuals: Plotly Dark Engine]
    D --> G[Reports: ReportLab PDF Engine]
