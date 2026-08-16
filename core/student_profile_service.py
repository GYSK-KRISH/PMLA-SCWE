"""Student 360° Intelligence Profile Aggregation Layer.

Version 1.2 — Student 360° Intelligence Profile
Strict Single Source of Truth for Student Analytical Intelligence.

Synthesizes:
- Student Demographic & Registration Details
- Data Completeness & Confidence Scoring
- Learning Health Score with missing-data-aware dynamic normalization
- Academic Performance (averages, diagnostic history, best/weakest topics)
- Attendance Intelligence (rates, counts, recent patterns)
- Weekly Progress Analytics (scores, trend direction)
- Cyber-Wellbeing & Digital Screen Time (sleep, screen balance, distraction, safety)
- Predictive Forecasting (linear regression next-week score)
- Active Flagged Alerts (severity: HIGH, MEDIUM, INFO)
- Explainable Insights ("Why does this student need attention?")
- Structured Deterministic Interventions (priorities: HIGH, MEDIUM, LOW)
- Unified Chronological Learning Timeline
"""

from __future__ import annotations
from typing import Any
import datetime
from .database import execute_query, execute_select
from . import analytics, recommendation, attendance_service, wellness_service


def get_student_360_profile(student_id: int) -> dict[str, Any] | None:
    """Retrieve and synthesize the complete 360° analytical profile for a student.

    Returns None if student_id is invalid or does not exist.
    """
    # -----------------------------------------------------------------------
    # 1. Base Student Information
    # -----------------------------------------------------------------------
    student_rows = execute_select(
        "SELECT student_id, first_name, last_name, class_section, dob, gender, "
        "email, phone, enrollment_date FROM Students WHERE student_id = %s",
        (student_id,)
    )
    if not student_rows:
        return None

    s = student_rows[0]
    first_name = s.get("first_name", "")
    last_name = s.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()
    class_sec = s.get("class_section", "N/A")
    
    # Parse class and section
    class_name = class_sec
    section_name = ""
    if "-" in class_sec:
        parts = class_sec.split("-", 1)
        class_name = parts[0].strip()
        section_name = parts[1].strip()

    student_dict = {
        "id": int(s["student_id"]),
        "first_name": first_name,
        "last_name": last_name,
        "name": full_name,
        "class_section": class_sec,
        "class": class_name,
        "section": section_name,
        "dob": str(s.get("dob") or ""),
        "gender": s.get("gender", "O"),
        "email": s.get("email") or "N/A",
        "phone": s.get("phone") or "N/A",
        "enrollment_date": str(s.get("enrollment_date") or ""),
        "status": "Active"
    }

    # -----------------------------------------------------------------------
    # 2. Academic Intelligence (Diagnostic Logs)
    # -----------------------------------------------------------------------
    diag_rows = execute_select(
        "SELECT log_id, student_id, objective_id, score_obtained, max_score, test_date "
        "FROM Diagnostic_Logs WHERE student_id = %s ORDER BY test_date ASC, log_id ASC",
        (student_id,)
    )

    academic_has_data = len(diag_rows) > 0
    if academic_has_data:
        scores_pct = []
        recent_assessments = []
        for r in diag_rows:
            obtained = float(r.get("score_obtained", 0))
            max_s = float(r.get("max_score", 100) or 100)
            pct = (obtained / max_s * 100.0) if max_s > 0 else 0.0
            scores_pct.append(pct)
            
            recent_assessments.append({
                "log_id": r.get("log_id"),
                "objective_id": r.get("objective_id"),
                "score_obtained": obtained,
                "max_score": max_s,
                "percentage": round(pct, 1),
                "date": str(r.get("test_date") or "")
            })

        academic_avg = round(sum(scores_pct) / len(scores_pct), 1)
        academic_status = analytics.classify_academic_status(academic_avg)
        
        # Best & weakest assessments
        sorted_by_score = sorted(recent_assessments, key=lambda x: x["percentage"])
        weakest = f"Assessment #{sorted_by_score[0]['objective_id'] or sorted_by_score[0]['log_id']} ({sorted_by_score[0]['percentage']}%)"
        best = f"Assessment #{sorted_by_score[-1]['objective_id'] or sorted_by_score[-1]['log_id']} ({sorted_by_score[-1]['percentage']}%)"
        
        academic_dict = {
            "has_data": True,
            "average_score": academic_avg,
            "display": f"{academic_avg:.1f}%",
            "status": academic_status,
            "total_assessments": len(diag_rows),
            "recent_assessments": list(reversed(recent_assessments)),
            "best_subject": best,
            "weakest_subject": weakest
        }
    else:
        academic_avg = None
        academic_status = "Not Assessed"
        academic_dict = {
            "has_data": False,
            "average_score": None,
            "display": "Not enough data yet",
            "status": "Not Assessed",
            "total_assessments": 0,
            "recent_assessments": [],
            "best_subject": "N/A",
            "weakest_subject": "N/A"
        }

    # -----------------------------------------------------------------------
    # 3. Weekly Progress Analytics
    # -----------------------------------------------------------------------
    prog_rows = execute_select(
        "SELECT week_id, week_start, score FROM Weekly_Progress "
        "WHERE student_id = %s ORDER BY week_start ASC",
        (student_id,)
    )


    prog_has_data = len(prog_rows) > 0
    if prog_has_data:
        prog_scores = [float(r["score"]) for r in prog_rows if r.get("score") is not None]
        prog_weeks = [str(r.get("week_start") or "") for r in prog_rows]
        prog_current = prog_scores[-1] if prog_scores else 0.0
        prog_avg = round(sum(prog_scores) / len(prog_scores), 1) if prog_scores else 0.0
        
        # Regression prediction
        pred_res = analytics.predict_next_score(student_id)
        trend_direction = pred_res.get("trend_direction", "Stable")
        predicted_score = round(pred_res.get("predicted_score", prog_current), 1)
        slope = round(pred_res.get("slope", 0.0), 3)

        weekly_dict = {
            "has_data": True,
            "current_score": prog_current,
            "average_score": prog_avg,
            "display": f"{prog_current:.1f}%",
            "scores": prog_scores,
            "weeks": prog_weeks,
            "total_weeks": len(prog_scores),
            "trend_direction": trend_direction
        }
    else:
        prog_current = None
        prog_avg = None
        trend_direction = "Stable"
        predicted_score = None
        slope = 0.0
        weekly_dict = {
            "has_data": False,
            "current_score": None,
            "average_score": None,
            "display": "Not enough data yet",
            "scores": [],
            "weeks": [],
            "total_weeks": 0,
            "trend_direction": "Stable"
        }

    # -----------------------------------------------------------------------
    # 4. Attendance Intelligence
    # -----------------------------------------------------------------------
    att_rows = execute_select(
        "SELECT attendance_id, attendance_date, status FROM Attendance "
        "WHERE student_id = %s ORDER BY attendance_date ASC",
        (student_id,)
    )

    att_has_data = len(att_rows) > 0
    if att_has_data:
        present_cnt = sum(1 for r in att_rows if r.get("status") in ("P", "Present"))
        absent_cnt = sum(1 for r in att_rows if r.get("status") in ("A", "Absent"))
        total_days = len(att_rows)
        att_rate = round((present_cnt / total_days * 100.0), 1) if total_days > 0 else 0.0

        if att_rate >= 85.0:
            att_status = "Satisfactory"
        elif att_rate < 75.0:
            att_status = "Critical"
        else:
            att_status = "Monitoring Required"

        # Recent pattern (last 10 days)
        recent_att = [
            {"date": str(r.get("attendance_date") or ""), "status": "Present" if r.get("status") in ("P", "Present") else "Absent"}
            for r in att_rows[-10:]
        ]

        attendance_dict = {
            "has_data": True,
            "percentage": att_rate,
            "display": f"{att_rate:.1f}%",
            "present_count": present_cnt,
            "absent_count": absent_cnt,
            "total_days": total_days,
            "status": att_status,
            "recent_records": list(reversed(recent_att))
        }
    else:
        att_rate = None
        att_status = "Not Recorded"
        attendance_dict = {
            "has_data": False,
            "percentage": None,
            "display": "Not enough data yet",
            "present_count": 0,
            "absent_count": 0,
            "total_days": 0,
            "status": "Not Recorded",
            "recent_records": []
        }

    # -----------------------------------------------------------------------
    # 5. Cyber-Wellbeing & Digital Behaviour
    # -----------------------------------------------------------------------
    wellness_rows = execute_select(
        "SELECT audit_id, audit_date, daily_screen_time, study_screen_time, "
        "recreational_screen_time, sleep_duration, digital_distraction_level, "
        "cyber_safety_awareness, wellness_score FROM Cyber_Audit "
        "WHERE student_id = %s ORDER BY audit_date ASC",
        (student_id,)
    )

    wellness_has_data = len(wellness_rows) > 0
    if wellness_has_data:
        latest_audit = wellness_rows[-1]
        wellness_score = float(latest_audit.get("wellness_score", 70.0))
        daily_screen = float(latest_audit.get("daily_screen_time", 2.0))
        study_screen = float(latest_audit.get("study_screen_time", 1.0))
        rec_screen = float(latest_audit.get("recreational_screen_time", 1.0))
        sleep_hrs = float(latest_audit.get("sleep_duration", 8.0))
        distraction = int(latest_audit.get("digital_distraction_level", 1))
        safety = int(latest_audit.get("cyber_safety_awareness", 5))

        if wellness_score >= 80.0 and daily_screen <= 3.0:
            wellness_status = "Good"
            wellness_label = "Healthy Digital Routine"
        elif wellness_score < 55.0 or daily_screen > 6.0:
            wellness_status = "Concern"
            wellness_label = "Requires Attention"
        else:
            wellness_status = "Satisfactory"
            wellness_label = "Moderate Engagement"

        audit_history = [
            {
                "audit_id": r.get("audit_id"),
                "date": str(r.get("audit_date") or ""),
                "score": float(r.get("wellness_score", 0)),
                "screen_time": float(r.get("daily_screen_time", 0)),
                "sleep": float(r.get("sleep_duration", 0))
            }
            for r in wellness_rows
        ]

        wellness_dict = {
            "has_data": True,
            "wellness_score": wellness_score,
            "display": f"{wellness_score:.1f}%",
            "daily_screen_time": daily_screen,
            "study_screen_time": study_screen,
            "recreational_screen_time": rec_screen,
            "sleep_duration": sleep_hrs,
            "distraction_level": distraction,
            "safety_awareness": safety,
            "status": wellness_status,
            "status_label": wellness_label,
            "audit_history": list(reversed(audit_history))
        }
    else:
        wellness_score = None
        wellness_status = "Not Audited"
        wellness_dict = {
            "has_data": False,
            "wellness_score": None,
            "display": "Not enough data yet",
            "daily_screen_time": None,
            "study_screen_time": None,
            "recreational_screen_time": None,
            "sleep_duration": None,
            "distraction_level": None,
            "safety_awareness": None,
            "status": "Not Audited",
            "status_label": "Audit Pending",
            "audit_history": []
        }

    # -----------------------------------------------------------------------
    # 6. Data Completeness & Dynamic LHS Normalization
    # -----------------------------------------------------------------------
    # Component weights: Academic 40%, Progress 25%, Attendance 20%, Wellness 15%
    weights_map = {
        "academic": (40.0, academic_avg, academic_has_data),
        "progress": (25.0, prog_current if prog_has_data else None, prog_has_data),
        "attendance": (20.0, att_rate, att_has_data),
        "wellness": (15.0, wellness_score, wellness_has_data),
    }

    available_weight = 0.0
    weighted_sum = 0.0
    components_breakdown = {}

    for comp_name, (w, val, has_d) in weights_map.items():
        if has_d and val is not None:
            available_weight += w
            contrib = (val * w) / 100.0
            weighted_sum += contrib
            components_breakdown[comp_name] = {
                "has_data": True,
                "score": round(val, 1),
                "weight": w,
                "weighted_score": round(contrib, 2),
                "display": f"{val:.1f}%"
            }
        else:
            components_breakdown[comp_name] = {
                "has_data": False,
                "score": None,
                "weight": w,
                "weighted_score": 0.0,
                "display": "Not enough data yet"
            }

    data_completeness = int(round(available_weight))
    
    if data_completeness >= 75:
        confidence_level = "High Confidence"
    elif data_completeness >= 50:
        confidence_level = "Moderate Confidence"
    elif data_completeness >= 25:
        confidence_level = "Limited Confidence"
    else:
        confidence_level = "Insufficient Data"

    # Normalized LHS calculation
    if available_weight > 0:
        # Normalized score out of 100
        normalized_lhs = round((weighted_sum / available_weight) * 100.0, 1)
        
        # Risk classification based on normalized LHS and specific risk vectors
        effective_att = att_rate if att_rate is not None else 100.0
        effective_acad = academic_avg if academic_avg is not None else 100.0
        
        if normalized_lhs < 50.0 or effective_att < 75.0 or (effective_acad < 50.0 and trend_direction == "Declining"):
            risk_level = "HIGH"
            lhs_label = "Requires Immediate Support"
        elif normalized_lhs < 70.0 or effective_att < 85.0 or (wellness_score is not None and wellness_score < 60.0) or trend_direction == "Declining":
            risk_level = "MEDIUM"
            lhs_label = "Needs Targeted Attention"
        else:
            risk_level = "LOW"
            lhs_label = "On Track & Healthy"

        learning_health_dict = {
            "has_data": True,
            "score": normalized_lhs,
            "display": f"{normalized_lhs:.1f}/100",
            "risk_level": risk_level,
            "label": lhs_label,
            "available_weight": int(available_weight),
            "data_completeness": data_completeness,
            "confidence_level": confidence_level,
            "components": components_breakdown
        }
    else:
        # Absolutely zero data available for this student
        learning_health_dict = {
            "has_data": False,
            "score": None,
            "display": "Not enough data yet",
            "risk_level": "PENDING",
            "label": "Data Pending",
            "available_weight": 0,
            "data_completeness": 0,
            "confidence_level": "Insufficient Data",
            "components": components_breakdown
        }

    # -----------------------------------------------------------------------
    # 7. Prediction Intelligence
    # -----------------------------------------------------------------------
    if prog_has_data and predicted_score is not None:
        prediction_dict = {
            "has_data": True,
            "current_score": prog_current,
            "predicted_score": predicted_score,
            "display": f"{predicted_score:.1f}%",
            "slope": slope,
            "trend_direction": trend_direction,
            "confidence_text": f"Based on {len(prog_scores)} weekly evaluation points." if len(prog_scores) >= 3 else "Initial forecast — more weekly data recommended."
        }
    else:
        prediction_dict = {
            "has_data": False,
            "current_score": None,
            "predicted_score": None,
            "display": "Not enough data yet",
            "slope": 0.0,
            "trend_direction": "Stable",
            "confidence_text": "Requires at least 2 weeks of evaluation records."
        }

    # -----------------------------------------------------------------------
    # 8. Active Alerts & Explainable Insights
    # -----------------------------------------------------------------------
    alerts = []
    insights = []

    # Alerts
    if academic_has_data and academic_avg is not None and academic_avg < 60.0:
        alerts.append({
            "id": "low_academic",
            "severity": "HIGH" if academic_avg < 50.0 else "MEDIUM",
            "title": "Academic Performance Below Target",
            "description": f"Overall assessment average is {academic_avg:.1f}%."
        })

    if att_has_data and att_rate is not None:
        if att_rate < 75.0:
            alerts.append({
                "id": "critical_attendance",
                "severity": "HIGH",
                "title": "Critical Attendance Drop",
                "description": f"Attendance has fallen to {att_rate:.1f}% ({absent_cnt} absences recorded)."
            })
        elif att_rate < 85.0:
            alerts.append({
                "id": "moderate_attendance",
                "severity": "MEDIUM",
                "title": "Attendance Below Desired Threshold",
                "description": f"Attendance is at {att_rate:.1f}% and requires monitoring."
            })

    if prog_has_data and trend_direction == "Declining":
        alerts.append({
            "id": "declining_trend",
            "severity": "MEDIUM",
            "title": "Negative Performance Trajectory",
            "description": "Weekly test scores show a declining slope over recent cycles."
        })

    if wellness_has_data and wellness_score is not None:
        if daily_screen > 6.0:
            alerts.append({
                "id": "excessive_screen",
                "severity": "MEDIUM",
                "title": "Elevated Digital Screen Exposure",
                "description": f"Student logs {daily_screen:.1f} hours/day total screen time."
            })
        if wellness_score < 55.0:
            alerts.append({
                "id": "wellness_concern",
                "severity": "MEDIUM",
                "title": "Cyber-Wellbeing Concern Flagged",
                "description": f"Digital wellness index is {wellness_score:.1f}%."
            })

    # Insights ("Why this student requires attention")
    if not alerts and available_weight > 0:
        insights.append("Student is performing consistently well across all monitored academic and wellbeing dimensions.")
        insights.append(f"Learning Health Score is strong ({learning_health_dict.get('score', 0):.1f}/100) with positive habits.")
    elif not alerts and available_weight == 0:
        insights.append("Student profile is newly registered. Ongoing assessments and logs will populate intelligence insights.")
    else:
        for a in alerts:
            insights.append(f"{a['title']}: {a['description']}")

    # -----------------------------------------------------------------------
    # 9. Structured Deterministic Interventions
    # -----------------------------------------------------------------------
    interventions = []

    if academic_has_data and academic_avg is not None and academic_avg < 60.0:
        interventions.append({
            "id": "remedial_academic",
            "priority": "HIGH" if academic_avg < 50.0 else "MEDIUM",
            "title": "Schedule Remedial Concept Review",
            "description": f"Assign focused diagnostic practice for weaker topics ({academic_dict.get('weakest_subject', 'General')}).",
            "reason": f"Assessment average ({academic_avg:.1f}%) is below 60%.",
            "action_type": "academic",
            "completed": False
        })

    if prog_has_data and trend_direction == "Declining":
        interventions.append({
            "id": "progress_monitoring",
            "priority": "HIGH",
            "title": "Initiate Weekly Progress Check-ins",
            "description": "Review weekly test submissions with student to diagnose concept misunderstandings.",
            "reason": "Linear regression forecast shows declining trend.",
            "action_type": "monitoring",
            "completed": False
        })

    if att_has_data and att_rate is not None and att_rate < 85.0:
        interventions.append({
            "id": "attendance_followup",
            "priority": "HIGH" if att_rate < 75.0 else "MEDIUM",
            "title": "Conduct Attendance & Engagement Follow-up",
            "description": "Discuss attendance barriers with student and guardians to restore regular participation.",
            "reason": f"Attendance ({att_rate:.1f}%) is below 85% benchmark.",
            "action_type": "attendance",
            "completed": False
        })

    if wellness_has_data and ((daily_screen is not None and daily_screen > 6.0) or (wellness_score is not None and wellness_score < 55.0)):
        interventions.append({
            "id": "wellness_counseling",
            "priority": "MEDIUM",
            "title": "Digital Routine & Cyber-Wellbeing Guidance",
            "description": "Provide guidance on balancing recreational screen time with focused study habits.",
            "reason": f"Screen time ({daily_screen:.1f}h/day) or wellness index ({wellness_score:.1f}%) flagged.",
            "action_type": "wellness",
            "completed": False
        })

    # Default reinforcement action if all good
    if not interventions and available_weight > 0:
        interventions.append({
            "id": "enrichment_reinforcement",
            "priority": "LOW",
            "title": "Maintain Positive Learning Cadence",
            "description": "Acknowledge consistent engagement and provide advanced enrichment objectives.",
            "reason": "All learning health metrics are within optimal range.",
            "action_type": "enrichment",
            "completed": False
        })

    # -----------------------------------------------------------------------
    # 10. Unified Chronological Activity Timeline
    # -----------------------------------------------------------------------
    raw_events = []

    # Diagnostics events
    for diag in diag_rows:
        t_date = str(diag.get("test_date") or "")
        obtained = float(diag.get("score_obtained", 0))
        max_s = float(diag.get("max_score", 100) or 100)
        pct = (obtained / max_s * 100.0) if max_s > 0 else 0.0
        obj_id = diag.get("objective_id") or diag.get("log_id")
        
        raw_events.append({
            "date": t_date,
            "timestamp": f"{t_date} 10:00:00" if len(t_date) == 10 else t_date,
            "type": "assessment",
            "icon": "📊",
            "title": f"Diagnostic Assessment Recorded",
            "description": f"Objective #{obj_id} — Score: {obtained:.0f}/{max_s:.0f} ({pct:.1f}%)",
            "priority": "normal"
        })

    # Attendance events (recent 15)
    for att in att_rows[-15:]:
        a_date = str(att.get("attendance_date") or "")
        is_pres = att.get("status") in ("P", "Present")
        raw_events.append({
            "date": a_date,
            "timestamp": f"{a_date} 08:30:00" if len(a_date) == 10 else a_date,
            "type": "attendance",
            "icon": "📅",
            "title": "Attendance Recorded",
            "description": f"Status: {'Present (PMLA Registry)' if is_pres else 'Absent — Follow-up recommended'}",
            "priority": "high" if not is_pres else "normal"
        })

    # Weekly progress events
    for wp in prog_rows:
        w_date = str(wp.get("week_start") or "")
        w_score = float(wp.get("score", 0))
        raw_events.append({
            "date": w_date,
            "timestamp": f"{w_date} 16:00:00" if len(w_date) == 10 else w_date,
            "type": "weekly_progress",
            "icon": "📈",
            "title": "Weekly Progress Milestone",
            "description": f"Progress Score: {w_score:.1f}%",
            "priority": "normal"
        })

    # Cyber wellness events
    for wa in wellness_rows:
        wa_date = str(wa.get("audit_date") or "")
        wa_score = float(wa.get("wellness_score", 0))
        wa_screen = float(wa.get("daily_screen_time", 0))
        raw_events.append({
            "date": wa_date,
            "timestamp": f"{wa_date} 12:00:00" if len(wa_date) == 10 else wa_date,
            "type": "wellness",
            "icon": "🛡️",
            "title": "Cyber-Wellness Audit Logged",
            "description": f"Wellness Index: {wa_score:.1f}% | Daily Screen: {wa_screen:.1f}h",
            "priority": "high" if wa_score < 55.0 else "normal"
        })

    # Achievements events
    ach_rows = execute_select(
        "SELECT badge_name, date_awarded FROM Achievements WHERE student_id = %s",
        (student_id,)
    )
    for ach in ach_rows:
        ach_date = str(ach.get("date_awarded") or "")
        raw_events.append({
            "date": ach_date,
            "timestamp": f"{ach_date} 15:00:00" if len(ach_date) == 10 else ach_date,
            "type": "achievement",
            "icon": "🏆",
            "title": "Achievement Unlocked",
            "description": str(ach.get("badge_name", "Student Achievement")),
            "priority": "normal"
        })

    # Interventions events & history
    try:
        iv_rows = execute_select(
            "SELECT intervention_id, title, risk_factor, action_type, priority, status, assigned_date, completed_date, effectiveness_score, effectiveness_tier "
            "FROM Interventions WHERE student_id = %s ORDER BY assigned_date DESC",
            (student_id,)
        )
    except Exception:
        iv_rows = []

    for iv in iv_rows:
        iv_date = str(iv.get("assigned_date") or "")
        iv_status = iv.get("status", "PENDING")
        iv_title = iv.get("title", "Teacher Intervention")
        raw_events.append({
            "date": iv_date,
            "timestamp": f"{iv_date} 09:00:00" if len(iv_date) == 10 else iv_date,
            "type": "intervention",
            "icon": "🛠️",
            "title": f"Intervention: {iv_title}",
            "description": f"Status: {iv_status} | Priority: {iv.get('priority')} | Strategy: {iv.get('action_type')}",
            "priority": "high" if iv_status == "ESCALATED" else "normal"
        })

    # -----------------------------------------------------------------------
    # 11. Explainable Risk Intelligence Integration
    # -----------------------------------------------------------------------

    from . import risk_engine, explainability
    metrics_for_risk = {
        "student_id": student_id,
        "has_data": available_weight > 0,
        "data_completeness": data_completeness,
        "academic_average": academic_avg,
        "attendance_percentage": att_rate,
        "slope": slope,
        "trend_direction": trend_direction,
        "progress_count": len(prog_rows),
        "wellness_score": wellness_dict.get("wellness_score"),
        "daily_screen_time": wellness_dict.get("daily_screen_time"),
        "screen_time_hours": wellness_dict.get("daily_screen_time"),
        "learning_health_score": learning_health_dict.get("score")
    }
    risk_res = risk_engine.calculate_risk_score_from_metrics(metrics_for_risk)
    factors = explainability.extract_contributing_risk_factors(metrics_for_risk, risk_res["breakdown"])
    why_text = explainability.generate_why_narrative(metrics_for_risk, factors, risk_res["risk_level"])
    explainable_actions = explainability.generate_explainable_recommendations(factors, risk_res["risk_level"])


    # Sort timeline events chronologically descending (newest first)
    timeline_sorted = sorted(raw_events, key=lambda x: x["timestamp"], reverse=True)

    # -----------------------------------------------------------------------
    # 12. Complete Structured Profile Return
    # -----------------------------------------------------------------------
    return {

        "student": student_dict,
        "profile_status": {
            "has_data": available_weight > 0,
            "data_completeness": data_completeness,
            "confidence_level": confidence_level
        },
        "learning_health": learning_health_dict,
        "academic": academic_dict,
        "attendance": attendance_dict,
        "weekly_progress": weekly_dict,
        "wellness": wellness_dict,
        "prediction": prediction_dict,
        "risk_engine": {
            "risk_score": risk_res["risk_score"],
            "risk_level": risk_res["risk_level"],
            "breakdown": risk_res["breakdown"],
            "factors": factors,
            "early_warnings": risk_res["early_warnings"],
            "data_quality": risk_res["data_quality"]
        },
        "alerts": alerts,
        "insights": why_text if why_text else insights,
        "interventions": explainable_actions if explainable_actions else interventions,
        "recorded_interventions": iv_rows,
        "timeline": timeline_sorted
    }


