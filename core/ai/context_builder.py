"""Context Builder for PMLA-SCWE AI Teacher Copilot.

Grounded Data Pipeline:
Database ➔ Student Profile Service ➔ Risk Engine ➔ Explainability Engine ➔ Context Builder ➔ AI Provider

Ensures the AI model receives strictly grounded, calculated, and validated educational facts.
"""

from __future__ import annotations
from typing import Any


def build_grounded_student_context(student_id: int) -> dict[str, Any]:
    """Assembles a verified, structured fact payload for a student using the 360 profile service."""
    from core.student_profile_service import get_student_360_profile
    from core.risk_engine import compute_student_risk_profile

    profile = get_student_360_profile(student_id)
    if not profile:
        return {
            "found": False,
            "student_id": student_id,
            "text": f"No student record found for Student ID #{student_id}.",
            "data": None
        }

    s = profile["student"]
    lh = profile["learning_health"]
    acad = profile["academic"]
    att = profile["attendance"]
    prog = profile["weekly_progress"]
    well = profile["wellness"]
    pred = profile["prediction"]
    risk = profile.get("risk_engine", {})
    insights = profile.get("insights", [])
    interventions = profile.get("interventions", [])
    alerts = [a["title"] for a in profile.get("alerts", [])]

    # Calculate topic breakdown
    weakest_subj = acad.get("weakest_subject", "N/A")
    best_subj = acad.get("best_subject", "N/A")
    recent_assessments = acad.get("recent_assessments", [])

    lines = [
        "==================================================",
        f"VERIFIED PMLA-SCWE STUDENT INTELLIGENCE PROFILE",
        "==================================================",
        f"STUDENT IDENTITY:",
        f"• Student ID: #{s['id']}",
        f"• Name: {s['name']}",
        f"• Class & Section: {s['class_section']}",
        f"• Profile Completeness: {profile['profile_status']['data_completeness']}% ({profile['profile_status']['confidence_level']} Confidence)",
        "",
        "ACADEMIC PERFORMANCE:",
        f"• Academic Average: {acad.get('display', 'N/A')} (Status: {acad.get('status', 'N/A')})",
        f"• Strongest Area: {best_subj}",
        f"• Area Needing Practice: {weakest_subj}",
        f"• Total Assessments Recorded: {acad.get('total_tests', 0)}",
        "",
        "ATTENDANCE INTELLIGENCE:",
        f"• Attendance Rate: {att.get('display', 'N/A')} (Status: {att.get('status', 'N/A')})",
        f"• Total Tracked Days: {att.get('total_days', 0)} ({att.get('present_count', 0)} Present, {att.get('absent_count', 0)} Absent)",
        "",
        "PERFORMANCE TRAJECTORY & FORECAST:",
        f"• Trend Direction: {pred.get('trend_direction', 'N/A')}",
        f"• Regression Slope: {pred.get('slope', 0.0):.3f} pts/week",
        f"• Forecasted Next Score: {pred.get('display', 'N/A')}",
        f"• Weekly Milestone Progressions: {prog.get('total_weeks', 0)} weeks logged",
        "",
        "CYBER-WELLBEING & DIGITAL ROUTINE:",
        f"• Wellness Score: {well.get('display', 'N/A')} (Status: {well.get('status_label', 'N/A')})",
        f"• Daily Screen Exposure: {well.get('daily_screen_time', 'N/A')} hours (Study: {well.get('study_screen_time', 'N/A')}h, Recreation: {well.get('recreational_screen_time', 'N/A')}h)",
        f"• Sleep Duration: {well.get('sleep_duration', 'N/A')} hours/night",
        "",
        "EXPLAINABLE LEARNING RISK ENGINE:",
        f"• Learning Health Score (LHS): {lh.get('display', 'N/A')} (Tier: {lh.get('label', 'N/A')})",
        f"• Composite Risk Score: {risk.get('risk_score', 'N/A')}/100",
        f"• Assigned Risk Level: {risk.get('risk_level', 'INSUFFICIENT DATA')}",
        f"• Active Warning Flags: {', '.join(alerts) if alerts else 'None'}",
        "",
        "DATA-DRIVEN CONTRIBUTING FACTORS & EVIDENCE:"
    ]

    factors = risk.get("factors", [])
    if factors:
        for f in factors:
            lines.append(f"• {f['name']} (+{f['points_contributed']:.0f} pts, {f['impact'].upper()} impact): {f['evidence']}")
    else:
        lines.append("• No negative contributing risk factors flagged.")

    lines.append("")
    lines.append("EXISTING DETERMINISTIC RECOMMENDATIONS:")
    if interventions:
        for iv in interventions:
            lines.append(f"• [{iv.get('priority', 'MEDIUM')} Priority] {iv.get('title', '')}: {iv.get('description', '')}")
    else:
        lines.append("• Continue standard curriculum reinforcement.")

    return {
        "found": True,
        "student_id": s["id"],
        "student_name": s["name"],
        "class_section": s["class_section"],
        "text": "\n".join(lines),
        "profile": profile,
        "weak_topic": weakest_subj,
        "recent_assessments": recent_assessments
    }


def build_class_context(class_name: str | None = None, section: str | None = None) -> dict[str, Any]:
    """Assembles aggregate, privacy-safe classroom metrics for teacher decision support."""
    from core.risk_engine import get_class_risk_overview

    overview = get_class_risk_overview(class_name=class_name or "All", section=section or "All")
    c_label = f"Class {class_name or 'All'}-{section or 'All'}"

    lines = [
        "==================================================",
        f"CLASSROOM AGGREGATE METRICS SUMMARY — {c_label}",
        "==================================================",
        f"• Total Registered Cohort: {overview['total_students']} Students",
        f"• Filtered Subset Size: {overview['filtered_count']} Students",
        "",
        "RISK TIER DISTRIBUTION:",
        f"• 🔴 High Risk Students: {overview['total_high']} (Requires targeted support)",
        f"• 🟡 Medium Risk Students: {overview['total_medium']} (Requires monitoring)",
        f"• 🟢 Low Risk Students: {overview['total_low']} (Meeting expectations)",
        f"• ⚪ Insufficient Data: {overview['total_insufficient']} (Awaiting assessment)",
        "",
        "COHORT VULNERABILITY ANALYSIS:",
        f"• Primary Common Factor: {overview['most_common_risk_factor']}"
    ]

    return {
        "class_name": class_name or "All",
        "section": section or "All",
        "total_students": overview["total_students"],
        "overview": overview,
        "text": "\n".join(lines)
    }


def build_comparison_context(student_id_1: int, student_id_2: int) -> dict[str, Any]:
    """Assembles side-by-side facts for two students in a constructive, non-humiliating manner."""
    ctx_1 = build_grounded_student_context(student_id_1)
    ctx_2 = build_grounded_student_context(student_id_2)

    if not ctx_1["found"] or not ctx_2["found"]:
        missing = []
        if not ctx_1["found"]:
            missing.append(f"Student #{student_id_1}")
        if not ctx_2["found"]:
            missing.append(f"Student #{student_id_2}")
        return {
            "valid": False,
            "text": f"Cannot perform comparison: {', '.join(missing)} not found.",
            "student_1": ctx_1,
            "student_2": ctx_2
        }

    p1 = ctx_1["profile"]
    p2 = ctx_2["profile"]
    s1, s2 = p1["student"], p2["student"]

    lines = [
        "==================================================",
        f"CONSTRUCTIVE COMPARATIVE METRICS MATRIX",
        "==================================================",
        f"STUDENT A: {s1['name']} (#{s1['id']}, {s1['class_section']})",
        f"• Academic Average: {p1['academic'].get('display', 'N/A')} (Weakest: {p1['academic'].get('weakest_subject', 'N/A')})",
        f"• Attendance: {p1['attendance'].get('display', 'N/A')}",
        f"• Trajectory / Slope: {p1['prediction'].get('trend_direction', 'N/A')} ({p1['prediction'].get('slope', 0.0):.2f} pts/wk)",
        f"• Learning Health Score: {p1['learning_health'].get('display', 'N/A')}",
        f"• Composite Risk: {p1.get('risk_engine', {}).get('risk_score', 'N/A')}/100 ({p1.get('risk_engine', {}).get('risk_level', 'N/A')})",
        f"• Daily Screen Time: {p1['wellness'].get('daily_screen_time', 'N/A')}h",
        "",
        f"STUDENT B: {s2['name']} (#{s2['id']}, {s2['class_section']})",
        f"• Academic Average: {p2['academic'].get('display', 'N/A')} (Weakest: {p2['academic'].get('weakest_subject', 'N/A')})",
        f"• Attendance: {p2['attendance'].get('display', 'N/A')}",
        f"• Trajectory / Slope: {p2['prediction'].get('trend_direction', 'N/A')} ({p2['prediction'].get('slope', 0.0):.2f} pts/wk)",
        f"• Learning Health Score: {p2['learning_health'].get('display', 'N/A')}",
        f"• Composite Risk: {p2.get('risk_engine', {}).get('risk_score', 'N/A')}/100 ({p2.get('risk_engine', {}).get('risk_level', 'N/A')})",
        f"• Daily Screen Time: {p2['wellness'].get('daily_screen_time', 'N/A')}h",
        "",
        "COMPARISON GUIDELINES FOR COPILOT:",
        "1. Highlight complementary strengths and distinct individual learning trajectories.",
        "2. Provide constructive, respectful pedagogical opportunities for both students.",
        "3. Avoid ranking or demoralizing terminology."
    ]

    return {
        "valid": True,
        "student_1": ctx_1,
        "student_2": ctx_2,
        "text": "\n".join(lines)
    }
