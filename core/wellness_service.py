"""Wellness service implementing screen-time validation and cyber-wellbeing index formulas."""

from __future__ import annotations
from typing import Any
from .database import execute_query, execute_non_query


def calculate_wellness_score(audit_data: dict[str, Any]) -> float:
    """Calculates a student's wellness index score (0-100)."""
    # 1. Sleep score
    try:
        sleep = float(audit_data.get("sleep_duration", 8.0))
    except (ValueError, TypeError):
        sleep = 8.0

    if 7.0 <= sleep <= 9.0:
        sleep_score = 100.0
    elif sleep < 7.0:
        sleep_score = max(0.0, 100.0 - (7.0 - sleep) * 15.0)
    else:
        sleep_score = max(0.0, 100.0 - (sleep - 9.0) * 15.0)

    # 2. Recreational screen time score
    try:
        rec_screen = float(audit_data.get("recreational_screen_time", 2.0))
    except (ValueError, TypeError):
        rec_screen = 2.0

    if rec_screen <= 2.0:
        rec_screen_score = 100.0
    else:
        rec_screen_score = max(0.0, 100.0 - (rec_screen - 2.0) * 15.0)

    # 3. Digital distraction level (1-5)
    try:
        distraction = int(audit_data.get("digital_distraction_level", 1))
    except (ValueError, TypeError):
        distraction = 1
    
    distraction_score = max(0.0, min(100.0, (5 - distraction) * 25.0))

    # 4. Cyber safety awareness (1-5)
    try:
        safety = int(audit_data.get("cyber_safety_awareness", 5))
    except (ValueError, TypeError):
        safety = 5

    safety_score = max(0.0, min(100.0, safety * 20.0))

    # Weighted calculation
    wellness_score = (sleep_score * 0.25) + (rec_screen_score * 0.25) + (distraction_score * 0.25) + (safety_score * 0.25)
    return float(round(wellness_score, 2))


def validate_audit_data(audit_data: dict[str, Any]) -> list[str]:
    """Validates student cyber wellness audit inputs."""
    errors = []

    # 1. Student existence check
    if "student_id" not in audit_data:
        errors.append("Student ID is required.")
    else:
        try:
            student_id = int(audit_data["student_id"])
            res = execute_query("SELECT COUNT(*) AS cnt FROM Students WHERE student_id = %s", (student_id,))
            if not res or res[0].get("cnt", 0) == 0:
                errors.append(f"Student ID {student_id} does not exist.")
        except (ValueError, TypeError):
            errors.append("Student ID must be an integer.")

    # 2. Screen times validation
    screen_fields = ["daily_screen_time", "study_screen_time", "recreational_screen_time"]
    for field in screen_fields:
        if field not in audit_data or audit_data[field] is None:
            errors.append(f"{field.replace('_', ' ').capitalize()} is required.")
        else:
            try:
                val = float(audit_data[field])
                if val < 0.0 or val > 24.0:
                    errors.append(f"{field.replace('_', ' ').capitalize()} must be between 0 and 24 hours.")
            except (ValueError, TypeError):
                errors.append(f"{field.replace('_', ' ').capitalize()} must be a number.")

    # Check sum consistency: daily = study + recreational
    if all(field in audit_data and audit_data[field] is not None for field in screen_fields):
        try:
            daily = float(audit_data["daily_screen_time"])
            study = float(audit_data["study_screen_time"])
            rec = float(audit_data["recreational_screen_time"])
            if abs(daily - (study + rec)) > 0.01:
                errors.append("Daily screen time must equal the sum of study and recreational screen time.")
        except (ValueError, TypeError):
            pass

    # 3. Sleep duration validation
    if "sleep_duration" not in audit_data or audit_data["sleep_duration"] is None:
        errors.append("Sleep duration is required.")
    else:
        try:
            val = float(audit_data["sleep_duration"])
            if val < 0.0 or val > 24.0:
                errors.append("Sleep duration must be between 0 and 24 hours.")
        except (ValueError, TypeError):
            errors.append("Sleep duration must be a number.")

    # 4. Digital distraction level (1-5)
    if "digital_distraction_level" not in audit_data or audit_data["digital_distraction_level"] is None:
        errors.append("Digital distraction level is required.")
    else:
        try:
            val = int(audit_data["digital_distraction_level"])
            if val < 1 or val > 5:
                errors.append("Digital distraction level must be between 1 and 5.")
        except (ValueError, TypeError):
            errors.append("Digital distraction level must be an integer.")

    # 5. Cyber safety awareness (1-5)
    if "cyber_safety_awareness" not in audit_data or audit_data["cyber_safety_awareness"] is None:
        errors.append("Cyber safety awareness is required.")
    else:
        try:
            val = int(audit_data["cyber_safety_awareness"])
            if val < 1 or val > 5:
                errors.append("Cyber safety awareness must be between 1 and 5.")
        except (ValueError, TypeError):
            errors.append("Cyber safety awareness must be an integer.")

    return errors


def add_cyber_audit(audit_data: dict[str, Any]) -> bool:
    """Validates, calculates wellness score, and inserts audit record into database."""
    errors = validate_audit_data(audit_data)
    if errors:
        return False

    wellness_score = calculate_wellness_score(audit_data)

    query = """
        INSERT INTO Cyber_Audit (
            student_id, password_strength, screen_time_hours, daily_screen_time,
            study_screen_time, recreational_screen_time, sleep_duration,
            digital_distraction_level, cyber_safety_awareness, netiquette_score,
            privacy_awareness, e_waste_awareness, wellness_score, audit_date, remarks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # screen_time_hours is equivalent to daily_screen_time
    daily = float(audit_data["daily_screen_time"])
    
    params = (
        audit_data["student_id"],
        audit_data.get("password_strength", 0),
        daily,
        daily,
        float(audit_data["study_screen_time"]),
        float(audit_data["recreational_screen_time"]),
        float(audit_data["sleep_duration"]),
        int(audit_data["digital_distraction_level"]),
        int(audit_data["cyber_safety_awareness"]),
        audit_data.get("netiquette_score", 0),
        audit_data.get("privacy_awareness", 0),
        audit_data.get("e_waste_awareness", 0),
        wellness_score,
        audit_data.get("audit_date"),
        audit_data.get("remarks"),
    )

    return execute_non_query(query, params) == 1


def get_student_audits(student_id: int) -> list[dict[str, Any]]:
    """Retrieve full historical wellness audits for a student."""
    query = """
        SELECT audit_id, student_id, password_strength, screen_time_hours, daily_screen_time,
               study_screen_time, recreational_screen_time, sleep_duration, digital_distraction_level,
               cyber_safety_awareness, netiquette_score, privacy_awareness, e_waste_awareness,
               wellness_score, audit_date, remarks
        FROM Cyber_Audit WHERE student_id = %s ORDER BY audit_date DESC
    """
    return execute_query(query, (student_id,))


def get_latest_audit(student_id: int) -> dict[str, Any] | None:
    """Retrieve only the most recent wellness audit record for a student."""
    rows = get_student_audits(student_id)
    return rows[0] if rows else None


def get_student_wellness_score(student_id: int) -> float | None:
    """Retrieve the most recent calculated wellness score for a student."""
    audit = get_latest_audit(student_id)
    return float(audit["wellness_score"]) if audit and audit.get("wellness_score") is not None else None

