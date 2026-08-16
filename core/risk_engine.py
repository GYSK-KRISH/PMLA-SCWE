"""Explainable Learning Risk Engine for PMLA-SCWE.

Version 1.3 — Explainable Predictive Analytics
Computes transparent multi-factor risk scores (0-100), detects performance trajectories,
generates deduplicated early warnings, and aggregates classroom risk overviews.
"""

from __future__ import annotations
import math
import time
from typing import Any
from . import constants
from . import explainability

# In-memory deduplication registry for active early warning dispatches: (student_id, warning_code) -> timestamp
_ALERT_COOLDOWN_REGISTRY: dict[tuple[int, str], float] = {}
DEFAULT_ALERT_COOLDOWN_SECONDS = 3600  # 1 hour cooldown for identical warning codes


def validate_metrics_data_quality(metrics: dict[str, Any]) -> dict[str, Any]:
    """Inspects metrics for minimum observation thresholds, bounded intervals, and missing values.
    
    Args:
        metrics: Raw or normalized student metric dictionary.
        
    Returns:
        Dictionary with data quality validation results and actionable notices.
    """
    quality_notes = []
    is_valid = True

    # 1. Academic validation
    acad = metrics.get("academic_average")
    if acad is not None:
        if not isinstance(acad, (int, float)) or math.isnan(acad):
            is_valid = False
            quality_notes.append("Academic score contains non-numeric or NaN values.")
        elif acad < 0.0 or acad > 100.0:
            is_valid = False
            quality_notes.append(f"Academic score ({acad}%) is outside physical 0-100% boundary.")
    else:
        quality_notes.append("No diagnostic quiz logs recorded.")

    # 2. Attendance validation
    att = metrics.get("attendance_percentage")
    if att is not None:
        if not isinstance(att, (int, float)) or math.isnan(att):
            is_valid = False
            quality_notes.append("Attendance rate contains non-numeric or NaN values.")
        elif att < 0.0 or att > 100.0:
            is_valid = False
            quality_notes.append(f"Attendance rate ({att}%) is outside physical 0-100% boundary.")
    else:
        quality_notes.append("No attendance records logged.")

    # 3. Weekly progress & regression count
    obs_count = metrics.get("progress_count", 0)
    if obs_count < 2:
        quality_notes.append(f"Insufficient progress observations ({obs_count}/2 minimum required for linear regression).")

    # 4. Screen time & wellness validation
    screen = metrics.get("daily_screen_time") or metrics.get("screen_time_hours")
    if screen is not None:
        if screen < 0.0 or screen > 24.0:
            is_valid = False
            quality_notes.append(f"Daily screen time ({screen}h) is outside valid 0-24h range.")

    has_sufficient = bool(
        (acad is not None or att is not None) and
        metrics.get("data_completeness", 0) >= 20
    )

    return {
        "is_valid": is_valid,
        "has_sufficient_data": has_sufficient,
        "quality_notes": quality_notes
    }


def calculate_risk_score_from_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Pure, database-agnostic calculation of transparent multi-factor risk score (0-100).
    
    Formula:
      Risk Score = Academic_Deficit (0-35) + Attendance_Deficit (0-30) +
                   Trend_Deficit (0-15) + Wellness_Deficit (0-10) + LHS_Deficit (0-10)
                   
    Args:
        metrics: Dictionary containing normalized metric values.
        
    Returns:
        Structured risk breakdown and risk level classification.
    """
    quality = validate_metrics_data_quality(metrics)
    
    # Check if student has sufficient data to produce a validated risk score
    if not quality["has_sufficient_data"] or metrics.get("has_data") is False:
        return {
            "risk_score": None,
            "risk_level": constants.RISK_LEVEL_INSUFFICIENT,
            "breakdown": {
                "academic_points": 0.0,
                "attendance_points": 0.0,
                "trend_points": 0.0,
                "wellness_points": 0.0,
                "lhs_points": 0.0
            },
            "early_warnings": [],
            "data_quality": quality
        }

    # 1. Academic Risk Points (0 to 35)
    acad_avg = metrics.get("academic_average")
    acad_pts = 0.0
    if acad_avg is not None:
        # Sanitize bounded range
        acad_avg = max(0.0, min(100.0, float(acad_avg)))
        if acad_avg < constants.ACADEMIC_CRITICAL:  # < 50.0
            # Scales from 22 to 35 pts as score drops from 50 to 0
            ratio = (constants.ACADEMIC_CRITICAL - acad_avg) / constants.ACADEMIC_CRITICAL
            acad_pts = 22.0 + (13.0 * ratio)
        elif acad_avg < constants.ACADEMIC_SATISFACTORY:  # 50.0 to 59.9
            # Scales linearly from 8 to 22 pts
            ratio = (constants.ACADEMIC_SATISFACTORY - acad_avg) / (constants.ACADEMIC_SATISFACTORY - constants.ACADEMIC_CRITICAL)
            acad_pts = 8.0 + (14.0 * ratio)
        elif acad_avg < 75.0:  # 60.0 to 74.9
            # Minor advisory points (0 to 8 pts)
            ratio = (75.0 - acad_avg) / 15.0
            acad_pts = 8.0 * ratio
        else:
            acad_pts = 0.0
    acad_pts = min(constants.MAX_ACADEMIC_RISK_POINTS, max(0.0, acad_pts))

    # 2. Attendance Risk Points (0 to 30)
    att_pct = metrics.get("attendance_percentage")
    att_pts = 0.0
    if att_pct is not None:
        att_pct = max(0.0, min(100.0, float(att_pct)))
        if att_pct < constants.ATTENDANCE_MINIMUM_CBSE:  # < 75.0%
            # Scales from 18 to 30 pts as attendance drops from 75 to 0
            ratio = (constants.ATTENDANCE_MINIMUM_CBSE - att_pct) / constants.ATTENDANCE_MINIMUM_CBSE
            att_pts = 18.0 + (12.0 * ratio)
        elif att_pct < constants.ATTENDANCE_SATISFACTORY:  # 75.0 to 84.9%
            # Scales from 0 to 18 pts
            ratio = (constants.ATTENDANCE_SATISFACTORY - att_pct) / (constants.ATTENDANCE_SATISFACTORY - constants.ATTENDANCE_MINIMUM_CBSE)
            att_pts = 18.0 * ratio
        else:
            att_pts = 0.0
    att_pts = min(constants.MAX_ATTENDANCE_RISK_POINTS, max(0.0, att_pts))

    # 3. Performance Trend Risk Points (0 to 15)
    trend_pts = 0.0
    trajectory = str(metrics.get("trend_direction", constants.TRAJECTORY_STABLE)).upper()
    slope = metrics.get("slope")
    if trajectory in (constants.TRAJECTORY_DECLINING, "DECLINING"):
        if slope is not None and slope < 0:
            # Scale based on steepness of negative slope (e.g. -0.5 to -3.0 pts/wk)
            mag = min(3.0, abs(slope))
            trend_pts = 6.0 + (9.0 * (mag / 3.0))
        else:
            trend_pts = 9.0
    trend_pts = min(constants.MAX_TREND_RISK_POINTS, max(0.0, trend_pts))


    # 4. Cyber-Wellbeing & Screen Exposure (0 to 10)
    well_pts = 0.0
    screen = metrics.get("daily_screen_time") or metrics.get("screen_time_hours")
    wellness = metrics.get("wellness_score")
    if screen is not None and screen > constants.MAX_HEALTHY_DAILY_SCREEN_HOURS:
        excess = min(6.0, screen - constants.MAX_HEALTHY_DAILY_SCREEN_HOURS)
        well_pts += 4.0 + (3.0 * (excess / 6.0))
    if wellness is not None and wellness < constants.WELLNESS_CONCERN_THRESHOLD:
        defic = (constants.WELLNESS_CONCERN_THRESHOLD - max(0.0, wellness)) / constants.WELLNESS_CONCERN_THRESHOLD
        well_pts += 3.0 + (2.0 * defic)
    well_pts = min(constants.MAX_WELLNESS_RISK_POINTS, max(0.0, well_pts))

    # 5. Learning Health Score Deficit (0 to 10)
    lhs_pts = 0.0
    lhs_val = metrics.get("learning_health_score")
    if lhs_val is not None:
        lhs_val = max(0.0, min(100.0, float(lhs_val)))
        if lhs_val < constants.LHS_CRITICAL:  # < 50.0
            ratio = (constants.LHS_CRITICAL - lhs_val) / constants.LHS_CRITICAL
            lhs_pts = 6.0 + (4.0 * ratio)
        elif lhs_val < constants.LHS_MONITOR:  # 50.0 to 59.9
            ratio = (constants.LHS_MONITOR - lhs_val) / (constants.LHS_MONITOR - constants.LHS_CRITICAL)
            lhs_pts = 6.0 * ratio
    lhs_pts = min(constants.MAX_LHS_RISK_POINTS, max(0.0, lhs_pts))

    # Composite Total
    raw_total = acad_pts + att_pts + trend_pts + well_pts + lhs_pts
    final_score = int(round(min(100.0, max(0.0, raw_total))))


    # Risk Level Classification
    if final_score >= constants.RISK_SCORE_HIGH_THRESHOLD:
        risk_level = constants.RISK_LEVEL_HIGH
    elif final_score >= constants.RISK_SCORE_MEDIUM_THRESHOLD:
        risk_level = constants.RISK_LEVEL_MEDIUM
    else:
        risk_level = constants.RISK_LEVEL_LOW

    # Generate Early Warnings
    early_warnings = []
    if acad_avg is not None and acad_avg < constants.ACADEMIC_CRITICAL:
        early_warnings.append({
            "code": constants.WARN_ACADEMIC,
            "title": "Critical Academic Alert",
            "message": f"Diagnostic score is {acad_avg:.1f}% (below critical {constants.ACADEMIC_CRITICAL:.0f}% threshold).",
            "severity": "CRITICAL"
        })
    if att_pct is not None and att_pct < constants.ATTENDANCE_MINIMUM_CBSE:
        early_warnings.append({
            "code": constants.WARN_ATTENDANCE,
            "title": "CBSE Attendance Violation Warning",
            "message": f"Attendance has dropped to {att_pct:.1f}% (below CBSE minimum requirement of {constants.ATTENDANCE_MINIMUM_CBSE:.0f}%).",
            "severity": "CRITICAL"
        })
    if trajectory == constants.TRAJECTORY_DECLINING:
        early_warnings.append({
            "code": constants.WARN_DECLINE,
            "title": "Negative Performance Trajectory",
            "message": f"Weekly progress shows a steady downward slope ({slope:.2f} pts/wk).",
            "severity": "WARNING"
        })
    if (screen is not None and screen > constants.MAX_HEALTHY_DAILY_SCREEN_HOURS) or (wellness is not None and wellness < constants.WELLNESS_CONCERN_THRESHOLD):
        early_warnings.append({
            "code": constants.WARN_CONSISTENCY,
            "title": "Digital Wellbeing Imbalance",
            "message": "Screen time and digital habit audit indicate potential learning distraction.",
            "severity": "WARNING"
        })
    if risk_level == constants.RISK_LEVEL_HIGH and len(early_warnings) >= 2:
        early_warnings.insert(0, {
            "code": constants.WARN_MULTI_FACTOR,
            "title": "Multiple Compounding Risk Factors",
            "message": f"Student has crossed into HIGH risk tier (Risk Score: {final_score}/100) with concurrent academic and engagement flags.",
            "severity": "CRITICAL"
        })

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "breakdown": {
            "academic_points": round(acad_pts, 1),
            "attendance_points": round(att_pts, 1),
            "trend_points": round(trend_pts, 1),
            "wellness_points": round(well_pts, 1),
            "lhs_points": round(lhs_pts, 1)
        },
        "early_warnings": early_warnings,
        "data_quality": quality
    }


def should_dispatch_warning(student_id: int, warning_code: str, cooldown_seconds: float = DEFAULT_ALERT_COOLDOWN_SECONDS) -> bool:
    """Checks whether an early warning should be dispatched or suppressed under cooldown deduplication."""
    now = time.time()
    key = (student_id, warning_code)
    last_sent = _ALERT_COOLDOWN_REGISTRY.get(key)
    
    if last_sent is None or (now - last_sent) > cooldown_seconds:
        _ALERT_COOLDOWN_REGISTRY[key] = now
        return True
    return False


def compute_student_risk_profile(student_id: int) -> dict[str, Any] | None:
    """Computes a complete explainable risk intelligence profile for a student using centralized services.
    
    Args:
        student_id: Primary key of the student.
        
    Returns:
        Structured Explainable Risk Profile dictionary or None if student does not exist.
    """
    from .student_profile_service import get_student_360_profile
    profile = get_student_360_profile(student_id)
    if not profile:
        return None

    s = profile["student"]
    acad = profile["academic"]
    att = profile["attendance"]
    prog = profile["weekly_progress"]
    well = profile["wellness"]
    pred = profile["prediction"]
    lh = profile["learning_health"]
    st = profile["profile_status"]

    # Assemble normalized metrics for pure risk calculation
    metrics = {
        "student_id": student_id,
        "has_data": st.get("has_data", True),
        "data_completeness": st.get("data_completeness", 0),
        "academic_average": acad.get("average_score"),
        "attendance_percentage": att.get("percentage"),
        "slope": pred.get("slope"),
        "trend_direction": (pred.get("trend_direction") or prog.get("trend_direction", constants.TRAJECTORY_STABLE)),
        "progress_count": len(prog.get("scores", [])) or prog.get("total_weeks", 0),
        "wellness_score": well.get("wellness_score"),

        "daily_screen_time": well.get("daily_screen_time"),
        "screen_time_hours": well.get("daily_screen_time"),
        "learning_health_score": lh.get("score")
    }

    risk_res = calculate_risk_score_from_metrics(metrics)
    factors = explainability.extract_contributing_risk_factors(metrics, risk_res["breakdown"])
    why_text = explainability.generate_why_narrative(metrics, factors, risk_res["risk_level"])
    actions = explainability.generate_explainable_recommendations(factors, risk_res["risk_level"])

    # Filter early warnings through deduplication
    deduped_warnings = []
    for w in risk_res["early_warnings"]:
        is_fresh = should_dispatch_warning(student_id, w["code"])
        w_copy = dict(w)
        w_copy["is_new_alert"] = is_fresh
        deduped_warnings.append(w_copy)

    return {
        "student": s,
        "risk_level": risk_res["risk_level"],
        "risk_score": risk_res["risk_score"],
        "breakdown": risk_res["breakdown"],
        "factors": factors,
        "trend": pred.get("trend_direction", constants.TRAJECTORY_STABLE),
        "slope": pred.get("slope", 0.0),
        "prediction": {
            "status": "VALID" if pred.get("has_data") else "INSUFFICIENT DATA",
            "current_score": pred.get("current_score"),
            "predicted_score": pred.get("predicted_score"),
            "methodology": "Linear regression over weekly progress milestone scores (y = mx + c)",
            "confidence_text": pred.get("confidence_text", "Based on available weekly scores.")
        },
        "early_warnings": deduped_warnings,
        "why_explanation": why_text,
        "recommended_actions": actions,
        "data_quality": risk_res["data_quality"],
        "metrics_summary": {
            "academic_avg": acad.get("display", "N/A"),
            "attendance_rate": att.get("display", "N/A"),
            "wellness_score": well.get("display", "N/A"),
            "lhs_score": lh.get("display", "N/A"),
            "data_completeness": f"{st.get('data_completeness', 0)}%"
        }
    }


def get_class_risk_overview(
    class_name: str | None = None,
    section: str | None = None,
    risk_filter: str | None = None
) -> dict[str, Any]:
    """Generates an aggregate classroom risk overview with distribution counts and common risk factors.
    
    Args:
        class_name: Optional filter for class (e.g. 'XII', 'XI').
        section: Optional filter for section (e.g. 'A', 'B').
        risk_filter: Optional filter for risk tier ('HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT DATA').
        
    Returns:
        Structured class risk overview dictionary.
    """
    from .student_service import get_all_students
    students = get_all_students()

    total_high = 0
    total_medium = 0
    total_low = 0
    total_insufficient = 0
    factor_frequency: dict[str, int] = {}
    
    students_at_risk = []
    filtered_roster = []

    for s in students:
        sid = s["student_id"]
        c_sec = s.get("class_section", "")

        # Apply class / section filtering
        if class_name and class_name != "All":
            if not c_sec.startswith(class_name):
                continue
        if section and section != "All":
            if not c_sec.endswith(section):
                continue

        r_profile = compute_student_risk_profile(sid)
        if not r_profile:
            continue

        r_level = r_profile["risk_level"]
        r_score = r_profile["risk_score"]

        # Aggregate totals
        if r_level == constants.RISK_LEVEL_HIGH:
            total_high += 1
        elif r_level == constants.RISK_LEVEL_MEDIUM:
            total_medium += 1
        elif r_level == constants.RISK_LEVEL_LOW:
            total_low += 1
        else:
            total_insufficient += 1

        # Track factor frequencies
        for f in r_profile["factors"]:
            fname = f["name"]
            factor_frequency[fname] = factor_frequency.get(fname, 0) + 1

        # Check if student belongs in students_at_risk summary
        summary_item = {
            "student_id": sid,
            "name": s.get("first_name", "") + " " + s.get("last_name", ""),
            "class_section": c_sec,
            "risk_level": r_level,
            "risk_score": r_score if r_score is not None else 0,
            "primary_factor": r_profile["factors"][0]["name"] if r_profile["factors"] else "None",
            "trend": r_profile["trend"]
        }

        if r_level in [constants.RISK_LEVEL_HIGH, constants.RISK_LEVEL_MEDIUM]:
            students_at_risk.append(summary_item)

        # Apply risk filter
        if risk_filter and risk_filter != "All":
            if r_level != risk_filter:
                continue

        filtered_roster.append(summary_item)

    # Calculate most common risk factor
    most_common = "None identified"
    if factor_frequency:
        top_factor, count = max(factor_frequency.items(), key=lambda item: item[1])
        total_flagged = total_high + total_medium
        pct = int(round((count / total_flagged) * 100)) if total_flagged > 0 else 0
        most_common = f"{top_factor} ({pct}% of flagged students)"

    # Sort students at risk by risk score descending
    students_at_risk.sort(key=lambda x: x["risk_score"], reverse=True)
    filtered_roster.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "total_students": len(students),
        "filtered_count": len(filtered_roster),
        "total_high": total_high,
        "total_medium": total_medium,
        "total_low": total_low,
        "total_insufficient": total_insufficient,
        "most_common_risk_factor": most_common,
        "students_at_risk": students_at_risk[:15],  # top 15 high/medium
        "roster": filtered_roster,
        "factor_breakdown": factor_frequency
    }
