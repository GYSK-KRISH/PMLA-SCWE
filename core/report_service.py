"""Professional Report Generation Engine for PMLA-SCWE.

Version 1.5 — Professional Report Generation Engine
Features:
- 6 Report Types:
  1. Individual Student Intelligence Report
  2. Class Performance Report
  3. At-Risk Student Report
  4. Attendance Report
  5. Monthly Progress Report
  6. Teacher Intervention Report
- High-quality PDF export (ReportLab) with embedded charts, tables, and branding.
- Clean CSV data export.
- Section customization toggles.
- Optional AI-generated executive summaries (grounded with clear advisory labels).
- Standardized educational decision-support safety disclaimers.
"""

from __future__ import annotations
import os
import csv
import io
from datetime import datetime, date
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from core.student_profile_service import get_student_360_profile
from core.risk_engine import compute_student_risk_profile, get_class_risk_overview
from core.student_service import get_all_students, get_student_by_id
from core.analytics import get_student_analytics_summary
from core.database import execute_select


REPORT_TYPE_STUDENT_INTELLIGENCE = "STUDENT_INTELLIGENCE"
REPORT_TYPE_CLASS_PERFORMANCE = "CLASS_PERFORMANCE"
REPORT_TYPE_AT_RISK = "AT_RISK"
REPORT_TYPE_ATTENDANCE = "ATTENDANCE"
REPORT_TYPE_MONTHLY_PROGRESS = "MONTHLY_PROGRESS"
REPORT_TYPE_INTERVENTIONS = "INTERVENTIONS"

REPORT_TYPES = [
    (REPORT_TYPE_STUDENT_INTELLIGENCE, "Individual Student Intelligence Report"),
    (REPORT_TYPE_CLASS_PERFORMANCE, "Class Performance Report"),
    (REPORT_TYPE_AT_RISK, "At-Risk Student Report"),
    (REPORT_TYPE_ATTENDANCE, "Attendance & Compliance Report"),
    (REPORT_TYPE_MONTHLY_PROGRESS, "Monthly Progress & Trajectory Report"),
    (REPORT_TYPE_INTERVENTIONS, "Teacher Intervention Action Report"),
]

SAFETY_DISCLAIMER = (
    "NOTICE: This report contains data-driven analytical indicators and recommendations "
    "intended to support teacher decision-making. Predictive trends and Learning Health Scores "
    "are statistical indicators derived from historical observations and should not be interpreted as absolute guarantees."
)


def _get_report_styles():
    """Builds a cohesive, clean palette of typography styles for PDF documents."""
    styles = getSampleStyleSheet()

    # Primary brand colors
    primary_color = colors.HexColor("#1A1D2E")
    accent_color = colors.HexColor("#4A3AFF")
    secondary_text = colors.HexColor("#555E6D")
    body_text = colors.HexColor("#222530")

    styles.add(ParagraphStyle(
        "ReportHeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=TA_LEFT
    ))

    styles.add(ParagraphStyle(
        "ReportHeaderSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=secondary_text,
        alignment=TA_LEFT
    ))

    styles.add(ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        "BodySmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=body_text
    ))

    styles.add(ParagraphStyle(
        "BodySmallBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=body_text
    ))

    styles.add(ParagraphStyle(
        "DisclaimerStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#6B7280"),
        alignment=TA_JUSTIFY
    ))

    styles.add(ParagraphStyle(
        "AISummaryStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    ))

    return styles


# ---------------------------------------------------------------------------
# Chart Generation Utilities for PDF Embedding
# ---------------------------------------------------------------------------

def _generate_student_kpi_chart(profile: dict, tmp_dir: str = "reports/charts") -> str:
    """Generates clean mini bar/radar chart of student metrics for PDF embedding."""
    os.makedirs(tmp_dir, exist_ok=True)
    out_path = os.path.join(tmp_dir, f"student_{profile['student']['id']}_chart.png")

    acad = profile["academic"].get("average_score") or 0.0
    att = profile["attendance"].get("percentage") or 0.0
    lhs = profile["learning_health"].get("score") or 0.0
    well = profile["wellness"].get("wellness_score") or 0.0

    categories = ["Academic", "Attendance", "Learning Health", "Cyber-Wellness"]
    values = [acad, att, lhs, well]
    bar_colors = ["#4A3AFF", "#00B4D8", "#10B981", "#8B5CF6"]

    fig, ax = plt.subplots(figsize=(6, 2.2), dpi=200)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FAFAFC")

    bars = ax.barh(categories, values, color=bar_colors, height=0.55, edgecolor="none")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score / Metric (%)", fontsize=8, fontweight="bold", color="#4B5563")
    ax.grid(axis="x", linestyle="--", alpha=0.5, color="#E5E7EB")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D1D5DB")
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.tick_params(colors="#4B5563", labelsize=8)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%",
                va="center", ha="left", fontsize=8, fontweight="bold", color="#1F2937")

    plt.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return out_path


def _generate_class_donut_chart(overview: dict, tmp_dir: str = "reports/charts") -> str:
    """Generates clean risk distribution donut chart for class PDF reports."""
    os.makedirs(tmp_dir, exist_ok=True)
    out_path = os.path.join(tmp_dir, "class_risk_donut.png")

    high = overview.get("total_high", 0)
    med = overview.get("total_medium", 0)
    low = overview.get("total_low", 0)
    insuf = overview.get("total_insufficient", 0)

    labels = ["High Risk", "Medium Risk", "Low Risk", "Insufficient"]
    sizes = [high, med, low, insuf]
    slice_colors = ["#EF4444", "#F59E0B", "#10B981", "#9CA3AF"]

    # Filter zero slices
    filtered_data = [(l, s, c) for l, s, c in zip(labels, sizes, slice_colors) if s > 0]
    if not filtered_data:
        filtered_data = [("No Data", 1, "#E5E7EB")]

    f_labels = [d[0] for d in filtered_data]
    f_sizes = [d[1] for d in filtered_data]
    f_colors = [d[2] for d in filtered_data]

    fig, ax = plt.subplots(figsize=(4.5, 2.5), dpi=200)
    fig.patch.set_facecolor("#FFFFFF")

    wedges, texts, autotexts = ax.pie(
        f_sizes, labels=f_labels, colors=f_colors, autopct="%1.0f%%",
        startangle=140, pctdistance=0.75,
        textprops=dict(color="#1F2937", fontsize=8, fontweight="bold")
    )
    center_circle = plt.Circle((0, 0), 0.55, fc="#FFFFFF")
    fig.gca().add_artist(center_circle)

    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontsize(7.5)

    plt.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Individual Student Intelligence PDF Report
# ---------------------------------------------------------------------------

def generate_student_pdf_report(
    student_id: int,
    output_path: str | None = None,
    options: dict[str, Any] | None = None
) -> str:
    """Generates a professional multi-page or executive single-sheet PDF intelligence report for a student."""
    opts = options or {}
    profile = get_student_360_profile(student_id)
    if not profile:
        raise ValueError(f"Student ID #{student_id} not found in database.")

    if not output_path:
        os.makedirs("reports", exist_ok=True)
        s_name = profile["student"]["name"].replace(" ", "_")
        output_path = os.path.join("reports", f"Student_Report_{student_id}_{s_name}.pdf")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    styles = _get_report_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    elements = []
    s = profile["student"]
    lh = profile["learning_health"]
    acad = profile["academic"]
    att = profile["attendance"]
    well = profile["wellness"]
    pred = profile["prediction"]
    risk = profile.get("risk_engine", {})
    r_score = risk.get("risk_score")
    r_level = risk.get("risk_level", "LOW")

    # 1. Header Banner & Title
    gen_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")
    header_data = [
        [
            Paragraph("<b>PMLA-SCWE</b> | Student Intelligence Report", styles["ReportHeaderTitle"]),
            Paragraph(f"<b>Date:</b> {gen_time}<br/><b>Student ID:</b> #{s['id']}", styles["BodySmallBold"])
        ]
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_header)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4A3AFF"), spaceAfter=10))

    # 2. Student Identity & Executive Summary Box
    risk_color = colors.HexColor("#EF4444") if r_level == "HIGH" else (colors.HexColor("#F59E0B") if r_level == "MEDIUM" else colors.HexColor("#10B981"))
    id_data = [
        [
            Paragraph(f"<b>Student Name:</b> {s['name']}", styles["BodySmall"]),
            Paragraph(f"<b>Class & Section:</b> {s['class_section']}", styles["BodySmall"]),
            Paragraph(f"<b>Learning Health:</b> {lh.get('display', 'N/A')}", styles["BodySmallBold"]),
            Paragraph(f"<b>Risk Level:</b> <font color='{risk_color.hexval()}'><b>{r_level} ({r_score or 'N/A'}/100)</b></font>", styles["BodySmallBold"])
        ]
    ]
    t_id = Table(id_data, colWidths=[140, 120, 140, 140])
    t_id.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t_id)
    elements.append(Spacer(1, 10))

    # Optional AI Executive Summary
    if opts.get("include_ai_summary", True):
        ai_summary_text = None
        # Check if AI summary was pre-requested or generate rule-based synthesis
        from core import explainability
        factors = risk.get("factors", [])
        why_bullets = explainability.generate_why_narrative(
            {
                "academic_average": acad.get("average_score"),
                "attendance_percentage": att.get("percentage"),
                "trend_direction": pred.get("trend_direction"),
                "slope": pred.get("slope", 0.0),
                "daily_screen_time": well.get("daily_screen_time"),
                "learning_health_score": lh.get("score")
            },
            factors,
            r_level
        )
        ai_summary_text = " ".join(why_bullets)

        ai_box_data = [
            [
                Paragraph("<b>EXECUTIVE ADVISORY BRIEFING (AI-GROUNDED)</b>", styles["BodySmallBold"]),
            ],
            [
                Paragraph(ai_summary_text, styles["AISummaryStyle"])
            ]
        ]
        t_ai = Table(ai_box_data, colWidths=[540])
        t_ai.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#93C5FD")),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ]))
        elements.append(t_ai)
        elements.append(Spacer(1, 10))

    # 3. Core Metrics Grid Table (Academic, Attendance, Trajectory, Wellness)
    if opts.get("include_metrics", True):
        elements.append(Paragraph("<b>1. Multi-Dimensional Performance Summary</b>", styles["SectionHeading"]))
        metrics_table_data = [
            [
                Paragraph("<b>Metric Dimension</b>", styles["BodySmallBold"]),
                Paragraph("<b>Current Value</b>", styles["BodySmallBold"]),
                Paragraph("<b>Status / Benchmark</b>", styles["BodySmallBold"]),
                Paragraph("<b>Key Indicator / Trajectory</b>", styles["BodySmallBold"])
            ],
            [
                Paragraph("Academic Performance", styles["BodySmall"]),
                Paragraph(f"{acad.get('display', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"{acad.get('status', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"Weakest Area: {acad.get('weakest_subject', 'N/A')}", styles["BodySmall"])
            ],
            [
                Paragraph("Attendance & Punctuality", styles["BodySmall"]),
                Paragraph(f"{att.get('display', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"{att.get('status', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"{att.get('present_count', 0)} Days Present, {att.get('absent_count', 0)} Absent", styles["BodySmall"])
            ],
            [
                Paragraph("Performance Trajectory", styles["BodySmall"]),
                Paragraph(f"Slope: {pred.get('slope', 0.0):.2f} pts/wk", styles["BodySmall"]),
                Paragraph(f"{pred.get('trend_direction', 'Stable')}", styles["BodySmallBold"]),
                Paragraph(f"Forecast Next Score: {pred.get('display', 'N/A')}", styles["BodySmall"])
            ],
            [
                Paragraph("Cyber-Wellbeing & Habits", styles["BodySmall"]),
                Paragraph(f"{well.get('display', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"{well.get('status_label', 'N/A')}", styles["BodySmall"]),
                Paragraph(f"Daily Screen: {well.get('daily_screen_time', 'N/A')}h (Study: {well.get('study_screen_time', 'N/A')}h)", styles["BodySmall"])
            ]
        ]
        t_metrics = Table(metrics_table_data, colWidths=[140, 100, 130, 170])
        t_metrics.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        elements.append(t_metrics)
        elements.append(Spacer(1, 10))

    # 4. Embedded Visual Chart
    if opts.get("include_charts", True):
        try:
            chart_file = _generate_student_kpi_chart(profile)
            if os.path.exists(chart_file):
                elements.append(Paragraph("<b>2. Graphical Dimension Breakdown</b>", styles["SectionHeading"]))
                elements.append(Image(chart_file, width=5.5 * inch, height=2.0 * inch))
                elements.append(Spacer(1, 10))
        except Exception:
            pass

    # 5. Contributing Risk Factors & Evidence Table
    if opts.get("include_risk_factors", True):
        elements.append(Paragraph("<b>3. Explainable Risk Factors & Verified Evidence</b>", styles["SectionHeading"]))
        factors = risk.get("factors", [])
        if factors:
            factor_table_data = [
                [
                    Paragraph("<b>Risk Factor</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Impact</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Points Contributed</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Specific Evidence</b>", styles["BodySmallBold"])
                ]
            ]
            for f in factors:
                factor_table_data.append([
                    Paragraph(f["name"], styles["BodySmall"]),
                    Paragraph(f["impact"].upper(), styles["BodySmallBold"]),
                    Paragraph(f"+{f['points_contributed']:.0f} pts", styles["BodySmall"]),
                    Paragraph(f["evidence"], styles["BodySmall"])
                ])
            t_factors = Table(factor_table_data, colWidths=[130, 70, 100, 240])
            t_factors.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEE2E2")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FECACA")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(t_factors)
        else:
            elements.append(Paragraph("<i>No critical negative risk factors detected for this student profile.</i>", styles["BodySmall"]))
        elements.append(Spacer(1, 10))

    # 6. Recommended Teacher Interventions Checklist
    if opts.get("include_interventions", True):
        elements.append(Paragraph("<b>4. Recommended Teacher Intervention Checklist</b>", styles["SectionHeading"]))
        interventions = profile.get("interventions", [])
        if interventions:
            iv_data = [
                [
                    Paragraph("<b>[  ]</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Priority</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Intervention Action</b>", styles["BodySmallBold"]),
                    Paragraph("<b>Detailed Description & Strategy</b>", styles["BodySmallBold"])
                ]
            ]
            for iv in interventions:
                iv_data.append([
                    Paragraph("[  ]", styles["BodySmall"]),
                    Paragraph(f"<b>{iv.get('priority', 'MEDIUM')}</b>", styles["BodySmall"]),
                    Paragraph(f"<b>{iv.get('title', '')}</b>", styles["BodySmallBold"]),
                    Paragraph(iv.get("description", ""), styles["BodySmall"])
                ])
            t_iv = Table(iv_data, colWidths=[30, 60, 150, 300])
            t_iv.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]))
            elements.append(t_iv)
        else:
            elements.append(Paragraph("<i>Standard syllabus progression recommended. No active intervention required.</i>", styles["BodySmall"]))
        elements.append(Spacer(1, 10))

    # 7. Teacher Signoff Area & Safety Disclaimer
    elements.append(Spacer(1, 8))
    signoff_data = [
        [
            Paragraph("<b>Teacher / Evaluator Signature:</b> ___________________________", styles["BodySmall"]),
            Paragraph(f"<b>Review Date:</b> ___________________________", styles["BodySmall"])
        ]
    ]
    t_sign = Table(signoff_data, colWidths=[300, 240])
    elements.append(t_sign)
    elements.append(Spacer(1, 10))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=6))
    elements.append(Paragraph(SAFETY_DISCLAIMER, styles["DisclaimerStyle"]))

    # Build Document
    doc.build(elements)
    return output_path


# ---------------------------------------------------------------------------
# Class Performance PDF Report
# ---------------------------------------------------------------------------

def generate_class_pdf_report(
    class_name: str = "All",
    section: str = "All",
    output_path: str | None = None,
    options: dict[str, Any] | None = None
) -> str:
    """Generates an executive classroom performance and risk distribution PDF report."""
    opts = options or {}
    overview = get_class_risk_overview(class_name=class_name, section=section)

    if not output_path:
        os.makedirs("reports", exist_ok=True)
        c_tag = f"Class_{class_name}_{section}".replace(" ", "_")
        output_path = os.path.join("reports", f"Class_Report_{c_tag}.pdf")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    styles = _get_report_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    elements = []
    gen_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")

    # 1. Header
    header_data = [
        [
            Paragraph(f"<b>PMLA-SCWE</b> | Class Performance Report", styles["ReportHeaderTitle"]),
            Paragraph(f"<b>Date:</b> {gen_time}<br/><b>Target:</b> Class {class_name}-{section}", styles["BodySmallBold"])
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(t_header)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4A3AFF"), spaceAfter=10))

    # 2. Executive Overview Summary Cards
    kpi_data = [
        [
            Paragraph(f"<b>Cohort Size:</b> {overview['total_students']} Students", styles["BodySmallBold"]),
            Paragraph(f"<b>🔴 High Risk:</b> {overview['total_high']}", styles["BodySmallBold"]),
            Paragraph(f"<b>🟡 Medium Risk:</b> {overview['total_medium']}", styles["BodySmallBold"]),
            Paragraph(f"<b>🟢 Low Risk:</b> {overview['total_low']}", styles["BodySmallBold"])
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[135, 135, 135, 135])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 10))

    # 3. Primary Cohort Vulnerability
    vuln_data = [
        [
            Paragraph(f"<b>PRIMARY COHORT VULNERABILITY:</b> {overview['most_common_risk_factor']}", styles["BodySmallBold"])
        ]
    ]
    t_vuln = Table(vuln_data, colWidths=[540])
    t_vuln.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCD34D")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_vuln)
    elements.append(Spacer(1, 10))

    # 4. Donut Chart
    if opts.get("include_charts", True):
        try:
            chart_file = _generate_class_donut_chart(overview)
            if os.path.exists(chart_file):
                elements.append(Paragraph("<b>1. Risk Distribution Breakdown</b>", styles["SectionHeading"]))
                elements.append(Image(chart_file, width=4.5 * inch, height=2.2 * inch))
                elements.append(Spacer(1, 10))
        except Exception:
            pass

    # 5. Prioritized Students at Risk Roster Table
    elements.append(Paragraph("<b>2. Students Requiring Academic Monitoring & Intervention</b>", styles["SectionHeading"]))
    roster = overview.get("roster", [])
    if roster:
        table_rows = [
            [
                Paragraph("<b>ID</b>", styles["BodySmallBold"]),
                Paragraph("<b>Student Name</b>", styles["BodySmallBold"]),
                Paragraph("<b>Class</b>", styles["BodySmallBold"]),
                Paragraph("<b>Risk Tier</b>", styles["BodySmallBold"]),
                Paragraph("<b>Risk Score</b>", styles["BodySmallBold"]),
                Paragraph("<b>Primary Contributing Factor</b>", styles["BodySmallBold"])
            ]
        ]
        for s_item in roster:
            r_lvl = s_item.get("risk_level", "LOW")
            r_col = colors.HexColor("#EF4444") if r_lvl == "HIGH" else (colors.HexColor("#F59E0B") if r_lvl == "MEDIUM" else colors.HexColor("#10B981"))
            table_rows.append([
                Paragraph(f"#{s_item['student_id']}", styles["BodySmall"]),
                Paragraph(s_item["name"], styles["BodySmallBold"]),
                Paragraph(s_item.get("class_section", "N/A"), styles["BodySmall"]),
                Paragraph(f"<font color='{r_col.hexval()}'><b>{r_lvl}</b></font>", styles["BodySmallBold"]),
                Paragraph(f"{s_item.get('risk_score', 'N/A')}/100", styles["BodySmall"]),
                Paragraph(s_item.get("primary_factor", "General Review"), styles["BodySmall"])
            ])

        t_roster = Table(table_rows, colWidths=[40, 130, 60, 80, 70, 160])
        t_roster.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        elements.append(t_roster)
    else:
        elements.append(Paragraph("<i>No students flagged in this classroom filter.</i>", styles["BodySmall"]))

    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=6))
    elements.append(Paragraph(SAFETY_DISCLAIMER, styles["DisclaimerStyle"]))

    doc.build(elements)
    return output_path


# ---------------------------------------------------------------------------
# CSV Exporter Utility
# ---------------------------------------------------------------------------

def export_report_csv(
    report_type: str = REPORT_TYPE_CLASS_PERFORMANCE,
    class_name: str = "All",
    section: str = "All",
    student_id: int | None = None,
    output_path: str | None = None
) -> str:
    """Exports structured, comma-separated values compatible with spreadsheet software."""
    if not output_path:
        os.makedirs("reports", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("reports", f"{report_type.lower()}_{ts}.csv")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if report_type == REPORT_TYPE_STUDENT_INTELLIGENCE and student_id:
            profile = get_student_360_profile(student_id)
            if not profile:
                raise ValueError(f"Student ID #{student_id} not found.")

            s = profile["student"]
            acad = profile["academic"]
            att = profile["attendance"]
            lh = profile["learning_health"]
            well = profile["wellness"]
            pred = profile["prediction"]
            risk = profile.get("risk_engine", {})

            writer.writerow(["PMLA-SCWE STUDENT INTELLIGENCE REPORT"])
            writer.writerow(["Generated At", datetime.now().isoformat()])
            writer.writerow([])
            writer.writerow(["Student ID", s["id"]])
            writer.writerow(["Full Name", s["name"]])
            writer.writerow(["Class Section", s["class_section"]])
            writer.writerow(["Email", s["email"]])
            writer.writerow([])
            writer.writerow(["METRIC DIMENSION", "VALUE", "STATUS / BENCHMARK"])
            writer.writerow(["Academic Average", f"{(acad.get('average_score') or 0.0):.2f}%", acad.get("status") or "N/A"])
            writer.writerow(["Attendance Rate", f"{(att.get('percentage') or 0.0):.2f}%", att.get("status") or "N/A"])
            writer.writerow(["Learning Health Score", f"{(lh.get('score') or 0.0):.2f}/100", lh.get("label") or "N/A"])
            writer.writerow(["Composite Risk Score", f"{risk.get('risk_score', 'N/A')}/100", risk.get("risk_level") or "LOW"])
            writer.writerow(["Performance Trajectory", pred.get("trend_direction") or "Stable", f"Slope: {(pred.get('slope') or 0.0):.3f} pts/wk"])
            writer.writerow(["Cyber-Wellness Index", f"{(well.get('wellness_score') or 0.0):.2f}%", well.get("status_label") or "N/A"])
            writer.writerow(["Daily Screen Time", f"{(well.get('daily_screen_time') or 0.0):.2f} hours", ""])


        else: # Class cohort exporter
            overview = get_class_risk_overview(class_name=class_name, section=section)
            writer.writerow(["PMLA-SCWE CLASSROOM PERFORMANCE REPORT"])
            writer.writerow(["Class Filter", class_name, "Section Filter", section])
            writer.writerow(["Generated At", datetime.now().isoformat()])
            writer.writerow(["Total Students", overview["total_students"]])
            writer.writerow(["High Risk Count", overview["total_high"]])
            writer.writerow(["Medium Risk Count", overview["total_medium"]])
            writer.writerow(["Low Risk Count", overview["total_low"]])
            writer.writerow(["Primary Cohort Vulnerability", overview["most_common_risk_factor"]])
            writer.writerow([])
            writer.writerow([
                "Student ID", "Full Name", "Class Section", "Risk Tier",
                "Risk Score", "Academic Average (%)", "Attendance Rate (%)", "LHS Score"
            ])

            for item in overview.get("roster", []):
                summary = get_student_analytics_summary(item["student_id"])
                acad_avg = f"{summary['academic_average']:.1f}" if summary else "N/A"
                att_pct = f"{summary['attendance_percentage']:.1f}" if summary else "N/A"
                lhs_val = f"{summary['learning_health_score']:.1f}" if summary else "N/A"

                writer.writerow([
                    item["student_id"],
                    item["name"],
                    item.get("class_section", ""),
                    item.get("risk_level", ""),
                    item.get("risk_score", ""),
                    acad_avg,
                    att_pct,
                    lhs_val
                ])

    return output_path


# ---------------------------------------------------------------------------
# Formatted Markdown / Text Preview Generator
# ---------------------------------------------------------------------------

def generate_report_preview_text(
    report_type: str,
    student_id: int | None = None,
    class_name: str = "All",
    section: str = "All",
    options: dict[str, Any] | None = None
) -> str:
    """Generates an immediate structured Markdown preview for the user interface."""
    gen_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")

    if report_type == REPORT_TYPE_STUDENT_INTELLIGENCE and student_id:
        profile = get_student_360_profile(student_id)
        if not profile:
            return f"⚠️ Student ID #{student_id} not found in database."

        s = profile["student"]
        acad = profile["academic"]
        att = profile["attendance"]
        lh = profile["learning_health"]
        well = profile["wellness"]
        pred = profile["prediction"]
        risk = profile.get("risk_engine", {})

        lines = [
            f"# PMLA-SCWE STUDENT INTELLIGENCE REPORT",
            f"**Generated**: {gen_time} | **Student**: {s['name']} (#{s['id']}, {s['class_section']})",
            "",
            "## 1. Executive Summary",
            f"• **Risk Classification**: **{risk.get('risk_level', 'LOW')}** (Risk Score: **{risk.get('risk_score', 'N/A')}/100**)",
            f"• **Learning Health Score**: **{lh.get('display', 'N/A')}** ({lh.get('label', 'N/A')})",
            "",
            "## 2. Core Metrics Breakdown",
            f"• **Academic Performance**: {acad.get('display', 'N/A')} ({acad.get('status', 'N/A')}) — Weakest: {acad.get('weakest_subject', 'N/A')}",
            f"• **Attendance Rate**: {att.get('display', 'N/A')} ({att.get('present_count', 0)} Present, {att.get('absent_count', 0)} Absent)",
            f"• **Performance Trajectory**: {pred.get('trend_direction', 'N/A')} (Slope: {pred.get('slope', 0.0):.3f} pts/wk)",
            f"• **Cyber-Wellness Index**: {well.get('display', 'N/A')} (Daily Screen: {well.get('daily_screen_time', 'N/A')}h)",
            "",
            "## 3. Contributing Risk Factors",
        ]
        for f in risk.get("factors", []):
            lines.append(f"• **{f['name']}** (+{f['points_contributed']:.0f} pts): {f['evidence']}")
        if not risk.get("factors"):
            lines.append("• *No negative risk factors currently contributing to risk index.*")

        lines.extend([
            "",
            "## 4. Recommended Teacher Interventions",
        ])
        for iv in profile.get("interventions", []):
            lines.append(f"• [{iv.get('priority', 'MEDIUM')}] **{iv.get('title', '')}**: {iv.get('description', '')}")

        lines.extend([
            "",
            "---",
            f"*{SAFETY_DISCLAIMER}*"
        ])
        return "\n".join(lines)

    else: # Class report preview
        overview = get_class_risk_overview(class_name=class_name, section=section)
        lines = [
            f"# PMLA-SCWE CLASSROOM PERFORMANCE REPORT",
            f"**Generated**: {gen_time} | **Filter**: Class {class_name}-{section}",
            "",
            "## 1. Cohort Risk Distribution",
            f"• **Total Evaluated Cohort**: {overview['total_students']} Students",
            f"• 🔴 **High Risk Students**: {overview['total_high']}",
            f"• 🟡 **Medium Risk Students**: {overview['total_medium']}",
            f"• 🟢 **Low Risk Students**: {overview['total_low']}",
            f"• ⚪ **Insufficient Data**: {overview['total_insufficient']}",
            "",
            f"## 2. Primary Cohort Vulnerability",
            f"• **Primary Concern**: **{overview['most_common_risk_factor']}**",
            "",
            "## 3. Priority At-Risk Roster",
        ]
        for item in overview.get("roster", [])[:8]:
            lines.append(f"• **#{item['student_id']} {item['name']}** ({item.get('class_section', '')}) — {item.get('risk_level', '')} Risk ({item.get('risk_score', 'N/A')}/100)")

        lines.extend([
            "",
            "---",
            f"*{SAFETY_DISCLAIMER}*"
        ])
        return "\n".join(lines)
