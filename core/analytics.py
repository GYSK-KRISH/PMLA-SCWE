"""Analytics engine calculating academic status, regression forecasts, and Learning Health Scores."""

from __future__ import annotations
from typing import Any
from .database import execute_select


def calculate_learning_health_score(academic_score: float, weekly_progress: float, attendance_score: float, digital_wellness: float) -> float:
    """Calculates a weighted learning health score based on user specifications."""
    return (academic_score * 0.40) + (weekly_progress * 0.25) + (attendance_score * 0.20) + (digital_wellness * 0.15)


def calculate_topic_difficulty(average_score: float) -> float:
    return max(0.0, 100.0 - average_score)


def rank_students(student_rows: list[dict]) -> list[dict]:
    return sorted(student_rows, key=lambda item: item.get("average_score", 0), reverse=True)


def calculate_diagnostic_average(student_id: int) -> float:
    """Calculates the average diagnostic quiz score percentage for a student."""
    rows = execute_select(
        "SELECT AVG(score_obtained) AS avg_score, AVG(max_score) AS avg_max FROM Diagnostic_Logs WHERE student_id = %s",
        (student_id,)
    )
    avg_score = rows[0].get("avg_score") if rows else None
    avg_max = rows[0].get("avg_max") if rows else None
    if avg_score is not None and avg_max is not None and avg_max > 0:
        return (float(avg_score) / float(avg_max)) * 100.0
    return 0.0


def calculate_weekly_progress_average(student_id: int) -> float:
    """Calculates the average weekly progress score for a student."""
    rows = execute_select(
        "SELECT AVG(score) AS avg_progress FROM Weekly_Progress WHERE student_id = %s",
        (student_id,)
    )
    if rows and rows[0].get("avg_progress") is not None:
        return float(rows[0]["avg_progress"])
    return 0.0


def get_latest_cyber_wellness_score(student_id: int) -> float:
    """Retrieves the latest wellness score for a student."""
    rows = execute_select(
        "SELECT wellness_score FROM Cyber_Audit WHERE student_id = %s ORDER BY audit_date DESC LIMIT 1",
        (student_id,)
    )
    if rows and rows[0].get("wellness_score") is not None:
        return float(rows[0]["wellness_score"])
    return 70.0  # default baseline


def classify_academic_status(academic_average: float) -> str:
    """Classifies basic academic performance status."""
    if academic_average >= 85.0:
        return "Excellent"
    elif academic_average >= 60.0:
        return "Satisfactory"
    else:
        return "Needs Improvement"


def predict_next_score(student_id: int) -> dict[str, Any]:
    """Fits simple linear regression on a student's historical weekly progress."""
    rows = execute_select(
        "SELECT score FROM Weekly_Progress WHERE student_id = %s ORDER BY week_start ASC",
        (student_id,)
    )
    scores = [float(r["score"]) for r in rows if r.get("score") is not None]
    
    n = len(scores)
    if n == 0:
        return {
            "current_score": 0.0,
            "predicted_score": 0.0,
            "slope": 0.0,
            "trend_direction": "Stable"
        }
    if n == 1:
        return {
            "current_score": scores[0],
            "predicted_score": scores[0],
            "slope": 0.0,
            "trend_direction": "Stable"
        }
        
    # Fit regression line y = mx + c where x is the week index (1 to n)
    weeks = list(range(1, n + 1))
    sum_x = sum(weeks)
    sum_y = sum(scores)
    sum_xx = sum(x * x for x in weeks)
    sum_xy = sum(x * y for x, y in zip(weeks, scores))
    
    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        avg = sum_y / n
        return {
            "current_score": scores[-1],
            "predicted_score": avg,
            "slope": 0.0,
            "trend_direction": "Stable"
        }
        
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    
    predicted = slope * (n + 1) + intercept
    predicted = max(0.0, min(100.0, predicted))
    
    if slope > 0.1:
        trend = "Improving"
    elif slope < -0.1:
        trend = "Declining"
    else:
        trend = "Stable"
        
    return {
        "current_score": scores[-1],
        "predicted_score": predicted,
        "slope": slope,
        "trend_direction": trend
    }


def get_student_analytics_summary(student_id: int) -> dict[str, Any] | None:
    """Collects all diagnostic, weekly, attendance, and wellness scores for a student,
    computes learning health score, and classifies risk.
    """
    # 1. Fetch student details
    student_rows = execute_select(
        "SELECT first_name, last_name, class_section FROM Students WHERE student_id = %s",
        (student_id,)
    )
    if not student_rows:
        return None
    student_info = student_rows[0]
    
    # 2. Fetch academic performance (diagnostic logs)
    academic_average = calculate_diagnostic_average(student_id)
        
    # 3. Fetch attendance
    from .attendance_service import calculate_attendance_percentage
    attendance_percentage = calculate_attendance_percentage(student_id)
        
    # 4. Fetch cyber-wellness audit
    wellness_score = get_latest_cyber_wellness_score(student_id)
    audit_rows = execute_select(
        "SELECT screen_time_hours FROM Cyber_Audit WHERE student_id = %s ORDER BY audit_date DESC LIMIT 1",
        (student_id,)
    )
    screen_time_hours = float(audit_rows[0]["screen_time_hours"]) if audit_rows and audit_rows[0].get("screen_time_hours") is not None else 2.0
        
    # 5. Run prediction model
    pred = predict_next_score(student_id)
    
    # 6. Calculate Learning Health Score
    health_score = calculate_learning_health_score(
        academic_average,
        pred["current_score"] if pred["current_score"] > 0 else academic_average,
        attendance_percentage,
        wellness_score
    )
    
    # 7. Formulate Statuses
    academic_status = classify_academic_status(academic_average)
        
    if attendance_percentage >= 85.0:
        attendance_status = "Satisfactory"
    elif attendance_percentage < 75.0:
        attendance_status = "Critical"
    else:
        attendance_status = "Monitoring Required"
        
    if wellness_score >= 80.0 and screen_time_hours <= 3.0:
        wellness_status = "Good"
    elif wellness_score < 55.0 or screen_time_hours > 6.0:
        wellness_status = "Concern"
    else:
        wellness_status = "Satisfactory"
        
    # 8. Explainable Risk Engine Integration
    from . import risk_engine, explainability
    metrics_payload = {
        "academic_average": academic_average,
        "attendance_percentage": attendance_percentage,
        "slope": pred.get("slope", 0.0),
        "trend_direction": pred.get("trend_direction", "Stable"),
        "progress_count": 2 if pred.get("current_score", 0) > 0 else 0,
        "wellness_score": wellness_score,
        "daily_screen_time": screen_time_hours,
        "screen_time_hours": screen_time_hours,
        "learning_health_score": health_score,
        "has_data": True,
        "data_completeness": 100
    }
    risk_res = risk_engine.calculate_risk_score_from_metrics(metrics_payload)
    risk_score = risk_res["risk_score"]
    risk_level = risk_res["risk_level"]
    factors = explainability.extract_contributing_risk_factors(metrics_payload, risk_res["breakdown"])
    why_text = explainability.generate_why_narrative(metrics_payload, factors, risk_level)
    
    summary_dict = {
        "student_id": student_id,
        "first_name": student_info["first_name"],
        "last_name": student_info["last_name"],
        "class_section": student_info["class_section"],
        "academic_average": academic_average,
        "academic_status": academic_status,
        "attendance_percentage": attendance_percentage,
        "attendance_status": attendance_status,
        "wellness_score": wellness_score,
        "screen_time_hours": screen_time_hours,
        "wellness_status": wellness_status,
        "predicted_score": pred["predicted_score"],
        "trend_direction": pred["trend_direction"],
        "health_score": health_score,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "factors": factors,
        "why_explanation": why_text,
        "breakdown": risk_res["breakdown"]
    }
    
    from . import recommendation
    alerts = recommendation.generate_teacher_alerts(summary_dict)
    
    summary_dict["student_name"] = f"{student_info['first_name']} {student_info['last_name']}"
    summary_dict["weekly_progress"] = float(pred["current_score"])
    summary_dict["cyber_wellness_score"] = float(wellness_score)
    summary_dict["learning_health_score"] = float(health_score)
    summary_dict["current_score"] = float(pred["current_score"])
    summary_dict["predicted_next_score"] = float(pred["predicted_score"])
    summary_dict["trend"] = pred["trend_direction"]
    summary_dict["risk_reasons"] = alerts
    summary_dict["basic_status"] = academic_status
    
    return summary_dict


def get_class_risk_overview(
    class_name: str | None = None,
    section: str | None = None,
    risk_filter: str | None = None
) -> dict[str, Any]:
    """Exposes classroom-level aggregate risk overview from the risk engine."""
    from . import risk_engine
    return risk_engine.get_class_risk_overview(class_name, section, risk_filter)

