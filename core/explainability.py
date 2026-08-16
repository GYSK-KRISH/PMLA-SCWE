"""Explainability Engine for PMLA-SCWE.

Translates quantitative risk factor contributions into transparent, human-interpretable
evidence narratives and deterministic pedagogical intervention checklists.
"""

from __future__ import annotations
from typing import Any
from . import constants


def extract_contributing_risk_factors(
    metrics: dict[str, Any],
    breakdown: dict[str, float]
) -> list[dict[str, Any]]:
    """Extracts structured contributing risk factors with evidence strings and impact levels.
    
    Args:
        metrics: Normalized student metrics dictionary.
        breakdown: Point contributions calculated by the risk engine.
        
    Returns:
        List of structured factor dictionaries.
    """
    factors = []

    # 1. Academic Factor
    acad_pts = breakdown.get("academic_points", 0.0)
    acad_avg = metrics.get("academic_average")
    if acad_pts > 0 and acad_avg is not None:
        if acad_avg < constants.ACADEMIC_CRITICAL:
            impact = "high"
            sev = "critical"
            ev = f"Average diagnostic score is {acad_avg:.1f}% (below critical benchmark of {constants.ACADEMIC_CRITICAL:.0f}%)"
        elif acad_avg < constants.ACADEMIC_SATISFACTORY:
            impact = "medium"
            sev = "warning"
            ev = f"Average diagnostic score is {acad_avg:.1f}% (below satisfactory standard of {constants.ACADEMIC_SATISFACTORY:.0f}%)"
        else:
            impact = "low"
            sev = "advisory"
            ev = f"Academic performance is at {acad_avg:.1f}% (minor deficit points applied)"

        factors.append({
            "factor_key": "academic",
            "name": "Academic Performance Deficit",
            "impact": impact,
            "severity": sev,
            "points_contributed": round(acad_pts, 1),
            "max_points": constants.MAX_ACADEMIC_RISK_POINTS,
            "evidence": ev
        })

    # 2. Attendance Factor
    att_pts = breakdown.get("attendance_points", 0.0)
    att_pct = metrics.get("attendance_percentage")
    if att_pts > 0 and att_pct is not None:
        if att_pct < constants.ATTENDANCE_MINIMUM_CBSE:
            impact = "high"
            sev = "critical"
            ev = f"Attendance rate is {att_pct:.1f}% (below mandatory CBSE threshold of {constants.ATTENDANCE_MINIMUM_CBSE:.0f}%)"
        elif att_pct < constants.ATTENDANCE_SATISFACTORY:
            impact = "medium"
            sev = "warning"
            ev = f"Attendance rate is {att_pct:.1f}% (below target of {constants.ATTENDANCE_SATISFACTORY:.0f}%)"
        else:
            impact = "low"
            sev = "advisory"
            ev = f"Attendance is {att_pct:.1f}%"

        factors.append({
            "factor_key": "attendance",
            "name": "Attendance Inconsistency",
            "impact": impact,
            "severity": sev,
            "points_contributed": round(att_pts, 1),
            "max_points": constants.MAX_ATTENDANCE_RISK_POINTS,
            "evidence": ev
        })

    # 3. Performance Trend Factor
    trend_pts = breakdown.get("trend_points", 0.0)
    slope = metrics.get("slope")
    trajectory = metrics.get("trend_direction", constants.TRAJECTORY_STABLE)
    if trend_pts > 0 and trajectory == constants.TRAJECTORY_DECLINING:
        slope_str = f"{slope:.2f} pts/wk" if slope is not None else "negative"
        factors.append({
            "factor_key": "trend",
            "name": "Declining Performance Trajectory",
            "impact": "high" if trend_pts >= 10 else "medium",
            "severity": "warning",
            "points_contributed": round(trend_pts, 1),
            "max_points": constants.MAX_TREND_RISK_POINTS,
            "evidence": f"Weekly progress regression indicates a downward trajectory (slope: {slope_str})"
        })

    # 4. Cyber-Wellbeing & Screen Exposure Factor
    well_pts = breakdown.get("wellness_points", 0.0)
    screen_time = metrics.get("daily_screen_time") or metrics.get("screen_time_hours")
    wellness_score = metrics.get("wellness_score")
    if well_pts > 0:
        ev_parts = []
        if screen_time is not None and screen_time > constants.MAX_HEALTHY_DAILY_SCREEN_HOURS:
            ev_parts.append(f"Screen exposure ({screen_time:.1f}h/day) exceeds healthy threshold ({constants.MAX_HEALTHY_DAILY_SCREEN_HOURS:.0f}h)")
        if wellness_score is not None and wellness_score < constants.WELLNESS_CONCERN_THRESHOLD:
            ev_parts.append(f"Digital wellness index ({wellness_score:.1f}%) is in concern range")

        factors.append({
            "factor_key": "wellness",
            "name": "Cyber-Wellbeing / Screen Exposure Concern",
            "impact": "medium" if well_pts >= 6 else "low",
            "severity": "warning" if well_pts >= 6 else "advisory",
            "points_contributed": round(well_pts, 1),
            "max_points": constants.MAX_WELLNESS_RISK_POINTS,
            "evidence": " • ".join(ev_parts) if ev_parts else "Sub-optimal digital wellness audit indicators recorded."
        })

    # 5. Learning Health Score (LHS) Factor
    lhs_pts = breakdown.get("lhs_points", 0.0)
    lhs_val = metrics.get("learning_health_score")
    if lhs_pts > 0 and lhs_val is not None:
        if lhs_val < constants.LHS_CRITICAL:
            impact = "high"
            sev = "critical"
            ev = f"Composite Learning Health Score ({lhs_val:.1f}/100) is in critical deficit range"
        elif lhs_val < constants.LHS_MONITOR:
            impact = "medium"
            sev = "warning"
            ev = f"Composite Learning Health Score ({lhs_val:.1f}/100) requires active monitoring"
        else:
            impact = "low"
            sev = "advisory"
            ev = f"Learning Health Score is {lhs_val:.1f}/100"

        factors.append({
            "factor_key": "lhs",
            "name": "Compounding Learning Health Deficit",
            "impact": impact,
            "severity": sev,
            "points_contributed": round(lhs_pts, 1),
            "max_points": constants.MAX_LHS_RISK_POINTS,
            "evidence": ev
        })

    # Sort factors by points contributed descending
    factors.sort(key=lambda f: f["points_contributed"], reverse=True)
    return factors


def generate_why_narrative(
    metrics: dict[str, Any],
    factors: list[dict[str, Any]],
    risk_level: str
) -> list[str]:
    """Generates human-readable plain-English narrative answering 'Why does this student need attention?'
    
    Args:
        metrics: Normalized student metrics dictionary.
        factors: Contributing factors extracted by the explainability engine.
        risk_level: Overall classified risk level.
        
    Returns:
        List of bullet points.
    """
    if risk_level == constants.RISK_LEVEL_INSUFFICIENT:
        return [
            "Insufficient historical observations are currently available for this student.",
            "Record at least 2 weekly progress entries and regular attendance to generate a validated risk assessment."
        ]

    if not factors or risk_level == constants.RISK_LEVEL_LOW:
        return [
            "Student demonstrates consistent mastery and healthy learning patterns.",
            "Attendance rate is compliant with academic standards.",
            "Performance trajectory is positive or stable with balanced screen exposure."
        ]

    narrative = []
    for f in factors:
        key = f["factor_key"]
        ev = f["evidence"]
        if key == "academic":
            narrative.append(f"Academic Performance: {ev}.")
        elif key == "attendance":
            narrative.append(f"Attendance Benchmark: {ev}.")
        elif key == "trend":
            narrative.append(f"Learning Trajectory: {ev}.")
        elif key == "wellness":
            narrative.append(f"Digital Wellness: {ev}.")
        elif key == "lhs":
            narrative.append(f"Holistic Health: {ev}.")

    if len(factors) >= 3:
        narrative.append("Multiple compounding risk factors are occurring concurrently, compounding overall academic vulnerability.")

    return narrative


def generate_explainable_recommendations(
    factors: list[dict[str, Any]],
    risk_level: str
) -> list[dict[str, Any]]:
    """Generates structured, deterministic pedagogical intervention actions mapped to active risk factors.
    
    Args:
        factors: Contributing risk factors.
        risk_level: Overall classified risk level.
        
    Returns:
        List of structured intervention dictionaries.
    """
    actions = []
    factor_keys = {f["factor_key"]: f for f in factors}

    if risk_level == constants.RISK_LEVEL_INSUFFICIENT:
        return [{
            "id": "collect_baseline_data",
            "priority": "MEDIUM",
            "title": "Establish Baseline Learning Records",
            "description": "Log initial diagnostic quizzes and mark daily attendance to calibrate risk monitoring.",
            "reason": "Insufficient student data recorded",
            "action_type": "Administrative",
            "completed": False
        }]

    if "academic" in factor_keys:
        f = factor_keys["academic"]
        actions.append({
            "id": "remedial_support",
            "priority": "HIGH" if f["impact"] == "high" else "MEDIUM",
            "title": "Schedule Targeted Remedial Session",
            "description": "Provide scaffolded practice and 1-on-1 concept clarification on weak diagnostic topics.",
            "reason": f["evidence"],
            "action_type": "Academic Remediation",
            "completed": False
        })

    if "attendance" in factor_keys:
        f = factor_keys["attendance"]
        actions.append({
            "id": "attendance_counseling",
            "priority": "HIGH" if f["impact"] == "high" else "MEDIUM",
            "title": "Conduct Attendance & Engagement Follow-Up",
            "description": "Contact parent/guardian to understand absence reasons and reinforce attendance compliance.",
            "reason": f["evidence"],
            "action_type": "Counseling / Communication",
            "completed": False
        })

    if "trend" in factor_keys:
        f = factor_keys["trend"]
        actions.append({
            "id": "weekly_progress_review",
            "priority": "MEDIUM",
            "title": "Initiate Weekly Progress Checkpoints",
            "description": "Set short-term micro-learning goals and track performance on weekly quiz cycles.",
            "reason": f["evidence"],
            "action_type": "Monitoring",
            "completed": False
        })

    if "wellness" in factor_keys:
        f = factor_keys["wellness"]
        actions.append({
            "id": "digital_hygiene_guidance",
            "priority": "MEDIUM" if f["impact"] == "medium" else "LOW",
            "title": "Provide Digital Wellness & Screen Hygiene Guidance",
            "description": "Advise student and parents on balancing study screen time and establishing healthy sleep routines.",
            "reason": f["evidence"],
            "action_type": "Wellbeing Guidance",
            "completed": False
        })

    if risk_level == constants.RISK_LEVEL_HIGH and not any(a["id"] == "holistic_case_review" for a in actions):
        actions.insert(0, {
            "id": "holistic_case_review",
            "priority": "HIGH",
            "title": "Convene Multi-Disciplinary Case Review",
            "description": "Coordinate between subject teachers, class teacher, and school counselor for comprehensive support.",
            "reason": "Compounding multi-factor high risk level",
            "action_type": "Administrative Intervention",
            "completed": False
        })

    if not actions:
        actions.append({
            "id": "positive_reinforcement",
            "priority": "LOW",
            "title": "Acknowledge Consistent Performance",
            "description": "Encourage student to maintain positive study routines and explore enrichment topics.",
            "reason": "Low risk with stable learning indicators",
            "action_type": "Enrichment",
            "completed": False
        })

    return actions
