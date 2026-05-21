"""
report_generator.py — PDF report generation.

Uses ReportLab to produce a formatted PDF containing:
  • Executive summary (rows, cols, quality score)
  • Cleaning audit log
  • Descriptive statistics table
  • Outlier summary
  • AI insights (if available)
  • Data download links (CSV / Excel)

No raw user data is embedded — only aggregated statistics.
"""

import io
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

from src.config import COLORS
from src.utils import (
    data_quality_score, quality_label, fmt_number,
    memory_usage, human_bytes, section_header,
    df_to_csv_bytes, df_to_excel_bytes,
    get_numeric_cols,
)

logger = logging.getLogger(__name__)

_REPORTLAB_AVAILABLE = True
try:
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    _REPORTLAB_AVAILABLE = False


# ── PDF builder ────────────────────────────────────────────────────────────────

def _hex_to_rl(hex_color: str):
    """Convert a hex colour string to a ReportLab Color."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return rl_colors.Color(r, g, b)


def generate_pdf_report(
    df_raw: pd.DataFrame,
    df_cleaned: Optional[pd.DataFrame],
    file_name: str,
    cleaning_log: list[str],
    ai_insights: Optional[str] = None,
) -> bytes:
    """
    Build and return a PDF report as bytes.
    Only aggregated statistics are included — no raw rows.
    """
    if not _REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    PRIMARY = _hex_to_rl(COLORS["primary"])
    SURFACE = _hex_to_rl("#1f1f28")
    ON_SURFACE = _hex_to_rl(COLORS["on_surface"])
    OUTLINE = _hex_to_rl(COLORS["outline"])

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=24, textColor=PRIMARY, spaceAfter=6,
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=14, textColor=PRIMARY, spaceBefore=14, spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=11, textColor=ON_SURFACE, spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, textColor=ON_SURFACE, leading=14,
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=8, textColor=OUTLINE, leading=12,
    )

    def hr():
        return HRFlowable(width="100%", thickness=0.5, color=OUTLINE, spaceAfter=8)

    def sp(n=8):
        return Spacer(1, n)

    elements = []

    # ── Cover ──
    elements.append(Paragraph("STITCH", title_style))
    elements.append(Paragraph("AI Data Intelligence Report", h2_style))
    elements.append(sp(4))
    elements.append(Paragraph(f"Dataset: {file_name}", label_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", label_style))
    elements.append(sp(16))
    elements.append(hr())

    # ── Executive summary ──
    elements.append(Paragraph("Executive Summary", h1_style))
    df_active = df_cleaned if df_cleaned is not None else df_raw
    score = data_quality_score(df_active)
    lbl, _ = quality_label(score)
    null_pct = df_active.isnull().mean().mean() * 100
    dupe_pct = df_active.duplicated().mean() * 100

    summary_data = [
        ["Metric", "Raw Dataset", "After Cleaning" if df_cleaned is not None else "N/A"],
        ["Rows", fmt_number(len(df_raw)), fmt_number(len(df_active))],
        ["Columns", str(df_raw.shape[1]), str(df_active.shape[1])],
        ["Quality Score", "—", f"{score} / 100 ({lbl})"],
        ["Missing Values", f"{df_raw.isnull().mean().mean() * 100:.1f}%", f"{null_pct:.1f}%"],
        ["Duplicate Rows", f"{df_raw.duplicated().mean() * 100:.1f}%", f"{dupe_pct:.1f}%"],
        ["Memory", human_bytes(memory_usage(df_raw)), human_bytes(memory_usage(df_active))],
    ]
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE, _hex_to_rl("#2a2933")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), ON_SURFACE),
        ("GRID", (0, 0), (-1, -1), 0.25, OUTLINE),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(summary_table)
    elements.append(sp(16))

    # ── Cleaning log ──
    if cleaning_log:
        elements.append(hr())
        elements.append(Paragraph("Cleaning Audit Log", h1_style))
        for entry in cleaning_log:
            clean_entry = entry.replace("🗑️", "").replace("♻️", "").replace("🔧", "").replace(
                "🔄", "").replace("✏️", "").replace("📌", "").replace("📐", "").replace("✅", "").strip()
            elements.append(Paragraph(f"• {clean_entry}", body_style))
        elements.append(sp(12))

    # ── Descriptive statistics ──
    num_cols = get_numeric_cols(df_active)
    if num_cols:
        elements.append(hr())
        elements.append(Paragraph("Descriptive Statistics (Numeric Columns)", h1_style))
        desc = df_active[num_cols].describe().round(3)
        stat_rows = [["Column"] + list(desc.index)]
        for col in num_cols[:15]:  # cap to avoid overflow
            stat_rows.append([col] + [str(v) for v in desc[col].values])
        stat_table = Table(stat_rows, repeatRows=1)
        col_w = 6.5 / (len(stat_rows[0])) * inch
        stat_table._argW = [col_w] * len(stat_rows[0])
        stat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE, _hex_to_rl("#2a2933")]),
            ("TEXTCOLOR", (0, 1), (-1, -1), ON_SURFACE),
            ("GRID", (0, 0), (-1, -1), 0.25, OUTLINE),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(stat_table)
        elements.append(sp(12))

    # ── AI insights (text only, no markdown parsing) ──
    if ai_insights and not ai_insights.startswith("__"):
        elements.append(PageBreak())
        elements.append(Paragraph("AI-Generated Insights", h1_style))
        # Strip markdown-ish formatting for PDF
        clean_insight = (
            ai_insights
            .replace("**", "")
            .replace("###", "")
            .replace("##", "")
            .replace("#", "")
            .replace("`", "'")
        )
        for line in clean_insight.split("\n"):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, body_style))
                elements.append(sp(4))

    # ── Footer ──
    elements.append(sp(20))
    elements.append(hr())
    elements.append(Paragraph(
        f"Generated by Stitch AI Data Suite v1.0 | {datetime.now().year}",
        label_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# ── Page UI ───────────────────────────────────────────────────────────────────

def render_reports_page() -> None:
    section_header(
        "REPORTS",
        "Export & Download",
        "Generate PDF reports or download your cleaned dataset in multiple formats.",
    )

    df_raw = st.session_state.get("df_raw")
    df_cleaned = st.session_state.get("df_cleaned")
    file_name = st.session_state.get("file_name", "dataset")

    if df_raw is None:
        st.info("⬆️ Upload a dataset first.")
        return

    df_active = df_cleaned if df_cleaned is not None else df_raw

    # ── Data Downloads ──
    st.markdown("### 📥 Download Cleaned Dataset")
    c1, c2 = st.columns(2)

    with c1:
        csv_bytes = df_to_csv_bytes(df_active)
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_bytes,
            file_name=f"stitch_cleaned_{file_name.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c2:
        excel_bytes = df_to_excel_bytes(df_active)
        st.download_button(
            label="⬇️ Download as Excel",
            data=excel_bytes,
            file_name=f"stitch_cleaned_{file_name.rsplit('.', 1)[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown("---")

    # ── PDF Report ──
    st.markdown("### 📄 PDF Report")

    ai_insights = st.session_state.get("insights_cache", {}).get("dataset_insights")
    cleaning_log = st.session_state.get("cleaning_log", [])

    if st.button("🖨️ Generate PDF Report", use_container_width=True):
        if not _REPORTLAB_AVAILABLE:
            st.error("ReportLab not installed. Run: `pip install reportlab`")
        else:
            with st.spinner("Building PDF report…"):
                try:
                    pdf_bytes = generate_pdf_report(
                        df_raw=df_raw,
                        df_cleaned=df_cleaned,
                        file_name=file_name,
                        cleaning_log=cleaning_log,
                        ai_insights=ai_insights,
                    )
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"stitch_report_{file_name.rsplit('.', 1)[0]}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ PDF report ready for download!")
                except Exception as exc:
                    st.error(f"Report generation failed: {exc}")

    st.markdown("---")

    # ── Dataset summary table ──
    st.markdown("### 📊 Session Summary")
    col1, col2 = st.columns(2)
    with col1:
        score = data_quality_score(df_active)
        lbl, colour = quality_label(score)
        st.metric("Quality Score", f"{score} / 100")
        st.metric("Rows", fmt_number(len(df_active)))
        st.metric("Columns", str(df_active.shape[1]))
    with col2:
        st.metric("Missing Values", f"{df_active.isnull().mean().mean() * 100:.1f}%")
        st.metric("Duplicate Rows", f"{df_active.duplicated().mean() * 100:.1f}%")
        st.metric("Memory", human_bytes(memory_usage(df_active)))
