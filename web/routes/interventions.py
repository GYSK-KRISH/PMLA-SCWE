"""Flask blueprint for Teacher Intervention Tracking & Outcome Intelligence."""

from __future__ import annotations
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import intervention_service, intervention_analytics, student_service, student_profile_service
from core.database import get_db_status

interventions_bp = Blueprint("interventions", __name__)


@interventions_bp.route("/interventions")
def view_interventions():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    all_items = intervention_service.get_all_interventions()
    kpi_metrics = intervention_analytics.aggregate_cohort_intervention_metrics(all_items)
    students = student_service.get_all_students()

    active_items = [i for i in all_items if i.get("status") in ("PENDING", "IN_PROGRESS", "ESCALATED")]
    completed_items = [i for i in all_items if i.get("status") == "COMPLETED"]

    return render_template(
        "interventions.html",
        active_tab="interventions",
        db_status=db_status,
        kpi=kpi_metrics,
        active_interventions=active_items,
        completed_interventions=completed_items,
        students=students,
        action_types=intervention_service.ACTION_TYPES,
        priorities=intervention_service.PRIORITY_LEVELS
    )


@interventions_bp.route("/interventions/create", methods=["POST"])
def create_intervention_route():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    sid = data.get("student_id")
    title = data.get("title", "").strip()
    risk_f = data.get("risk_factor", "General Review").strip()
    atype = data.get("action_type", "Remedial Practice")
    prio = data.get("priority", "MEDIUM")
    t_date = data.get("target_date") or date.today().isoformat()
    notes = data.get("teacher_notes", "")

    if not sid or not title:
        return jsonify({"success": False, "message": "Student ID and title are required."}), 400

    try:
        res = intervention_service.create_intervention(
            student_id=int(sid),
            title=title,
            risk_factor=risk_f,
            action_type=atype,
            priority=prio,
            target_date=t_date,
            teacher_notes=notes
        )
        return jsonify(res)
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@interventions_bp.route("/interventions/status", methods=["POST"])
def update_status_route():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    iv_id = data.get("intervention_id")
    new_st = data.get("status")
    notes = data.get("teacher_notes")

    if not iv_id or not new_st:
        return jsonify({"success": False, "message": "Missing intervention_id or status."}), 400

    try:
        ok = intervention_service.update_intervention_status(int(iv_id), new_st, teacher_notes=notes)
        return jsonify({"success": ok})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@interventions_bp.route("/interventions/evaluate", methods=["POST"])
def evaluate_intervention_route():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    iv_id = data.get("intervention_id")
    notes = data.get("teacher_notes", "")
    overrides = data.get("overrides")  # optional dict with post metrics

    if not iv_id:
        return jsonify({"success": False, "message": "Missing intervention_id."}), 400

    try:
        res = intervention_service.evaluate_intervention_outcome(
            intervention_id=int(iv_id),
            teacher_notes=notes,
            post_metrics_override=overrides
        )
        return jsonify(res)
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
