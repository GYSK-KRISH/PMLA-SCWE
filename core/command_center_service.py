"""Executive Academic Intelligence Command Center Service for PMLA-SCWE.

Version 1.7 — Academic Intelligence Command Center & Smart Notification Engine
Aggregates and synthesizes data from:
- Student 360° Profile Engine
- Explainable Risk & Analytics Engine
- Smart Notification & Decision Center
- Intervention Tracking & Outcome Intelligence
- Cyber-Wellbeing & Attendance Registries

Provides a single unified payload powering the Executive Command Center on Desktop and Web.
"""

from __future__ import annotations
from typing import Any

from core import (
    student_service, attendance_service, assessment_service,
    wellness_service, analytics, risk_engine,
    intervention_service, intervention_analytics, notification_service
)
from core.database import get_db_status, execute_query


def get_executive_command_center_data() -> dict[str, Any]:
    """Single Source of Truth aggregating all institutional intelligence into an executive overview."""
    students = student_service.get_all_students()
    total_students = len(students)

    # 1. Database & System Status
    db_status = get_db_status()

    # 2. Aggregations & Metrics
    total_score = 0.0
    scored_students = 0
    total_att_pct = 0.0
    att_students = 0
    total_wellness = 0.0
    wellness_students = 0
    total_lhs = 0.0
    lhs_students = 0

    high_risk_students = []
    moderate_risk_students = []
    low_risk_students = []

    for s in students:
        sid = s["student_id"]
        # Academic
        scores = assessment_service.get_student_scores(sid)
        if scores:
            avg_s = sum(sc["score_obtained"] for sc in scores) / len(scores)
            total_score += avg_s
            scored_students += 1
        else:
            avg_s = None

        # Attendance
        att = attendance_service.get_student_attendance(sid)
        if att:
            tot = len(att)
            pres = sum(1 for a in att if a["status"] == "P")
            att_pct = (pres / tot) * 100.0
            total_att_pct += att_pct
            att_students += 1
        else:
            att_pct = None

        # Wellness
        w_score = wellness_service.get_student_wellness_score(sid)
        if w_score is not None:
            total_wellness += w_score
            wellness_students += 1

        # Risk Engine Synthesis
        r_prof = risk_engine.compute_student_risk_profile(sid)
        r_lvl = r_prof.get("risk_level", "LOW")
        r_score = r_prof.get("risk_score", 0)

        student_summary = {
            "student_id": sid,
            "name": f"{s['first_name']} {s['last_name']}",
            "class_section": s.get("class_section", "XII-A"),
            "academic_avg": avg_s,
            "attendance_pct": att_pct,
            "wellness_score": w_score,
            "risk_level": r_lvl,
            "risk_score": r_score,
            "primary_concern": r_prof.get("factors", [{}])[0].get("name", "None") if r_prof.get("factors") else "Stable",
            "trend": r_prof.get("trend", "stable")
        }

        if r_lvl == "HIGH":
            high_risk_students.append(student_summary)
        elif r_lvl == "MEDIUM":
            moderate_risk_students.append(student_summary)
        else:
            low_risk_students.append(student_summary)

    # Sort priority students by risk score descending
    high_risk_students.sort(key=lambda x: x["risk_score"] or 0, reverse=True)
    moderate_risk_students.sort(key=lambda x: x["risk_score"] or 0, reverse=True)

    class_avg_performance = round(total_score / scored_students, 1) if scored_students > 0 else 0.0
    class_avg_attendance = round(total_att_pct / att_students, 1) if att_students > 0 else 0.0
    class_avg_wellness = round(total_wellness / wellness_students, 1) if wellness_students > 0 else 0.0

    # Composite Class Health Score
    class_lhs = round((class_avg_performance * 0.40) + (class_avg_attendance * 0.40) + (class_avg_wellness * 0.20), 1)

    # 3. Interventions Overview
    interventions = intervention_service.get_all_interventions()
    iv_metrics = intervention_analytics.aggregate_cohort_intervention_metrics(interventions)

    # 4. Notifications & Alerts Overview
    unread_alerts = notification_service.get_unread_notification_count()
    high_prio_alerts = notification_service.get_high_priority_count()
    recent_alerts = notification_service.get_notifications(limit=5)

    # 5. Smart Teacher Action Recommendations (Auto-Grounded)
    smart_actions = []
    if high_prio_alerts > 0:
        smart_actions.append({
            "priority": "HIGH",
            "title": f"Review {high_prio_alerts} Urgent High-Priority Alert(s)",
            "description": "Critical attendance thresholds or acute risk escalations require immediate teacher action.",
            "target": "notifications"
        })

    if len(high_risk_students) > 0:
        top_s = high_risk_students[0]
        smart_actions.append({
            "priority": "HIGH",
            "title": f"Initiate Remedial Intervention: {top_s['name']}",
            "description": f"Flagged at High Risk (Score: {top_s['risk_score']}/100) due to {top_s['primary_concern']}.",
            "target": "interventions",
            "student_id": top_s["student_id"]
        })
    elif len(moderate_risk_students) > 0:
        top_s = moderate_risk_students[0]
        smart_actions.append({
            "priority": "MEDIUM",
            "title": f"Review At-Risk Student: {top_s['name']}",
            "description": f"Flagged at Moderate Risk (Score: {top_s['risk_score']}/100) due to {top_s['primary_concern']}.",
            "target": "interventions",
            "student_id": top_s["student_id"]
        })


    active_iv_count = iv_metrics.get("active_count", 0)
    if active_iv_count > 0:
        smart_actions.append({
            "priority": "MEDIUM",
            "title": f"Monitor {active_iv_count} Active Intervention Pipeline Cases",
            "description": "Track ongoing remediation progress and verify weekly diagnostic assessment logs.",
            "target": "interventions"
        })

    if class_avg_attendance < 75.0:
        smart_actions.append({
            "priority": "HIGH",
            "title": "Classroom Attendance Rate Below CBSE 75% Target",
            "description": f"Cohort attendance is currently at {class_avg_attendance}%. Issue guardian attendance advisories.",
            "target": "attendance"
        })

    if not smart_actions:
        smart_actions.append({
            "priority": "SUCCESS",
            "title": "All Student Learning Indicators Stable",
            "description": "Cohort performance, attendance, and cyber-wellness are within healthy target ranges.",
            "target": "analytics"
        })

    return {
        "summary": {
            "total_students": total_students,
            "class_average_performance": class_avg_performance,
            "class_average_attendance": class_avg_attendance,
            "class_average_wellness": class_avg_wellness,
            "class_learning_health_score": class_lhs,
            "high_risk_count": len(high_risk_students),
            "moderate_risk_count": len(moderate_risk_students),
            "low_risk_count": len(low_risk_students),
            "active_interventions": iv_metrics.get("active_count", 0),
            "completed_interventions": iv_metrics.get("completed_count", 0),
            "resolution_rate": iv_metrics.get("resolution_rate", 0.0),
            "unread_alerts_count": unread_alerts,
            "high_priority_alerts_count": high_prio_alerts,
        },
        "health_distribution": {
            "healthy": len(low_risk_students),
            "moderate": len(moderate_risk_students),
            "critical": len(high_risk_students),
        },
        "top_priority_students": high_risk_students[:5] if high_risk_students else moderate_risk_students[:5],
        "intervention_outcomes": iv_metrics,
        "recent_alerts": recent_alerts,
        "smart_teacher_actions": smart_actions,
        "db_status": db_status
    }
