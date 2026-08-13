"""Flask blueprint routing attendance registers and bulk saves."""

from __future__ import annotations
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

from core import attendance_service
from core.database import get_db_status

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/attendance", methods=["GET"])
def mark_attendance_page():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()

    # Default parameters
    classes = ["XII-A", "XII-B", "XI-A", "XI-B", "X-A", "X-B"]
    selected_class = request.args.get("class_section", "XII-A").strip()
    selected_date = request.args.get("date", datetime.date.today().isoformat()).strip()

    # Validate class section
    if selected_class not in classes:
        selected_class = "XII-A"

    # Validate date
    try:
        datetime.datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        selected_date = datetime.date.today().isoformat()

    # Load students and existing attendance records
    students = attendance_service.get_students_by_class(selected_class)
    existing_attendance = attendance_service.get_attendance_for_date_and_class(selected_date, selected_class)

    return render_template(
        "attendance.html",
        active_tab="attendance",
        db_status=db_status,
        classes=classes,
        selected_class=selected_class,
        selected_date=selected_date,
        students=students,
        existing_attendance=existing_attendance
    )


@attendance_bp.route("/api/attendance/save", methods=["POST"])
def save_attendance_api():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized administrative session."}), 401

    if session.get("role") == "Viewer":
        return jsonify({"success": False, "message": "Access Denied: Viewers do not have write permissions."}), 403

    selected_class = request.form.get("class_section", "").strip()
    date_str = request.form.get("date", "").strip()

    if not selected_class or not date_str:
        return jsonify({"success": False, "message": "Missing class section or date parameter."}), 400

    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format YYYY-MM-DD."}), 400

    # Retrieve all students of this class
    students = attendance_service.get_students_by_class(selected_class)
    if not students:
        return jsonify({"success": False, "message": "No students found in cohort."}), 400

    # Extract attendance radio states from request form
    attendance_records = {}
    for s in students:
        sid = s["student_id"]
        # Form field name is status_<student_id>
        status_val = request.form.get(f"status_{sid}", "Present").strip()
        attendance_records[sid] = status_val

    try:
        ok = attendance_service.save_attendance(date_str, selected_class, attendance_records)
        if ok:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Failed to write attendance records to DB."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Database failure: {e}"}), 500
