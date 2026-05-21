<div align="center">

<br />

```
███████╗████████╗██╗████████╗ ██████╗██╗  ██╗
██╔════╝╚══██╔══╝██║╚══██╔══╝██╔════╝██║  ██║
███████╗   ██║   ██║   ██║   ██║     ███████║
╚════██║   ██║   ██║   ██║   ██║     ██╔══██║
███████║   ██║   ██║   ██║   ╚██████╗██║  ██║
╚══════╝   ╚═╝   ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
```

### **AI-Powered Data Intelligence Suite**

*Clean · Explore · Understand · Predict*

<br />

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-A855F7?style=flat-square)](CONTRIBUTING.md)

<br />

> **Stitch** is a production-grade data intelligence platform that brings together  
> AI-driven insights, automated cleaning, EDA, and AutoML — in one privacy-first workspace.

<br />

---

</div>

<br />

## ◈ What is Stitch?

Stitch bridges the gap between raw, messy data and actionable intelligence. Upload any CSV, Excel, or JSON file and immediately access a full suite of tools — from one-click data cleaning to natural language querying to automated machine learning — all powered by Gemini AI at the reasoning layer and trusted Python libraries at the compute layer.

**The core philosophy:** LLMs reason, Python crunches. Your raw data never leaves your session.

<br />

## ◈ Feature Overview

<br />

| Module | What it does |
|---|---|
| **📂 Dataset Upload** | Ingest CSV, Excel (`.xlsx`), or JSON — drag-and-drop or file picker |
| **🧹 Auto Cleaning** | Handle missing values, duplicates, dtype coercion, and text normalization |
| **📊 EDA Dashboard** | Interactive histograms, box plots, correlation heatmaps, scatter plots, pie & bar charts |
| **💡 AI Insights** | Gemini analyzes your schema + statistics and generates actionable business narratives |
| **💬 Chat with Data** | Ask questions in plain English → Pandas operations + AI-narrated answers |
| **🤖 AutoML** | Automatic model selection, cross-validation, and feature importance — no code required |
| **🔒 PII Detection** | Regex scan for emails, phone numbers, Aadhaar, PAN, SSN, and credit card patterns |
| **📄 PDF Reports** | One-click downloadable cleaning and analytics reports via ReportLab |
| **⬇️ Export** | Download cleaned data as CSV or Excel |

<br />

---

## ◈ Architecture

```
ai_data_saas/
│
├── app.py                    ← Streamlit entrypoint & page routing
├── requirements.txt
├── .env.example
│
└── src/
    ├── config.py             ← Global constants & colour tokens
    ├── security.py           ← PII detection, session isolation, API key handling
    ├── utils.py              ← Shared helpers & CSS injection
    ├── upload.py             ← File ingestion (CSV / XLSX / JSON)
    ├── cleaner.py            ← Data cleaning engine (pure Pandas)
    ├── eda.py                ← Exploratory charts (Plotly)
    ├── llm_engine.py         ← Gemini API integration layer
    ├── insights.py           ← AI Insights page
    ├── chatbot.py            ← Conversational dataset assistant
    ├── automl.py             ← AutoML with scikit-learn & XGBoost
    └── report_generator.py   ← PDF report generation (ReportLab)
```

<br />

> **Design principle:**  
> The LLM never sees your raw data — only schema, aggregated statistics, and ≤ 5 masked sample rows.  
> All data processing is handled locally by Pandas, NumPy, and Scikit-learn.

<br />

---

## ◈ Quick Start

### 1 · Clone the repository

```bash
git clone https://github.com/yourusername/stitch-ai-data-suite.git
cd stitch-ai-data-suite
```

### 2 · Create a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Configure your API key

```bash
cp .env.example .env
# Open .env and add your Gemini key:
# GEMINI_API_KEY=AIzaSy...your-key-here
```

> Get a free key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — no credit card required.

### 5 · Launch

```bash
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

<br />

---

## ◈ Gemini API Setup

1. Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the generated key
5. Paste it into your `.env` file:
   ```
   GEMINI_API_KEY=AIzaSy...your-key-here
   ```
6. Restart the app

> **Note:** AI features are fully optional. Stitch works without an API key — only the AI Insights page, Chat narration, and AutoML interpretation require Gemini.

<br />

---

## ◈ Deploy for Free (Streamlit Cloud)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "feat: initial Stitch deployment"
git branch -M main
git remote add origin https://github.com/yourusername/stitch-ai-data-suite.git
git push -u origin main
```

### Step 2 — Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Deploy**

### Step 3 — Add your secret

In Streamlit Cloud → your app → **Settings** → **Secrets**:

```toml
GEMINI_API_KEY = "AIzaSy...your-key-here"
```

<br />

---

## ◈ Security & Privacy

| Concern | How Stitch handles it |
|---|---|
| **Session isolation** | Each browser session gets a unique UUID — no shared memory between users |
| **API key safety** | Loaded via `.env` locally; Streamlit Secrets in production — never hardcoded |
| **LLM data exposure** | Only schema + aggregated stats + ≤ 5 masked rows are sent to Gemini |
| **PII detection** | Regex-based scan covers email, phone, SSN, Aadhaar, PAN, credit cards |
| **Temporary files** | `tempfile` module — all session files deleted after processing |
| **Error handling** | Generic messages to users; full stack traces only in server logs |

<br />

---

## ◈ Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| AI features not working | Verify `GEMINI_API_KEY` is set in `.env` or Streamlit Secrets |
| Excel file not parsing | Confirm `openpyxl` is installed: `pip install openpyxl` |
| PDF not generating | Confirm `reportlab` is installed: `pip install reportlab` |
| XGBoost not available | `pip install xgboost` — optional, app falls back to Random Forest + Logistic Regression |
| Large files running slowly | Reduce dataset size, or raise the Streamlit upload limit in `.streamlit/config.toml` |

<br />

---

## ◈ Roadmap

- [ ] Multi-file join & merge support
- [ ] Time-series decomposition (trend, seasonality, residuals)
- [ ] FAISS vector search for semantic data exploration
- [ ] SQLite-backed dataset versioning
- [ ] Scheduled report delivery via email
- [ ] Role-based access control for team plans
- [ ] Plugin system for custom cleaning rules

<br />

---

## ◈ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **UI** | Streamlit |
| **Data** | Pandas · NumPy |
| **Visualisation** | Plotly |
| **ML** | Scikit-learn · XGBoost |
| **AI** | Google Gemini |
| **Reports** | ReportLab |
| **Security** | Python `re` · `tempfile` · `uuid` |

</div>

<br />

---

## ◈ License

```
MIT License — free for personal and commercial use.
```

See [LICENSE](LICENSE) for full text.

<br />

---

<div align="center">

Built with focus, Python, and a little bit of magic.

**[⬆ Back to top](#)**

</div>
