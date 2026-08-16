"""Report generation and data export facade delegating to core.report_service."""

from __future__ import annotations
import csv
import os
from datetime import datetime
from .database import execute_select
from .analytics import get_student_analytics_summary
from . import recommendation
from . import report_service


# Export report service constants and functions
REPORT_TYPES = report_service.REPORT_TYPES
generate_student_pdf_report = report_service.generate_student_pdf_report
generate_class_pdf_report = report_service.generate_class_pdf_report
export_report_csv = report_service.export_report_csv
generate_report_preview_text = report_service.generate_report_preview_text


def get_class_summary_data() -> dict:
    """Aggregates class-wide statistics across all student analytics summaries."""
    rows = execute_select("SELECT student_id FROM Students")
    if not rows:
        return {
            "total_students": 0,
            "avg_academic": 0.0,
            "avg_attendance": 0.0,
            "avg_wellness": 0.0,
            "risk_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        }

    academics = []
    attendance = []
    wellness = []
    risk_dist = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for r in rows:
        summary = get_student_analytics_summary(r["student_id"])
        if not summary:
            continue
        academics.append(summary["academic_average"])
        attendance.append(summary["attendance_percentage"])
        wellness.append(summary["cyber_wellness_score"])
        risk_dist[summary["risk_level"]] = risk_dist.get(summary["risk_level"], 0) + 1

    total = len(academics)
    if total == 0:
        return {
            "total_students": 0,
            "avg_academic": 0.0,
            "avg_attendance": 0.0,
            "avg_wellness": 0.0,
            "risk_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        }

    return {
        "total_students": total,
        "avg_academic": sum(academics) / total,
        "avg_attendance": sum(attendance) / total,
        "avg_wellness": sum(wellness) / total,
        "risk_distribution": risk_dist
    }


def build_student_report(student_summary: dict) -> str:
    """Formats a structured, human-readable student performance text report."""
    insights = recommendation.explain_learning_insights(student_summary)
    plan = recommendation.generate_intervention_plan(student_summary)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = [
        "======================================================================",
        "                   PMLA-SCWE STUDENT PERFORMANCE REPORT",
        "======================================================================",
        f"Report Generated At : {timestamp}",
        f"Student ID          : {student_summary['student_id']}",
        f"Student Name        : {student_summary['student_name']}",
        f"Class/Section       : {student_summary['class_section']}",
        "----------------------------------------------------------------------",
        "KEY ANALYTICS SUMMARY",
        "----------------------------------------------------------------------",
        f"Academic Average Score : {student_summary['academic_average']:.2f}% ({student_summary['academic_status']})",
        f"Attendance Rate        : {student_summary['attendance_percentage']:.2f}% ({student_summary['attendance_status']})",
        f"Cyber-Wellness Index   : {student_summary['cyber_wellness_score']:.2f}% ({student_summary['wellness_status']})",
        f"Weekly Progress Trend  : {student_summary['trend']} (Current: {student_summary['current_score']:.2f}%)",
        f"Learning Health Score  : {student_summary['learning_health_score']:.2f}/100",
        f"Risk Classification    : {student_summary['risk_level']}"
    ]
    if student_summary.get('risk_reasons'):
        report.append(f"Flagged Reasons        : {', '.join(student_summary['risk_reasons'])}")
    report.extend([
        "----------------------------------------------------------------------",
        "EXPLAINABLE INSIGHTS",
        "----------------------------------------------------------------------"
    ])
    for ins in insights:
        report.append(f"- {ins}")
    report.extend([
        "----------------------------------------------------------------------",
        "PERSONALIZED INTERVENTION CHECKLIST",
        "----------------------------------------------------------------------"
    ])
    for item in plan:
        report.append(f"[ ] {item}")
    report.append("======================================================================")
    return "\n".join(report)


def build_teacher_report(class_summary: dict) -> str:
    """Formats a structured, human-readable class-wide performance text report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = [
        "======================================================================",
        "                     PMLA-SCWE CLASS ANALYTICS REPORT",
        "======================================================================",
        f"Report Generated At     : {timestamp}",
        f"Total Enrolled Students : {class_summary['total_students']}",
        "----------------------------------------------------------------------",
        "CLASS AVERAGES",
        "----------------------------------------------------------------------",
        f"Academic Performance Avg : {class_summary['avg_academic']:.2f}%",
        f"Attendance Rate Avg      : {class_summary['avg_attendance']:.2f}%",
        f"Cyber-Wellness Index Avg : {class_summary['avg_wellness']:.2f}%",
        "----------------------------------------------------------------------",
        "RISK DISTRIBUTION PROFILE",
        "----------------------------------------------------------------------"
    ]
    risk = class_summary.get("risk_distribution", {})
    report.extend([
        f"LOW RISK students        : {risk.get('LOW', 0)}",
        f"MEDIUM RISK students     : {risk.get('MEDIUM', 0)}",
        f"HIGH RISK students       : {risk.get('HIGH', 0)}",
        "======================================================================"
    ])
    return "\n".join(report)


def export_student_report_csv(student_id: int) -> str:
    """Exports a single student report as a CSV file and returns the filepath."""
    return report_service.export_report_csv(
        report_type=report_service.REPORT_TYPE_STUDENT_INTELLIGENCE,
        student_id=student_id
    )


def export_class_report_csv() -> str:
    """Exports the entire class report as a CSV file and returns the filepath."""
    return report_service.export_report_csv(
        report_type=report_service.REPORT_TYPE_CLASS_PERFORMANCE,
        class_name="All",
        section="All"
    )
