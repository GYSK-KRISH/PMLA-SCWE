"""Recommendation module generating explainable teaching alerts and personalized intervention checksheets."""

from __future__ import annotations
from typing import Any
from . import constants


def explain_learning_insights(student_summary: dict[str, Any]) -> list[str]:
    """Generates explainable learning insights based on student summary metrics."""
    insights = []
    
    # Academic insights
    acad_status = student_summary.get("academic_status", "Satisfactory")
    trend = student_summary.get("trend_direction", "Stable")
    
    if acad_status == "Excellent":
        insights.append("Academic performance is excellent, demonstrating mastery of the material.")
    elif acad_status == "Satisfactory":
        if trend == constants.TRAJECTORY_IMPROVING:
            insights.append("Academic performance is satisfactory and showing a positive upward trend.")
        elif trend == constants.TRAJECTORY_DECLINING:
            insights.append("Academic performance is satisfactory, but recent weekly scores indicate a decline.")
        else:
            insights.append("Academic performance is satisfactory and stable.")
    else:
        if trend == constants.TRAJECTORY_DECLINING:
            insights.append("Academic performance needs improvement, and recent weekly scores show a decline.")
        else:
            insights.append("Academic performance is below target. Regular revision is recommended.")
            
    # Attendance insights
    att_pct = student_summary.get("attendance_percentage", 100.0)
    att_status = student_summary.get("attendance_status", "Satisfactory")
    
    if att_status == "Satisfactory":
        insights.append(f"Attendance is satisfactory ({att_pct:.1f}%), supporting regular engagement.")
    elif att_status == "Critical":
        insights.append(f"Attendance is critical ({att_pct:.1f}%). Missing classes is affecting learning consistency.")
    else:
        insights.append(f"Attendance is at {att_pct:.1f}% and requires monitoring.")
        
    # Digital wellness insights
    screen_time = student_summary.get("screen_time_hours", 2.0)
    wellness_status = student_summary.get("wellness_status", "Satisfactory")
    
    if wellness_status == "Good":
        insights.append("Digital wellness is good with healthy and balanced screen exposure.")
    elif wellness_status == "Concern":
        insights.append(f"Recent audit shows a wellness concern with high screen exposure ({screen_time:.1f} hours/day).")
    else:
        insights.append(f"Digital wellness is satisfactory with moderate screen time ({screen_time:.1f} hours/day).")
        
    return insights


def generate_teacher_alerts(student_summary: dict[str, Any]) -> list[str]:
    """Generates active alerts for teachers when student metrics are sub-optimal."""
    alerts = []
    
    acad_avg = student_summary.get("academic_average", 0.0)
    att_pct = student_summary.get("attendance_percentage", 100.0)
    trend = student_summary.get("trend_direction", "Stable")
    screen_time = student_summary.get("screen_time_hours", 0.0)
    wellness = student_summary.get("wellness_score", 100.0)
    
    if acad_avg < constants.ACADEMIC_SATISFACTORY:
        alerts.append("Low academic performance")
    if att_pct < constants.ATTENDANCE_MINIMUM_CBSE:
        alerts.append("Critical attendance")
    elif att_pct < constants.ATTENDANCE_SATISFACTORY:
        alerts.append("Attendance below threshold")
    if trend == constants.TRAJECTORY_DECLINING:
        alerts.append("Declining weekly trend")
    if screen_time > constants.MAX_HEALTHY_DAILY_SCREEN_HOURS:
        alerts.append("Excessive screen exposure")
    if wellness < constants.WELLNESS_CONCERN_THRESHOLD:
        alerts.append("Wellness concern")
        
    return alerts


def generate_intervention_plan(student_summary: dict[str, Any]) -> list[str]:
    """Generates a personalized intervention checklist based on flagged concerns."""
    plan = []
    
    acad_avg = student_summary.get("academic_average", 0.0)
    att_pct = student_summary.get("attendance_percentage", 100.0)
    trend = student_summary.get("trend_direction", "Stable")
    screen_time = student_summary.get("screen_time_hours", 0.0)
    wellness = student_summary.get("wellness_score", 100.0)
    risk = student_summary.get("risk_level", "LOW")
    
    if acad_avg < constants.ACADEMIC_SATISFACTORY:
        plan.append("Schedule remedial practice sessions.")
    if trend == constants.TRAJECTORY_DECLINING:
        plan.append("Initiate weekly progress monitoring.")
    if att_pct < constants.ATTENDANCE_SATISFACTORY:
        plan.append("Conduct teacher/parent follow-up regarding attendance.")
    if screen_time > constants.MAX_HEALTHY_DAILY_SCREEN_HOURS or wellness < constants.WELLNESS_CONCERN_THRESHOLD:
        plan.append("Provide digital-wellness guidance to reduce screen exposure.")
    if risk == constants.RISK_LEVEL_HIGH:
        plan.append("Convene comprehensive student case review meeting.")
        
    if not plan:
        plan.append("Continue regular weekly revision and self-monitoring.")
        
    return plan
