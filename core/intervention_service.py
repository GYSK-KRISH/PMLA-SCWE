"""Centralized Database & Lifecycle Service for Teacher Interventions.

Version 1.6 — Intervention Tracking & Outcome Intelligence
Features:
- Automated baseline metric snapshot capture at creation time.
- Lifecycle transitions: PENDING -> IN_PROGRESS -> COMPLETED / ESCALATED.
- Automated outcome evaluation and delta calculation against verified student analytics.
- Cohort filtering and history lookup for Student 360 profile and reporting.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Any

from core.database import execute_query, execute_non_query, log_activity
from core.student_profile_service import get_student_360_profile
from core.risk_engine import compute_student_risk_profile
from core.intervention_analytics import calculate_intervention_effectiveness, aggregate_cohort_intervention_metrics


ACTION_TYPES = [
    "Remedial Practice",
    "Attendance Counseling",
    "Parent Consultation",
    "Screen Habit Pacing",
    "Peer Study Support",
    "Concept Revision",
]

PRIORITY_LEVELS = ["HIGH", "MEDIUM", "LOW"]
STATUS_LEVELS = ["PENDING", "IN_PROGRESS", "COMPLETED", "ESCALATED"]


def create_intervention(
    student_id: int,
    title: str,
    risk_factor: str,
    action_type: str = "Remedial Practice",
    priority: str = "MEDIUM",
    target_date: str | None = None,
    teacher_notes: str | None = None
) -> dict[str, Any]:
    """Creates a new teacher intervention and snapshots baseline pre-intervention metrics."""
    profile = get_student_360_profile(student_id)
    if not profile:
        raise ValueError(f"Student #{student_id} not found in database.")

    # Snapshot current baseline metrics
    acad_score = profile["academic"].get("average_score")
    att_rate = profile["attendance"].get("percentage")
    lhs_score = profile["learning_health"].get("score")
    risk_data = profile.get("risk_engine", {})
    risk_score = risk_data.get("risk_score")

    today_str = date.today().isoformat()
    target_str = target_date or today_str

    q = (
        "INSERT INTO Interventions ("
        "  student_id, title, risk_factor, action_type, priority, status, assigned_date, target_date, "
        "  teacher_notes, pre_academic_score, pre_attendance_rate, pre_risk_score, pre_lhs_score"
        ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    params = (
        student_id,
        title,
        risk_factor,
        action_type,
        priority,
        "PENDING",
        today_str,
        target_str,
        teacher_notes or "",
        acad_score,
        att_rate,
        risk_score,
        lhs_score
    )

    execute_non_query(q, params)
    log_activity(f"Created {priority} priority intervention for Student #{student_id}: {title}")

    # Fetch created row ID
    rows = execute_query(
        "SELECT intervention_id FROM Interventions WHERE student_id=%s ORDER BY intervention_id DESC LIMIT 1",
        (student_id,)
    )
    new_id = rows[0]["intervention_id"] if rows else None

    return {
        "success": True,
        "intervention_id": new_id,
        "student_id": student_id,
        "title": title,
        "status": "PENDING",
        "pre_metrics": {
            "academic_score": acad_score,
            "attendance_rate": att_rate,
            "risk_score": risk_score,
            "lhs_score": lhs_score
        }
    }


def get_intervention_by_id(intervention_id: int) -> dict[str, Any] | None:
    """Retrieves a single intervention by primary ID joined with student details."""
    q = (
        "SELECT i.*, s.first_name, s.last_name, s.class_section, s.email "
        "FROM Interventions i "
        "JOIN Students s ON i.student_id = s.student_id "
        "WHERE i.intervention_id = %s"
    )
    rows = execute_query(q, (intervention_id,))
    if not rows:
        return None
    r = dict(rows[0])
    r["student_name"] = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip()
    return r


def get_interventions_for_student(student_id: int) -> list[dict[str, Any]]:
    """Retrieves all past and active interventions for a specific student."""
    q = (
        "SELECT i.*, s.first_name, s.last_name, s.class_section "
        "FROM Interventions i "
        "JOIN Students s ON i.student_id = s.student_id "
        "WHERE i.student_id = %s "
        "ORDER BY i.assigned_date DESC, i.intervention_id DESC"
    )
    rows = execute_query(q, (student_id,))
    results = []
    for r in rows:
        d = dict(r)
        d["student_name"] = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
        results.append(d)
    return results


def get_all_interventions(
    status: str | None = None,
    priority: str | None = None,
    class_name: str = "All",
    section: str = "All"
) -> list[dict[str, Any]]:
    """Retrieves filtered interventions across the school or classroom."""
    clauses = []
    params = []

    if status and status != "All":
        clauses.append("i.status = %s")
        params.append(status)

    if priority and priority != "All":
        clauses.append("i.priority = %s")
        params.append(priority)

    if class_name and class_name != "All":
        clauses.append("s.class_section LIKE %s")
        params.append(f"{class_name}%")

    if section and section != "All":
        clauses.append("s.class_section LIKE %s")
        params.append(f"%{section}")

    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    q = (
        f"SELECT i.*, s.first_name, s.last_name, s.class_section "
        f"FROM Interventions i "
        f"JOIN Students s ON i.student_id = s.student_id "
        f"{where_sql} "
        f"ORDER BY CASE i.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, i.assigned_date DESC"
    )

    rows = execute_query(q, tuple(params) if params else None)
    results = []
    for r in rows:
        d = dict(r)
        d["student_name"] = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
        results.append(d)
    return results


def update_intervention_status(
    intervention_id: int,
    new_status: str,
    teacher_notes: str | None = None
) -> bool:
    """Updates the status of an active intervention."""
    if new_status not in STATUS_LEVELS:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {STATUS_LEVELS}")

    if teacher_notes:
        q = "UPDATE Interventions SET status=%s, teacher_notes=%s WHERE intervention_id=%s"
        params = (new_status, teacher_notes, intervention_id)
    else:
        q = "UPDATE Interventions SET status=%s WHERE intervention_id=%s"
        params = (new_status, intervention_id)

    affected = execute_non_query(q, params)
    log_activity(f"Updated Intervention #{intervention_id} status to {new_status}")
    return affected == 1


def evaluate_intervention_outcome(
    intervention_id: int,
    teacher_notes: str | None = None,
    post_metrics_override: dict[str, float] | None = None
) -> dict[str, Any]:
    """Evaluates an intervention's outcome, computes effectiveness score, and marks it COMPLETED."""
    iv = get_intervention_by_id(intervention_id)
    if not iv:
        raise ValueError(f"Intervention #{intervention_id} not found.")

    sid = iv["student_id"]
    profile = get_student_360_profile(sid)

    # Determine post-metrics (either override passed or fresh from database analytics)
    if post_metrics_override:
        post_acad = post_metrics_override.get("academic_score")
        post_att = post_metrics_override.get("attendance_rate")
        post_risk = post_metrics_override.get("risk_score")
        post_lhs = post_metrics_override.get("lhs_score")
    else:
        post_acad = profile["academic"].get("average_score") if profile else None
        post_att = profile["attendance"].get("percentage") if profile else None
        post_lhs = profile["learning_health"].get("score") if profile else None
        risk_data = profile.get("risk_engine", {}) if profile else {}
        post_risk = risk_data.get("risk_score")

    pre_metrics = {
        "academic_score": iv.get("pre_academic_score"),
        "attendance_rate": iv.get("pre_attendance_rate"),
        "risk_score": iv.get("pre_risk_score"),
        "lhs_score": iv.get("pre_lhs_score")
    }

    post_metrics = {
        "academic_score": post_acad,
        "attendance_rate": post_att,
        "risk_score": post_risk,
        "lhs_score": post_lhs
    }

    eval_result = calculate_intervention_effectiveness(pre_metrics, post_metrics)

    eff_score = eval_result["effectiveness_score"]
    eff_tier = eval_result["effectiveness_tier"]
    today_str = date.today().isoformat()
    combined_notes = (iv.get("teacher_notes", "") + "\n" + (teacher_notes or "")).strip()

    q = (
        "UPDATE Interventions SET "
        "  post_academic_score=%s, post_attendance_rate=%s, post_risk_score=%s, post_lhs_score=%s, "
        "  effectiveness_score=%s, effectiveness_tier=%s, completed_date=%s, status='COMPLETED', "
        "  teacher_notes=%s "
        "WHERE intervention_id=%s"
    )
    params = (
        post_acad,
        post_att,
        post_risk,
        post_lhs,
        eff_score,
        eff_tier,
        today_str,
        combined_notes,
        intervention_id
    )

    execute_non_query(q, params)
    log_activity(f"Evaluated Intervention #{intervention_id} for Student #{sid}: Outcome is {eff_tier} ({eff_score}/100)")

    return {
        "success": True,
        "intervention_id": intervention_id,
        "student_id": sid,
        "effectiveness_score": eff_score,
        "effectiveness_tier": eff_tier,
        "deltas": {
            "risk": eval_result["delta_risk"],
            "academic": eval_result["delta_academic"],
            "attendance": eval_result["delta_attendance"],
            "lhs": eval_result["delta_lhs"]
        },
        "narrative": eval_result["narrative"]
    }


def delete_intervention(intervention_id: int) -> bool:
    """Deletes an intervention record from the database."""
    affected = execute_non_query("DELETE FROM Interventions WHERE intervention_id=%s", (intervention_id,))
    return affected == 1
