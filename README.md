<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Stitch — AI Data Intelligence Suite</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,400;0,500;1,400&family=Syne:wght@400;500;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300&display=swap"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0a12;
  --bg2:#131220;
  --bg3:#1c1b2b;
  --bg4:#222132;
  --border:rgba(196,192,255,.1);
  --border2:rgba(196,192,255,.2);
  --border3:rgba(196,192,255,.35);
  --primary:#c4c0ff;
  --secondary:#d0bcff;
  --accent:#ffb785;
  --success:#6ee7b7;
  --text:#e4e1ee;
  --muted:#918fa1;
  --dim:#524f65;
  --red:#ffb4ab;
}
html{scroll-behavior:smooth}
body{
  font-family:'Syne',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
}

/* ── HERO ── */
.hero{
  position:relative;
  padding:5rem 4rem 4rem;
  overflow:hidden;
  border-bottom:1px solid var(--border);
}
.hero-grid{
  position:absolute;inset:0;
  background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(ellipse 90% 80% at 50% 0%,black 10%,transparent 75%);
}
.hero-glow{
  position:absolute;width:700px;height:350px;
  background:radial-gradient(ellipse,rgba(196,192,255,.055) 0%,transparent 70%);
  top:-120px;left:50%;transform:translateX(-50%);
  pointer-events:none;
}
.hero-inner{position:relative;z-index:1;max-width:900px}
.pill{
  display:inline-flex;align-items:center;gap:8px;
  font-size:10px;letter-spacing:.18em;text-transform:uppercase;font-weight:500;
  color:var(--primary);border:1px solid rgba(196,192,255,.25);
  background:rgba(196,192,255,.06);padding:5px 14px;border-radius:100px;
  margin-bottom:1.75rem;
}
.pill-dot{width:6px;height:6px;border-radius:50%;background:var(--primary);animation:blink 2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.35}}
h1{
  font-size:clamp(3rem,8vw,6rem);font-weight:800;
  letter-spacing:-.05em;line-height:.92;
  background:linear-gradient(140deg,#fff 0%,var(--primary) 45%,var(--secondary) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:.35rem;
}
.tagline{
  font-size:13px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin-bottom:1.5rem;
}
.hero-desc{
  font-family:'Fraunces',serif;font-weight:300;font-size:1.1rem;
  color:rgba(228,225,238,.7);line-height:1.7;max-width:580px;
  margin-bottom:2rem;
}
.badge-row{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:2.25rem}
.badge{
  font-size:10px;letter-spacing:.09em;text-transform:uppercase;font-weight:500;
  padding:4px 10px;border-radius:4px;border:1px solid;
}
.b-blue{color:#93c5fd;border-color:rgba(147,197,253,.28);background:rgba(147,197,253,.06)}
.b-purple{color:var(--primary);border-color:rgba(196,192,255,.28);background:rgba(196,192,255,.06)}
.b-orange{color:var(--accent);border-color:rgba(255,183,133,.28);background:rgba(255,183,133,.06)}
.b-green{color:var(--success);border-color:rgba(110,231,183,.28);background:rgba(110,231,183,.06)}
.b-pink{color:#f9a8d4;border-color:rgba(249,168,212,.28);background:rgba(249,168,212,.06)}
.btn-row{display:flex;gap:12px;flex-wrap:wrap}
.btn{
  font-family:'Syne',sans-serif;
  font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;
  padding:10px 22px;border-radius:6px;border:none;cursor:pointer;
  text-decoration:none;display:inline-flex;align-items:center;gap:8px;
  transition:all .2s;
}
.btn-primary{background:var(--primary);color:#0b0a12}
.btn-primary:hover{background:#b5b0ff;transform:translateY(-1px)}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border2)}
.btn-ghost:hover{border-color:var(--border3);background:rgba(196,192,255,.07)}

/* ── STAT BAR ── */
.stats{display:grid;grid-template-columns:repeat(5,1fr);border-bottom:1px solid var(--border)}
.stat{
  padding:1.5rem 2rem;
  border-right:1px solid var(--border);
  transition:background .2s;
}
.stat:last-child{border-right:none}
.stat:hover{background:rgba(196,192,255,.03)}
.stat-n{font-size:2.1rem;font-weight:800;letter-spacing:-.04em;line-height:1}
.stat-n sup{font-size:1rem;color:var(--primary)}
.stat-l{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-top:5px}

/* ── NAV ── */
.sticky-nav{
  position:sticky;top:0;z-index:100;
  display:flex;align-items:center;gap:0;
  background:rgba(11,10,18,.92);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  padding:0 2rem;
  overflow-x:auto;
}
.nav-link{
  font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;
  padding:14px 16px;color:var(--dim);
  border-bottom:2px solid transparent;
  text-decoration:none;white-space:nowrap;
  transition:all .18s;
}
.nav-link:hover{color:var(--text)}
.nav-link.active{color:var(--primary);border-bottom-color:var(--primary)}

/* ── SECTIONS ── */
section{padding:3.5rem 4rem;border-bottom:1px solid var(--border);max-width:1100px;margin:0 auto}
.section-label{
  font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--primary);font-weight:600;
  display:flex;align-items:center;gap:12px;margin-bottom:2rem;
}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
h2{font-size:1.7rem;font-weight:800;letter-spacing:-.03em;margin-bottom:.5rem}
.sub{font-family:'Fraunces',serif;font-weight:300;color:rgba(228,225,238,.6);font-size:1rem;line-height:1.6;margin-bottom:2rem}

/* ── FEATURES ── */
.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.fcard{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:12px;padding:1.4rem;
  transition:border-color .2s,transform .2s;
  cursor:default;
}
.fcard:hover{border-color:var(--border2);transform:translateY(-3px)}
.ficon{
  width:38px;height:38px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;margin-bottom:.9rem;
}
.fi-p{background:rgba(196,192,255,.12);color:var(--primary)}
.fi-o{background:rgba(255,183,133,.12);color:var(--accent)}
.fi-g{background:rgba(110,231,183,.12);color:var(--success)}
.fi-b{background:rgba(147,197,253,.12);color:#93c5fd}
.fi-k{background:rgba(249,168,212,.12);color:#f9a8d4}
.fi-y{background:rgba(253,230,138,.12);color:#fde68a}
.fname{font-size:13px;font-weight:700;letter-spacing:-.01em;margin-bottom:5px}
.fdesc{font-size:12px;color:var(--muted);line-height:1.6}
.ftags{display:flex;flex-wrap:wrap;gap:4px;margin-top:10px}
.ftag{
  font-size:9px;letter-spacing:.07em;text-transform:uppercase;
  padding:2px 7px;border-radius:3px;
  background:rgba(196,192,255,.06);color:var(--dim);border:1px solid var(--border);
}

/* ── ARCHITECTURE ── */
.arch-wrap{display:grid;grid-template-columns:1fr 1.1fr;gap:2rem;align-items:start}
.mono-tree{
  font-family:'DM Mono',monospace;font-size:12px;line-height:2;
  color:var(--muted);background:var(--bg2);
  border:1px solid var(--border);border-radius:12px;
  padding:1.5rem;overflow-x:auto;
}
.t-dir{color:var(--primary);font-weight:500}
.t-file{color:var(--text)}
.t-hl{color:var(--accent)}
.t-cm{color:var(--dim)}
.principle{
  border-left:3px solid var(--primary);
  background:rgba(196,192,255,.05);border-radius:0 8px 8px 0;
  padding:1.1rem 1.3rem;margin-bottom:1.25rem;
  font-family:'Fraunces',serif;font-size:.95rem;font-weight:300;font-style:italic;
  color:rgba(228,225,238,.75);line-height:1.65;
}
.module-list{display:flex;flex-direction:column;gap:9px}
.module{
  display:grid;grid-template-columns:140px 1fr;gap:12px;
  background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:.75rem 1rem;font-size:12px;align-items:center;
}
.module-name{font-family:'DM Mono',monospace;color:var(--primary);font-size:11px}
.module-desc{color:var(--muted);line-height:1.4}

/* ── SETUP ── */
.steps{display:flex;flex-direction:column}
.step{display:grid;grid-template-columns:52px 1fr;gap:0 1.2rem}
.step-col{display:flex;flex-direction:column;align-items:center}
.step-num{
  width:38px;height:38px;border-radius:50%;
  border:1px solid var(--border2);background:var(--bg2);
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;color:var(--primary);flex-shrink:0;z-index:1;
}
.step-line{flex:1;width:1px;background:var(--border);margin:4px 0}
.step:last-child .step-line{display:none}
.step-body{padding-bottom:1.75rem}
.step-title{font-size:14px;font-weight:700;color:var(--text);margin-bottom:6px;padding-top:8px}
.step-note{font-size:12px;color:var(--muted);line-height:1.55;margin-bottom:8px}
.code{
  font-family:'DM Mono',monospace;font-size:11.5px;color:#a5b4fc;
  background:var(--bg3);border:1px solid var(--border);border-radius:7px;
  padding:12px 14px;line-height:1.8;overflow-x:auto;
  position:relative;
}
.code .c-cmd{color:var(--success)}
.code .c-cm{color:var(--dim)}
.code .c-val{color:var(--accent)}
.code .c-str{color:#f9a8d4}
.copy-btn{
  position:absolute;top:8px;right:8px;
  font-family:'Syne',sans-serif;font-size:9px;letter-spacing:.1em;text-transform:uppercase;
  padding:3px 9px;border-radius:4px;border:1px solid var(--border);
  background:var(--bg4);color:var(--muted);cursor:pointer;transition:all .15s;
}
.copy-btn:hover{color:var(--text);border-color:var(--border2)}
.copy-btn.copied{color:var(--success);border-color:rgba(110,231,183,.3)}

/* ── SECURITY ── */
.sec-table{width:100%;border-collapse:collapse}
.sec-table th{
  font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);font-weight:500;padding:0 1rem .75rem;
  border-bottom:1px solid var(--border);text-align:left;
}
.sec-table td{
  font-size:12.5px;padding:.8rem 1rem;
  border-bottom:1px solid var(--border);vertical-align:top;
}
.sec-table tr:last-child td{border-bottom:none}
.sec-table tr:hover td{background:rgba(196,192,255,.025)}
.sec-concern{font-weight:600;color:var(--text)}
.sec-how{color:var(--muted);line-height:1.5}
code{
  font-family:'DM Mono',monospace;font-size:11px;
  color:var(--primary);background:rgba(196,192,255,.08);
  padding:1px 5px;border-radius:3px;
}

/* ── STACK ── */
.stack-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.stack-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:9px;
  padding:1rem;display:flex;align-items:center;gap:12px;
  transition:border-color .2s;
}
.stack-card:hover{border-color:var(--border2)}
.stack-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.stack-name{font-size:12px;font-weight:600;color:var(--text)}
.stack-role{font-size:10px;color:var(--muted);margin-top:2px}

/* ── DEPLOY ── */
.deploy-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
.deploy-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem;
}
.deploy-icon{font-size:1.75rem;margin-bottom:.75rem}
.deploy-title{font-size:14px;font-weight:700;margin-bottom:.4rem}
.deploy-desc{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:1rem}

/* ── TROUBLESHOOT ── */
.trouble-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.trouble{
  background:var(--bg2);border:1px solid var(--border);border-radius:9px;padding:1rem;
}
.trouble-prob{
  font-family:'DM Mono',monospace;font-size:11px;font-weight:500;
  color:var(--red);margin-bottom:5px;
}
.trouble-sol{font-size:11.5px;color:var(--muted);line-height:1.5}
.trouble-sol code{font-size:10.5px}

/* ── ROADMAP ── */
.roadmap{display:flex;flex-direction:column;gap:9px}
.roadmap-item{
  display:flex;align-items:center;gap:14px;
  background:var(--bg2);border:1px solid var(--border);border-radius:9px;
  padding:.85rem 1.1rem;font-size:13px;color:var(--muted);
  transition:border-color .2s;
}
.roadmap-item:hover{border-color:var(--border2);color:var(--text)}
.roadmap-box{
  width:18px;height:18px;border-radius:4px;
  border:1px solid var(--border2);flex-shrink:0;
}

/* ── FOOTER ── */
footer{
  padding:2.5rem 4rem;
  display:flex;align-items:center;justify-content:space-between;
  border-top:1px solid var(--border);
  flex-wrap:wrap;gap:1rem;
}
.footer-brand{font-size:1.6rem;font-weight:800;letter-spacing:-.04em;color:var(--primary)}
.footer-meta{font-size:11px;color:var(--dim);letter-spacing:.06em}
.mit{
  font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:500;
  padding:5px 13px;border-radius:4px;
  border:1px solid rgba(110,231,183,.28);background:rgba(110,231,183,.06);color:var(--success);
}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .hero{padding:3rem 1.5rem 2.5rem}
  section{padding:2.5rem 1.5rem}
  .features-grid{grid-template-columns:1fr 1fr}
  .stats{grid-template-columns:repeat(3,1fr)}
  .arch-wrap{grid-template-columns:1fr}
  .deploy-grid{grid-template-columns:1fr}
  .trouble-grid{grid-template-columns:1fr}
  footer{padding:2rem 1.5rem}
}
@media(max-width:560px){
  h1{font-size:2.8rem}
  .features-grid{grid-template-columns:1fr}
  .stats{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>

<!-- HERO -->
<div class="hero">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-inner">
    <div class="pill"><span class="pill-dot"></span>AI-Powered · Privacy-First · Production-Grade</div>
    <h1>Stitch</h1>
    <div class="tagline">AI Data Intelligence Suite &nbsp;·&nbsp; v1.0.0</div>
    <p class="hero-desc">
      A production-grade SaaS platform for AI-powered data cleaning, exploratory analysis,
      and machine learning — built on Streamlit with Gemini 2.5 Flash at its core.
    </p>
    <div class="badge-row">
      <span class="badge b-blue">Streamlit ≥1.32</span>
      <span class="badge b-purple">Gemini 2.5 Flash</span>
      <span class="badge b-orange">Pandas · NumPy</span>
      <span class="badge b-green">Scikit-learn · XGBoost</span>
      <span class="badge b-pink">ReportLab · Plotly</span>
      <span class="badge b-blue">MIT License</span>
    </div>
    <div class="btn-row">
      <a href="#setup" class="btn btn-primary">⚡ Quick Start</a>
      <a href="#features" class="btn btn-ghost">Explore Features →</a>
      <a href="#deploy" class="btn btn-ghost">Deploy Free →</a>
    </div>
  </div>
</div>

<!-- STATS -->
<div class="stats">
  <div class="stat"><div class="stat-n">9<sup>+</sup></div><div class="stat-l">Core Features</div></div>
  <div class="stat"><div class="stat-n">200<sup>MB</sup></div><div class="stat-l">Max Upload Size</div></div>
  <div class="stat"><div class="stat-n">4</div><div class="stat-l">File Formats</div></div>
  <div class="stat"><div class="stat-n">5<sup>rows</sup></div><div class="stat-l">LLM Data Exposure</div></div>
  <div class="stat"><div class="stat-n">0<sup>logs</sup></div><div class="stat-l">Raw Data Stored</div></div>
</div>

<!-- STICKY NAV -->
<nav class="sticky-nav">
  <a href="#features" class="nav-link">Features</a>
  <a href="#architecture" class="nav-link">Architecture</a>
  <a href="#stack" class="nav-link">Stack</a>
  <a href="#setup" class="nav-link">Setup</a>
  <a href="#security" class="nav-link">Security</a>
  <a href="#deploy" class="nav-link">Deploy</a>
  <a href="#troubleshoot" class="nav-link">Troubleshoot</a>
  <a href="#roadmap" class="nav-link">Roadmap</a>
</nav>

<!-- FEATURES -->
<section id="features">
  <div class="section-label">01 &nbsp; Features</div>
  <h2>Everything you need to understand your data</h2>
  <p class="sub">Nine purpose-built modules — from ingestion to PDF export — all wired together in a single Streamlit app.</p>
  <div class="features-grid">

    <div class="fcard">
      <div class="ficon fi-b">📂</div>
      <div class="fname">Dataset Upload</div>
      <div class="fdesc">Drag-and-drop ingestion for CSV, Excel (.xlsx/.xls), and JSON up to 200MB. Auto-detects encoding (utf-8, latin-1, cp1252). Instant 50-row preview, column schema, and quality KPIs on load.</div>
      <div class="ftags"><span class="ftag">CSV</span><span class="ftag">XLSX / XLS</span><span class="ftag">JSON</span><span class="ftag">200 MB limit</span><span class="ftag">SHA-256 fingerprint</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-g">🧹</div>
      <div class="fname">Auto Cleaning Engine</div>
      <div class="fdesc">Pure Pandas pipeline: drops columns with >60% nulls, fills missing values by dtype (median for numeric, mode for categorical, forward-fill for datetime), removes duplicate rows, infers & converts dtypes, detects IQR outliers (1.5× fence), normalises text (strip/lowercase), and emits a full audit log.</div>
      <div class="ftags"><span class="ftag">IQR outliers</span><span class="ftag">min-max norm</span><span class="ftag">z-score norm</span><span class="ftag">audit log</span><span class="ftag">dtype inference</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-p">📊</div>
      <div class="fname">EDA Dashboard</div>
      <div class="fdesc">Interactive Plotly charts rendered with a custom dark palette: histograms, box plots, correlation heatmap, scatter matrix, pie/bar breakdowns. Colour tokens match the app's design system for a cohesive feel.</div>
      <div class="ftags"><span class="ftag">Plotly</span><span class="ftag">Heatmap</span><span class="ftag">Correlation matrix</span><span class="ftag">Scatter</span><span class="ftag">Box plots</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-o">💡</div>
      <div class="fname">AI Insights</div>
      <div class="fdesc">Gemini 2.5 Flash generates business-relevant insights from schema + aggregated stats + ≤5 masked sample rows. Three tabs: Dataset Analysis, Preprocessing Guide, and PII Audit. Results cached in session to avoid repeat API calls.</div>
      <div class="ftags"><span class="ftag">Gemini 2.5 Flash</span><span class="ftag">Schema-only</span><span class="ftag">Session cache</span><span class="ftag">Privacy-safe</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-k">💬</div>
      <div class="fname">Chat with Dataset</div>
      <div class="fdesc">Natural language queries are translated to Pandas operations with AI-generated narration. Ask "what's average revenue by region?" and get executable code + plain-English explanation — no SQL needed.</div>
      <div class="ftags"><span class="ftag">NL → Pandas</span><span class="ftag">AI narration</span><span class="ftag">Conversational</span><span class="ftag">Stateful history</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-y">🤖</div>
      <div class="fname">AutoML Workspace</div>
      <div class="fdesc">Auto-infers task type (classification vs regression). Trains Random Forest, Logistic/Linear Regression, Ridge, and XGBoost (optional) with 3-fold cross-validation, confusion matrix, feature importance chart, and optional Gemini result interpretation.</div>
      <div class="ftags"><span class="ftag">XGBoost</span><span class="ftag">3-fold CV</span><span class="ftag">Feature importance</span><span class="ftag">Auto task detection</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-p">🔒</div>
      <div class="fname">PII Detection</div>
      <div class="fdesc">Regex scanner covers emails, Indian phone numbers (+91), US phone numbers, SSN, Aadhaar (12-digit), PAN (AAAAA9999A format), credit cards (13–16 digit), API keys/tokens, and IPv4 addresses. Samples 100 rows per column for speed.</div>
      <div class="ftags"><span class="ftag">Aadhaar</span><span class="ftag">PAN</span><span class="ftag">SSN</span><span class="ftag">Credit card</span><span class="ftag">API keys</span><span class="ftag">IPv4</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-b">📄</div>
      <div class="fname">PDF Reports & Export</div>
      <div class="fdesc">Downloadable cleaning and analytics reports generated via ReportLab. Export the cleaned dataset as CSV or Excel with one click. Reports written to <code>reports/</code>, cleaned data to <code>outputs/</code>.</div>
      <div class="ftags"><span class="ftag">ReportLab</span><span class="ftag">CSV export</span><span class="ftag">XLSX export</span><span class="ftag">Cleaning report</span></div>
    </div>

    <div class="fcard">
      <div class="ficon fi-g">🛡️</div>
      <div class="fname">Session Isolation</div>
      <div class="fdesc">Every browser session gets a unique UUID via Python's <code>uuid4()</code>. No shared memory between users. Temporary files use <code>tempfile</code> and are deleted immediately after processing. Generic user-facing errors; stack traces stay server-side.</div>
      <div class="ftags"><span class="ftag">UUID per session</span><span class="ftag">No shared state</span><span class="ftag">Temp file cleanup</span></div>
    </div>

  </div>
</section>

<!-- ARCHITECTURE -->
<section id="architecture">
  <div class="section-label">02 &nbsp; Architecture</div>
  <h2>Clean, modular, privacy-first</h2>
  <p class="sub">A single Streamlit entrypoint routes to isolated page modules. All ML stays in Python; LLMs only touch sanitised metadata.</p>
  <div class="arch-wrap">
    <div>
      <div class="mono-tree">
<span class="t-dir">ai_data_saas/</span>
├── <span class="t-file">app.py</span>               <span class="t-cm">← entrypoint &amp; routing</span>
├── <span class="t-file">requirements.txt</span>
├── <span class="t-file">.env.example</span>
│
├── <span class="t-dir">src/</span>
│   ├── <span class="t-hl">config.py</span>          <span class="t-cm">← constants &amp; colour tokens</span>
│   ├── <span class="t-hl">security.py</span>        <span class="t-cm">← PII, session, API key loading</span>
│   ├── <span class="t-hl">utils.py</span>           <span class="t-cm">← helpers, CSS inject, KPIs</span>
│   ├── <span class="t-file">upload.py</span>          <span class="t-cm">← file ingestion</span>
│   ├── <span class="t-file">cleaner.py</span>         <span class="t-cm">← data cleaning engine</span>
│   ├── <span class="t-file">eda.py</span>             <span class="t-cm">← EDA charts (Plotly)</span>
│   ├── <span class="t-file">llm_engine.py</span>      <span class="t-cm">← Gemini API integration</span>
│   ├── <span class="t-file">insights.py</span>        <span class="t-cm">← AI insights page</span>
│   ├── <span class="t-file">chatbot.py</span>         <span class="t-cm">← conversational assistant</span>
│   ├── <span class="t-file">automl.py</span>          <span class="t-cm">← AutoML workspace</span>
│   └── <span class="t-file">report_generator.py</span> <span class="t-cm">← PDF via ReportLab</span>
│
├── <span class="t-dir">data/</span>               <span class="t-cm">← sample datasets (optional)</span>
├── <span class="t-dir">outputs/</span>            <span class="t-cm">← cleaned dataset exports</span>
└── <span class="t-dir">reports/</span>            <span class="t-cm">← generated PDF reports</span>
      </div>
    </div>
    <div>
      <div class="principle">
        LLMs are used <em>only</em> for reasoning and language generation. All data processing — cleaning, statistics, ML training — is done with Pandas, NumPy, and Scikit-learn. The LLM never sees raw data, only schema, aggregated statistics, and ≤5 masked sample rows.
      </div>
      <div class="module-list">
        <div class="module"><span class="module-name">app.py</span><span class="module-desc">Streamlit page config, sidebar navigation, session init, CSS injection</span></div>
        <div class="module"><span class="module-name">security.py</span><span class="module-desc">PII regex patterns, masking, <code>safe_llm_context()</code>, UUID session isolation</span></div>
        <div class="module"><span class="module-name">cleaner.py</span><span class="module-desc">Null drops, dupe removal, dtype inference, IQR outliers, normalisation, audit log</span></div>
        <div class="module"><span class="module-name">llm_engine.py</span><span class="module-desc">Gemini 2.5 Flash client, status badge, insight/rec/chat/AutoML prompts</span></div>
        <div class="module"><span class="module-name">automl.py</span><span class="module-desc">Task inference, model pipeline, 3-fold CV, feature importance, LLM interpretation</span></div>
        <div class="module"><span class="module-name">report_generator.py</span><span class="module-desc">ReportLab PDF builder for cleaning &amp; analytics reports</span></div>
      </div>
    </div>
  </div>
</section>

<!-- STACK -->
<section id="stack">
  <div class="section-label">03 &nbsp; Tech Stack</div>
  <h2>Built on proven Python data tooling</h2>
  <p class="sub">Every dependency chosen for production reliability and permissive licensing.</p>
  <div class="stack-grid">
    <div class="stack-card"><div class="stack-dot" style="background:#ff4b4b"></div><div><div class="stack-name">Streamlit ≥1.32</div><div class="stack-role">UI framework &amp; routing</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#4285f4"></div><div><div class="stack-name">Gemini 2.5 Flash</div><div class="stack-role">LLM · insights · chat</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#150458"></div><div><div class="stack-name">Pandas ≥2.0</div><div class="stack-role">Data processing</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#4dabcf"></div><div><div class="stack-name">NumPy ≥1.26</div><div class="stack-role">Numeric operations</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#636efa"></div><div><div class="stack-name">Plotly ≥5.20</div><div class="stack-role">Interactive charts</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#f89939"></div><div><div class="stack-name">Scikit-learn ≥1.4</div><div class="stack-role">ML models &amp; CV</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#189b62"></div><div><div class="stack-name">XGBoost ≥2.0</div><div class="stack-role">Gradient boosting (opt.)</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#e25822"></div><div><div class="stack-name">ReportLab ≥4.1</div><div class="stack-role">PDF generation</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#217346"></div><div><div class="stack-name">openpyxl ≥3.1</div><div class="stack-role">Excel read / write</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#5c5ce6"></div><div><div class="stack-name">faiss-cpu ≥1.7</div><div class="stack-role">Vector search (future)</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#ecc94b"></div><div><div class="stack-name">python-dotenv ≥1.0</div><div class="stack-role">API key loading</div></div></div>
    <div class="stack-card"><div class="stack-dot" style="background:#6ee7b7"></div><div><div class="stack-name">google-generativeai</div><div class="stack-role">Gemini SDK</div></div></div>
  </div>
</section>

<!-- SETUP -->
<section id="setup">
  <div class="section-label">04 &nbsp; Local Setup</div>
  <h2>Running in five steps</h2>
  <p class="sub">Python 3.10+ recommended. The app runs without a Gemini key — AI features degrade gracefully to static stats.</p>
  <div class="steps">

    <div class="step">
      <div class="step-col"><div class="step-num">1</div><div class="step-line"></div></div>
      <div class="step-body">
        <div class="step-title">Clone the repository</div>
        <div class="code" id="c1">
<span class="c-cmd">git clone</span> https://github.com/yourusername/stitch-ai-data-suite.git
<span class="c-cmd">cd</span> stitch-ai-data-suite
          <button class="copy-btn" onclick="cp('c1',this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-col"><div class="step-num">2</div><div class="step-line"></div></div>
      <div class="step-body">
        <div class="step-title">Create &amp; activate virtual environment</div>
        <div class="code" id="c2">
<span class="c-cmd">python -m venv</span> .venv
<span class="c-cmd">source</span> .venv/bin/activate   <span class="c-cm"># Windows: .venv\Scripts\activate</span>
          <button class="copy-btn" onclick="cp('c2',this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-col"><div class="step-num">3</div><div class="step-line"></div></div>
      <div class="step-body">
        <div class="step-title">Install dependencies</div>
        <div class="code" id="c3">
<span class="c-cmd">pip install</span> -r requirements.txt
<span class="c-cm"># XGBoost is optional but recommended:</span>
<span class="c-cmd">pip install</span> xgboost
          <button class="copy-btn" onclick="cp('c3',this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-col"><div class="step-num">4</div><div class="step-line"></div></div>
      <div class="step-body">
        <div class="step-title">Configure Gemini API key <em style="font-size:10px;color:var(--dim);font-style:normal;font-weight:400">(optional — AI features only)</em></div>
        <div class="step-note">Get a free key at <strong style="color:var(--primary)">aistudio.google.com/app/apikey</strong>. Without it the app falls back to static statistical insights.</div>
        <div class="code" id="c4">
<span class="c-cmd">cp</span> .env.example .env
<span class="c-cm"># Open .env and set:</span>
GEMINI_API_KEY=<span class="c-val">AIzaSy...your-key-here</span>
          <button class="copy-btn" onclick="cp('c4',this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-col"><div class="step-num">5</div><div class="step-line"></div></div>
      <div class="step-body">
        <div class="step-title">Run the app</div>
        <div class="code" id="c5">
<span class="c-cmd">streamlit run</span> app.py
<span class="c-cm"># Opens at http://localhost:8501</span>
          <button class="copy-btn" onclick="cp('c5',this)">Copy</button>
        </div>
      </div>
    </div>

  </div>
</section>

<!-- SECURITY -->
<section id="security">
  <div class="section-label">05 &nbsp; Security &amp; Privacy</div>
  <h2>Privacy-first by design</h2>
  <p class="sub">Raw data never leaves your session. The LLM only ever receives schema, aggregated statistics, and masked samples.</p>
  <table class="sec-table">
    <thead><tr><th style="width:28%">Concern</th><th>How Stitch handles it</th></tr></thead>
    <tbody>
      <tr><td class="sec-concern">Session isolation</td><td class="sec-how">Each browser session receives a unique <code>uuid4()</code>; no data is shared between concurrent users in session state</td></tr>
      <tr><td class="sec-concern">API key safety</td><td class="sec-how">Loaded via <code>.env</code> locally or Streamlit Secrets in production — never hardcoded or logged</td></tr>
      <tr><td class="sec-concern">LLM data exposure</td><td class="sec-how"><code>safe_llm_context()</code> sends only schema + aggregated stats + ≤5 masked rows. Raw values never reach Gemini</td></tr>
      <tr><td class="sec-concern">PII detection</td><td class="sec-how">9 regex patterns: email, phone (IN/US), SSN, Aadhaar, PAN, credit card, API keys/tokens, IPv4. Samples 100 rows/column</td></tr>
      <tr><td class="sec-concern">PII masking</td><td class="sec-how"><code>mask_pii_value()</code> masks by type — email keeps domain, CC shows last 4, Aadhaar/SSN shows last 4, PAN keeps first 2 &amp; last 1</td></tr>
      <tr><td class="sec-concern">Temporary files</td><td class="sec-how"><code>tempfile.NamedTemporaryFile</code> handles all uploads; <code>delete_temp_file()</code> is called immediately after parsing</td></tr>
      <tr><td class="sec-concern">Error messages</td><td class="sec-how">Generic user-facing errors only — full stack traces are captured by Python logging and stay server-side</td></tr>
      <tr><td class="sec-concern">File integrity</td><td class="sec-how">SHA-256 fingerprint computed on raw upload bytes for deduplication and integrity verification</td></tr>
    </tbody>
  </table>
</section>

<!-- DEPLOY -->
<section id="deploy">
  <div class="section-label">06 &nbsp; Deployment</div>
  <h2>Free cloud deployment in minutes</h2>
  <p class="sub">Streamlit Community Cloud hosts your app for free from a public GitHub repo.</p>
  <div class="deploy-grid">
    <div class="deploy-card">
      <div class="deploy-icon">☁️</div>
      <div class="deploy-title">Streamlit Community Cloud</div>
      <div class="deploy-desc">Push to GitHub, connect at <strong style="color:var(--primary)">share.streamlit.io</strong>, set Main file to <code>app.py</code>, and deploy. Add your Gemini key under Settings → Secrets.</div>
      <div class="code" id="c6" style="font-size:11px">
<span class="c-cm"># In Streamlit Cloud Secrets (TOML format):</span>
GEMINI_API_KEY = <span class="c-str">"AIzaSy...your-key-here"</span>
        <button class="copy-btn" onclick="cp('c6',this)">Copy</button>
      </div>
    </div>
    <div class="deploy-card">
      <div class="deploy-icon">🐳</div>
      <div class="deploy-title">Docker / Self-hosted</div>
      <div class="deploy-desc">No Docker file is bundled, but the app is stateless and runs on any Python 3.10+ environment. Pass <code>GEMINI_API_KEY</code> as an environment variable and expose port 8501.</div>
      <div class="code" id="c7" style="font-size:11px">
<span class="c-cmd">docker run</span> -p 8501:8501 \
  -e GEMINI_API_KEY=<span class="c-val">your_key</span> \
  your-stitch-image
        <button class="copy-btn" onclick="cp('c7',this)">Copy</button>
      </div>
    </div>
  </div>
</section>

<!-- TROUBLESHOOT -->
<section id="troubleshoot">
  <div class="section-label">07 &nbsp; Troubleshooting</div>
  <h2>Common issues &amp; fixes</h2>
  <p class="sub">Most problems resolve with a dependency check or API key verification.</p>
  <div class="trouble-grid">
    <div class="trouble"><div class="trouble-prob">ModuleNotFoundError</div><div class="trouble-sol">Run <code>pip install -r requirements.txt</code> inside your activated venv.</div></div>
    <div class="trouble"><div class="trouble-prob">AI features offline</div><div class="trouble-sol">Check <code>GEMINI_API_KEY</code> in <code>.env</code> or Streamlit Secrets. The app works without it — only Insights, Chat narration, and AutoML interpretation require Gemini.</div></div>
    <div class="trouble"><div class="trouble-prob">Excel not parsing</div><div class="trouble-sol">Ensure <code>openpyxl</code> is installed: <code>pip install openpyxl</code>.</div></div>
    <div class="trouble"><div class="trouble-prob">PDF not generating</div><div class="trouble-sol">Ensure <code>reportlab</code> is installed: <code>pip install reportlab</code>.</div></div>
    <div class="trouble"><div class="trouble-prob">XGBoost not available</div><div class="trouble-sol"><code>pip install xgboost</code> — optional. Falls back to Random Forest + Logistic/Linear Regression automatically.</div></div>
    <div class="trouble"><div class="trouble-prob">Large file slow</div><div class="trouble-sol">Reduce dataset rows or increase the Streamlit upload limit via <code>server.maxUploadSize</code> in <code>.streamlit/config.toml</code>.</div></div>
    <div class="trouble"><div class="trouble-prob">Encoding errors on CSV</div><div class="trouble-sol">The parser tries utf-8, latin-1, and cp1252 automatically. If all fail, re-save the file as UTF-8 in Excel or a text editor.</div></div>
    <div class="trouble"><div class="trouble-prob">Streamlit version conflict</div><div class="trouble-sol">Upgrade with <code>pip install streamlit --upgrade</code>. Minimum required version is 1.32.0.</div></div>
  </div>
</section>

<!-- ROADMAP -->
<section id="roadmap">
  <div class="section-label">08 &nbsp; Roadmap</div>
  <h2>What's coming next</h2>
  <p class="sub">Planned features for future releases — contributions welcome.</p>
  <div class="roadmap">
    <div class="roadmap-item"><div class="roadmap-box"></div>Multi-file join / merge support</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>Time-series decomposition (trend, seasonality, forecasting)</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>FAISS vector search for semantic data exploration</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>SQLite-backed dataset versioning</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>Scheduled report emails</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>Role-based access control for team plans</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>Plugin system for custom cleaning rules</div>
    <div class="roadmap-item"><div class="roadmap-box"></div>Google Sheets / BigQuery direct connector</div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div>
    <div class="footer-brand">Stitch</div>
    <div class="footer-meta" style="margin-top:4px">Built with ♥ using Streamlit, Gemini AI, and the Python data stack</div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
    <span class="footer-meta">v1.0.0</span>
    <span class="mit">MIT License</span>
  </div>
</footer>

<script>
function cp(id,btn){
  const el=document.getElementById(id);
  const text=el.innerText.replace(/Copy$/,'').trim();
  navigator.clipboard.writeText(text).then(()=>{
    btn.textContent='Copied!';
    btn.classList.add('copied');
    setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('copied')},2000);
  });
}

// Active nav highlight on scroll
const sections=document.querySelectorAll('section[id]');
const links=document.querySelectorAll('.nav-link');
const obs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      links.forEach(l=>l.classList.remove('active'));
      const active=document.querySelector('.nav-link[href="#'+e.target.id+'"]');
      if(active)active.classList.add('active');
    }
  });
},{rootMargin:'-40% 0px -55% 0px'});
sections.forEach(s=>obs.observe(s));
</script>
</body>
</html>
