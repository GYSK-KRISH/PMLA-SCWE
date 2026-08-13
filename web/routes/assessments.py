"""Flask blueprint routing academic grades list and updates."""

from __future__ import annotations
import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import student_service, assessment_service
from core.database import get_db_status

assessments_bp = Blueprint("assessments", __name__)


@assessments_bp.route("/assessments", methods=["GET"])
def view_assessments():
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
                history = assessment_service.get_assessment_history(sid)
        except ValueError:
            pass

    topics = [
        "Pandas Basics", "SQL SELECT", "SQL JOIN", "Data Visualization",
        "Cyber Safety", "Python Functions", "Digital Wellness",
        "Spreadsheet Skills", "AI Literacy", "Ethics in Technology"
    ]

    return render_template(
        "assessments.html",
        active_tab="assessments",
        db_status=db_status,
        student_id=student_id,
        student_info=student_info,
        history=history,
        topics=topics
    )


@assessments_bp.route("/assessments/add", methods=["POST"])
def add_grade():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if session.get("role") == "Viewer":
        return jsonify({"success": False, "message": "Access Denied: Viewers do not have write permissions."}), 403

    try:
        student_id = int(request.form.get("student_id", "").strip())
        topic = request.form.get("topic", "").strip()
        score = float(request.form.get("score", "").strip())
        max_score = float(request.form.get("max_score", "100").strip() or 100)
        date_str = request.form.get("test_date", "").strip()

        # Map topic name to an index ID
        topics = [
            "Pandas Basics", "SQL SELECT", "SQL JOIN", "Data Visualization",
            "Cyber Safety", "Python Functions", "Digital Wellness",
            "Spreadsheet Skills", "AI Literacy", "Ethics in Technology"
        ]
        objective_id = 1
        if topic in topics:
            objective_id = topics.index(topic) + 1

        if not date_str:
            date_str = datetime.date.today().isoformat()

        success = assessment_service.add_assessment_record(
            student_id, objective_id, score, max_score, date_str
        )

        if success:
            return jsonify({"success": True, "message": "Grade submitted successfully!"})
        else:
            return jsonify({"success": False, "message": "Failed to write to database."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"}), 400
