<div align="center">

<img src="https://img.shields.io/badge/version-1.0.0-c4c0ff?style=for-the-badge&labelColor=13121b" alt="version"/>
<img src="https://img.shields.io/badge/python-3.10+-d0bcff?style=for-the-badge&logo=python&logoColor=white&labelColor=13121b" alt="python"/>
<img src="https://img.shields.io/badge/streamlit-1.32+-ffb785?style=for-the-badge&logo=streamlit&logoColor=white&labelColor=13121b" alt="streamlit"/>
<img src="https://img.shields.io/badge/license-MIT-6ee7b7?style=for-the-badge&labelColor=13121b" alt="license"/>
<img src="https://img.shields.io/badge/status-active-6ee7b7?style=for-the-badge&labelColor=13121b" alt="status"/>

<br/><br/>

```
███████╗████████╗██╗████████╗ ██████╗██╗  ██╗
██╔════╝╚══██╔══╝██║╚══██╔══╝██╔════╝██║  ██║
███████╗   ██║   ██║   ██║   ██║     ███████║
╚════██║   ██║   ██║   ██║   ██║     ██╔══██║
███████║   ██║   ██║   ██║   ╚██████╗██║  ██║
╚══════╝   ╚═╝   ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
```

### 🔮 AI-Powered Data Intelligence Platform

**Upload · Clean · Explore · Predict · Export — all in one place.**

[🚀 Live Demo](#) · [📖 Docs](#installation) · [🐛 Issues](https://github.com/sahil-gaund03/ai-data-saas/issues) · [⭐ Star this repo](#)

</div>

---

## ✨ What is Stitch?

**Stitch** is a full-stack, session-isolated data science SaaS platform built with Streamlit and Gemini AI. It takes you from raw CSV to ML model, actionable insights, and a polished PDF report — no code required.

> *Privacy-first design: all data lives in your session. Nothing is persisted server-side.*

---

## 🗺️ Platform Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     STITCH AI DATA SUITE                     │
│                                                             │
│  📁 Upload  →  🧹 Clean  →  📊 EDA  →  💡 Insights          │
│                                  ↓                          │
│              📄 Reports  ←  🤖 AutoML  ←  💬 Chat            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Feature Modules

### 📁 1 · Smart Dataset Upload
> Drag-and-drop data ingestion with instant schema detection.

- Supports **CSV, XLSX, XLS, JSON** — up to **200 MB**
- Instant preview table (50-row sample)
- Automatic data-type inference on load
- Session-isolated: your data is yours alone

---

### 🧹 2 · Intelligent Data Cleaning
> Fix messy data in seconds — no pandas expertise required.

| Capability | Detail |
|---|---|
| 🗑️ **Drop high-null columns** | Auto-drops columns with >60% missing values |
| 🔁 **Duplicate removal** | Exact-row deduplication with count reporting |
| 🩹 **Smart fill strategies** | Numeric → median · Categorical → mode · Datetime → ffill |
| 📐 **Type inference** | Coerces strings to numeric/datetime where safe |
| 📈 **Outlier detection** | IQR-based fencing (1.5× multiplier, configurable) |
| 📏 **Normalization** | Min-max scaling or Z-score standardization |
| 🔤 **Text cleaning** | Strip whitespace, lowercase, trim special characters |
| 📋 **Audit log** | Every change logged — reproducible pipeline |

---

### 📊 3 · Analytics Dashboard (EDA)
> Interactive, Plotly-powered charts — dark-themed and publication-ready.

- **Histograms** — distribution for any numeric column, configurable bins
- **Box plots** — outlier visualisation across multiple columns
- **Correlation heatmap** — full Pearson matrix, colour-coded
- **Missing value chart** — column-level null percentage bar chart
- **Scatter plots** — bivariate numeric exploration with trend overlay
- **Pie / bar charts** — categorical frequency breakdown
- **Skewness & kurtosis table** — distributional shape at a glance

---

### 💡 4 · AI Insights (Gemini-Powered)
> Turn statistics into business language — powered by `gemini-2.5-flash`.

```
┌──────────────────────────────────────────────────────┐
│  Tab 1: 💡 Dataset Insights                          │
│  Tab 2: 🔧 Preprocessing Guide                       │
│  Tab 3: 🔒 PII Audit                                 │
└──────────────────────────────────────────────────────┘
```

- **Dataset overview insights** — Gemini reads your schema + stats and writes a business-ready summary
- **Cleaning recommendations** — AI suggests which columns to fix and why
- **Trend analysis** — pattern recognition across numeric features
- **Anomaly explanations** — flags unusual distributions with natural-language context
- **PII detection** — auto-identifies columns that may contain personally identifiable information
- Results cached in session state — no repeated API calls

---

### 💬 5 · Chat with Dataset
> Ask questions about your data in plain English.

**Two-layer architecture:**

```
User Question
     │
     ▼
┌─────────────────────────┐
│  Pandas Resolver        │  ← Fast, free, no LLM
│  (pattern-matched ops)  │
└────────────┬────────────┘
             │ (if unresolved)
             ▼
┌─────────────────────────┐
│  Gemini LLM             │  ← Schema + stats context
│  (natural language)     │
└─────────────────────────┘
```

**Built-in pandas resolvers (zero-latency):**

- Row/column counts
- Missing value reports
- Duplicate detection
- Column averages, min, max
- Value distribution queries

**LLM fallback handles everything else.** Conversation history persisted in session.

---

### 🤖 6 · AutoML Workspace
> Train and compare ML models — no ML expertise required.

**Supported algorithms:**

| Model | Classification | Regression |
|---|---|---|
| Random Forest | ✅ | ✅ |
| Logistic / Linear Regression | ✅ | ✅ |
| Ridge Regression | — | ✅ |
| XGBoost *(if installed)* | ✅ | ✅ |

**Pipeline steps:**
1. 🎯 Auto-detect or manually select target column
2. 🔍 Infer task type: `classification` vs `regression`
3. ⚙️ Preprocess: encode categoricals + fill nulls
4. 🔀 Train/test split (80/20, configurable)
5. 📊 3-fold cross-validation for robust scoring
6. 🏆 Model leaderboard with ranked metrics
7. 📉 Feature importance chart (top 15 features)
8. 🧠 Optional: Gemini-generated model interpretation

**Classification metrics:** Accuracy · F1-score · Classification report  
**Regression metrics:** MAE · RMSE · R²

---

### 📄 7 · Reports & Export
> One-click PDF reports and clean data exports.

**PDF Report contains:**
- Executive summary (shape, quality score, file name)
- Cleaning audit log
- Descriptive statistics table
- Outlier summary
- AI insights section *(if Gemini key configured)*

**Data exports:**
- 📥 Download as **CSV**
- 📥 Download as **Excel (.xlsx)**

> Raw user data is never embedded — only aggregated statistics appear in reports.

---

## 🛡️ Security & Privacy

| Feature | Detail |
|---|---|
| 🔒 **Session isolation** | Per-user `st.session_state` — zero cross-user data leakage |
| 🕵️ **PII detection** | Heuristic column scanner flags sensitive fields |
| 🎭 **PII masking** | Mask character configurable (`*` by default) |
| 🧪 **LLM data minimization** | Only 5 sample rows sent to Gemini (configurable) |
| 📦 **No persistence** | Session data cleared on browser close |

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit 1.32+ |
| **Data** | Pandas 2.0 · NumPy 1.26 |
| **Visualisation** | Plotly 5.20 |
| **ML** | Scikit-learn 1.4 · XGBoost 2.0 |
| **AI / LLM** | Google Gemini 2.5 Flash (`google-generativeai`) |
| **PDF** | ReportLab 4.1 |
| **Vector Search** | FAISS CPU |
| **Exports** | openpyxl |

</div>

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) *(optional — AI features only)*

### 1 · Clone

```bash
git clone https://github.com/sahil-gaund03/ai-data-saas.git
cd ai-data-saas
```

### 2 · Install dependencies

```bash
pip install -r requirements.txt
```

### 3 · Configure environment

```bash
# Create a .env file in the project root
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Or add via Streamlit Secrets (`~/.streamlit/secrets.toml`):

```toml
GEMINI_API_KEY = "your_api_key_here"
```

### 4 · Run

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
ai-data-saas/
├── app.py                  # Streamlit entrypoint — routing + sidebar
├── requirements.txt
└── src/
    ├── config.py           # All constants — thresholds, colours, model params
    ├── security.py         # Session init + PII detection
    ├── utils.py            # Shared helpers — KPI cards, CSS injection, formatters
    ├── llm_engine.py       # Gemini API wrapper — all LLM calls centralised
    ├── upload.py           # Dataset upload page
    ├── cleaner.py          # Data cleaning engine
    ├── eda.py              # EDA charts — Plotly builders
    ├── insights.py         # AI Insights page
    ├── chatbot.py          # Chat with Dataset — pandas resolver + LLM fallback
    ├── automl.py           # AutoML Workspace — model training + evaluation
    └── report_generator.py # PDF report builder (ReportLab)
```

---

## 🗺️ Roadmap

- [ ] 🌐 Multi-file join / merge support
- [ ] 🕒 Time-series forecasting module
- [ ] 🗃️ PostgreSQL / BigQuery connector
- [ ] 📡 Real-time streaming data support
- [ ] 🧩 Plugin API for custom chart types
- [ ] 🔐 OAuth-based user authentication

---

## 🤝 Contributing

Pull requests are welcome!

```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/amazing-feature

# 3. Commit your changes
git commit -m "feat: add amazing feature"

# 4. Push and open a PR
git push origin feature/amazing-feature
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

<div align="center">

Built with 🔮 by **Sahil Gaund**

[![GitHub](https://img.shields.io/badge/GitHub-sahil--gaund03-c4c0ff?style=flat-square&logo=github&labelColor=13121b)](https://github.com/sahil-gaund03)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-sahilgaund03-d0bcff?style=flat-square&logo=linkedin&labelColor=13121b)](https://linkedin.com/in/sahilgaund03)
[![Portfolio](https://img.shields.io/badge/Portfolio-sahilgaund0310.netlify.app-ffb785?style=flat-square&labelColor=13121b)](https://sahilgaund0310.netlify.app)

*If this project helped you, please consider giving it a ⭐*

</div>
