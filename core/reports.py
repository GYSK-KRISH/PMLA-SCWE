"""Report generation and data export services."""

from __future__ import annotations
import csv
import os
from datetime import datetime
from .database import execute_select
from .analytics import get_student_analytics_summary
from . import recommendation


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

    report = []
    report.append("======================================================================")
    report.append("                   PMLA-SCWE STUDENT PERFORMANCE REPORT")
    report.append("======================================================================")
    report.append(f"Report Generated At : {timestamp}")
    report.append(f"Student ID          : {student_summary['student_id']}")
    report.append(f"Student Name        : {student_summary['student_name']}")
    report.append(f"Class/Section       : {student_summary['class_section']}")
    report.append("----------------------------------------------------------------------")
    report.append("KEY ANALYTICS SUMMARY")
    report.append("----------------------------------------------------------------------")
    report.append(f"Academic Average Score : {student_summary['academic_average']:.2f}% ({student_summary['academic_status']})")
    report.append(f"Attendance Rate        : {student_summary['attendance_percentage']:.2f}% ({student_summary['attendance_status']})")
    report.append(f"Cyber-Wellness Index   : {student_summary['cyber_wellness_score']:.2f}% ({student_summary['wellness_status']})")
    report.append(f"Weekly Progress Trend  : {student_summary['trend']} (Current: {student_summary['current_score']:.2f}%)")
    report.append(f"Learning Health Score  : {student_summary['learning_health_score']:.2f}/100")
    report.append(f"Risk Classification    : {student_summary['risk_level']}")
    if student_summary['risk_reasons']:
        report.append(f"Flagged Reasons        : {', '.join(student_summary['risk_reasons'])}")
    report.append("----------------------------------------------------------------------")
    report.append("EXPLAINABLE INSIGHTS")
    report.append("----------------------------------------------------------------------")
    for ins in insights:
        report.append(f"- {ins}")
    report.append("----------------------------------------------------------------------")
    report.append("PERSONALIZED INTERVENTION CHECKLIST")
    report.append("----------------------------------------------------------------------")
    for item in plan:
        report.append(f"[ ] {item}")
    report.append("======================================================================")
    
    return "\n".join(report)


def build_teacher_report(class_summary: dict) -> str:
    """Formats a structured, human-readable class-wide performance text report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = []
    report.append("======================================================================")
    report.append("                     PMLA-SCWE CLASS ANALYTICS REPORT")
    report.append("======================================================================")
    report.append(f"Report Generated At    : {timestamp}")
    report.append(f"Total Enrolled Students : {class_summary['total_students']}")
    report.append("----------------------------------------------------------------------")
    report.append("CLASS AVERAGES")
    report.append("----------------------------------------------------------------------")
    report.append(f"Academic Performance Avg : {class_summary['avg_academic']:.2f}%")
    report.append(f"Attendance Rate Avg      : {class_summary['avg_attendance']:.2f}%")
    report.append(f"Cyber-Wellness Index Avg : {class_summary['avg_wellness']:.2f}%")
    report.append("----------------------------------------------------------------------")
    report.append("RISK DISTRIBUTION PROFILE")
    report.append("----------------------------------------------------------------------")
    risk = class_summary["risk_distribution"]
    report.append(f"LOW RISK students        : {risk.get('LOW', 0)}")
    report.append(f"MEDIUM RISK students     : {risk.get('MEDIUM', 0)}")
    report.append(f"HIGH RISK students       : {risk.get('HIGH', 0)}")
    report.append("======================================================================")
    
    return "\n".join(report)


def export_student_report_csv(student_id: int) -> str:
    """Exports a single student report as a CSV file and returns the filepath."""
    summary = get_student_analytics_summary(student_id)
    if not summary:
        raise ValueError(f"Student ID {student_id} not found.")

    os.makedirs("reports", exist_ok=True)
    filepath = f"reports/student_{student_id}_report.csv"

    # Define headers
    headers = [
        "Metric", "Value", "Status"
    ]
    rows = [
        ["Student ID", summary["student_id"], ""],
        ["Student Name", summary["student_name"], ""],
        ["Class Section", summary["class_section"], ""],
        ["Academic Average (%)", f"{summary['academic_average']:.2f}", summary["academic_status"]],
        ["Attendance (%)", f"{summary['attendance_percentage']:.2f}", summary["attendance_status"]],
        ["Cyber-Wellness Score (%)", f"{summary['cyber_wellness_score']:.2f}", summary["wellness_status"]],
        ["Learning Health Score", f"{summary['learning_health_score']:.2f}", ""],
        ["Risk Level", summary["risk_level"], ""],
        ["Risk Reasons", ", ".join(summary["risk_reasons"]), ""],
        ["Predicted Next Score (%)", f"{summary['predicted_next_score']:.2f}", ""],
        ["Trend Direction", summary["trend"], ""]
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return filepath


def export_class_report_csv() -> str:
    """Exports the entire class report as a CSV file and returns the filepath."""
    os.makedirs("reports", exist_ok=True)
    filepath = "reports/class_report.csv"

    rows = execute_select("SELECT student_id FROM Students ORDER BY student_id")
    
    headers = [
        "Student ID", "Student Name", "Class Section", 
        "Academic Average", "Attendance Rate", "Cyber-Wellness Score", 
        "Learning Health Score", "Risk Level"
    ]

    records = []
    for r in rows:
        summary = get_student_analytics_summary(r["student_id"])
        if not summary:
            continue
        records.append([
            summary["student_id"],
            summary["student_name"],
            summary["class_section"],
            round(summary["academic_average"], 2),
            round(summary["attendance_percentage"], 2),
            round(summary["cyber_wellness_score"], 2),
            round(summary["learning_health_score"], 2),
            summary["risk_level"]
        ])

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)

    return filepath
