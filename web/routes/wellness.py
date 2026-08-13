"""Flask blueprint routing cyber wellness audits logging and history."""

from __future__ import annotations
import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import student_service, wellness_service
from core.database import get_db_status

wellness_bp = Blueprint("wellness", __name__)


@wellness_bp.route("/wellness", methods=["GET"])
def view_wellness():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    student_id = request.args.get("student_id", "").strip()

    student_info = None
    history = []
    
    if student_id:
        try:
            sid = int(student_id)
            res = student_service.search_students(str(sid))
            if res:
                student_info = res[0]
                history = wellness_service.get_student_audits(sid)
        except ValueError:
            pass

    return render_template(
        "wellness.html",
        active_tab="wellness",
        db_status=db_status,
        student_id=student_id,
        student_info=student_info,
        history=history
    )


@wellness_bp.route("/wellness/add", methods=["POST"])
def add_audit():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if session.get("role") == "Viewer":
        return jsonify({"success": False, "message": "Access Denied: Viewers do not have write permissions."}), 403

    try:
        student_id = int(request.form.get("student_id", "").strip())
        daily_screen = float(request.form.get("daily_screen_time", "").strip())
        study_screen = float(request.form.get("study_screen_time", "").strip())
        rec_screen = float(request.form.get("recreational_screen_time", "").strip())
        sleep = float(request.form.get("sleep_duration", "").strip())
        distraction = int(request.form.get("digital_distraction_level", "3").strip())
        safety = int(request.form.get("cyber_safety_awareness", "5").strip())
        remarks = request.form.get("remarks", "").strip()
        date_str = request.form.get("audit_date", "").strip()

        if not date_str:
            date_str = datetime.date.today().isoformat()

        payload = {
            "student_id": student_id,
            "daily_screen_time": daily_screen,
            "study_screen_time": study_screen,
            "recreational_screen_time": rec_screen,
            "sleep_duration": sleep,
            "digital_distraction_level": distraction,
            "cyber_safety_awareness": safety,
            "remarks": remarks,
            "audit_date": date_str
        }

        errors = wellness_service.validate_audit_data(payload)
        if errors:
            return jsonify({"success": False, "message": errors[0]})

        success = wellness_service.add_cyber_audit(payload)

        if success:
            return jsonify({"success": True, "message": "Cyber audit submitted successfully!"})
        else:
            return jsonify({"success": False, "message": "Failed to write to database."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"}), 400
