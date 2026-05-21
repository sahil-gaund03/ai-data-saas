# 🔮 Stitch — AI Data Intelligence Suite

> **Production-grade AI-powered data cleaning, EDA, and analytics SaaS platform.**  
> Built with Streamlit · Pandas · Scikit-learn · Gemini AI · Plotly

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 **Dataset Upload** | CSV, Excel, JSON — drag & drop or file browser |
| 🧹 **Auto Cleaning** | Missing values, duplicates, dtype conversion, text cleaning |
| 📊 **EDA Dashboard** | Histograms, box plots, correlation heatmap, scatter, pie/bar |
| 💡 **AI Insights** | Gemini-powered business insights from schema + stats |
| 💬 **Chat with Data** | Natural language queries → Pandas operations + AI narration |
| 🤖 **AutoML** | Auto model selection, cross-validation, feature importance |
| 🔒 **PII Detection** | Scan for emails, phones, Aadhaar, PAN, SSN, credit cards |
| 📄 **PDF Reports** | Downloadable cleaning + analytics reports via ReportLab |
| ⬇️ **Export** | Download cleaned dataset as CSV or Excel |

---

## 🏗️ Architecture

```
ai_data_saas/
├── app.py                  ← Streamlit entrypoint & routing
├── requirements.txt
├── .env.example
│
├── src/
│   ├── config.py           ← Global constants & colour tokens
│   ├── security.py         ← PII detection, session isolation, API key loading
│   ├── utils.py            ← Shared helpers, CSS injection, KPI cards
│   ├── upload.py           ← File ingestion (CSV/XLSX/JSON)
│   ├── cleaner.py          ← Data cleaning engine (Pandas only)
│   ├── eda.py              ← EDA charts (Plotly)
│   ├── llm_engine.py       ← Gemini API integration
│   ├── insights.py         ← AI insights page
│   ├── chatbot.py          ← Conversational dataset assistant
│   ├── automl.py           ← AutoML with scikit-learn / XGBoost
│   └── report_generator.py ← PDF report generation (ReportLab)
│
├── data/                   ← (Optional) sample datasets
├── outputs/                ← Generated output files
└── reports/                ← Generated PDF reports
```

### Key architectural principle

> **LLMs are used ONLY for reasoning and language generation.**  
> All data processing (cleaning, statistics, ML training) is done with **Pandas / NumPy / Scikit-learn**.  
> The LLM never sees raw data — only schema + aggregated statistics + ≤ 5 masked sample rows.

---

## 🚀 Local Setup

### 1. Clone / download

```bash
git clone https://github.com/yourusername/stitch-ai-data-suite.git
cd stitch-ai-data-suite
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

### 5. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 Gemini API Setup (step-by-step)

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key
5. Open your `.env` file and set:
   ```
   GEMINI_API_KEY=AIzaSy...your-key-here
   ```
6. Restart the app

> **Note:** AI features are optional. The app works without an API key — only the AI Insights, Chat narration, and AutoML interpretation require Gemini.

---

## ☁️ Free Deployment (Streamlit Community Cloud)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — Stitch AI Data Suite"
git branch -M main
git remote add origin https://github.com/yourusername/stitch-ai-data-suite.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository and set **Main file** to `app.py`
5. Click **Deploy**

### Step 3 — Add secrets

In Streamlit Cloud:
- Go to your app → **Settings** → **Secrets**
- Add:
  ```toml
  GEMINI_API_KEY = "AIzaSy...your-key-here"
  ```

---

## 🔒 Security & Privacy Design

| Concern | How Stitch Handles It |
|---|---|
| Session isolation | Each browser session gets a unique UUID; no shared memory |
| API key safety | Loaded via `.env` locally, Streamlit Secrets in production |
| LLM data exposure | Only schema + stats + ≤ 5 masked rows sent to Gemini |
| PII detection | Regex-based scan for email, phone, SSN, Aadhaar, PAN, CC |
| Temporary files | `tempfile` module; deleted after processing |
| Error messages | Generic user-facing errors; stack traces only in server logs |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| AI features offline | Check `GEMINI_API_KEY` in `.env` or Streamlit Secrets |
| Excel not parsing | Ensure `openpyxl` is installed |
| PDF not generating | Ensure `reportlab` is installed |
| XGBoost not available | `pip install xgboost` (optional; falls back to RF + LR) |
| Large file slow | Reduce dataset size or increase Streamlit file upload limit |

---

## 🔭 Future Improvements

- [ ] Multi-file join / merge support
- [ ] Time-series decomposition (trend, seasonality)
- [ ] FAISS vector search for semantic data exploration
- [ ] SQLite dataset versioning
- [ ] Scheduled report emails
- [ ] Role-based access control for team plans
- [ ] Plugin system for custom cleaning rules

---

## 📄 License

MIT License — free for personal and commercial use.

---

*Built with ❤️ using Streamlit, Gemini AI, and the Python data stack.*
