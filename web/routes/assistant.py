"""Flask blueprint routing AI decision support queries, recommendations, and dashboards."""

from __future__ import annotations
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import student_service, analytics, recommendation, ai_assistant
from core.database import get_db_status

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/assistant")
def view_assistant():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    students = student_service.get_all_students()
    total_students = len(students)

    stats = {
        "total_students": total_students,
        "avg_academic": 0.0,
        "avg_attendance": 0.0,
        "avg_wellness": 0.0,
    }

    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    alerts_list = []

    if total_students > 0:
        academics = []
        attendance = []
        wellness = []

        for s in students:
            sid = s["student_id"]
            summary = analytics.get_student_analytics_summary(sid)
            if not summary:
                continue
            academics.append(summary["academic_average"])
            attendance.append(summary["attendance_percentage"])
            wellness.append(summary["cyber_wellness_score"])

            rl = summary["risk_level"]
            if rl in risk_counts:
                risk_counts[rl] += 1

            student_alerts = recommendation.generate_teacher_alerts(summary)
            if student_alerts:
                alerts_list.append((summary["student_name"], student_alerts))

        stats["avg_academic"] = sum(academics) / len(academics) if academics else 0.0
        stats["avg_attendance"] = sum(attendance) / len(attendance) if attendance else 0.0
        stats["avg_wellness"] = sum(wellness) / len(wellness) if wellness else 0.0

    # Format risk distribution percentages
    risk_percentages = {}
    for k, v in risk_counts.items():
        pct = (v / total_students * 100) if total_students > 0 else 0.0
        risk_percentages[k] = {"count": v, "pct": f"{pct:.1f}"}

    return render_template(
        "assistant.html",
        active_tab="assistant",
        db_status=db_status,
        stats=stats,
        risk_counts=risk_counts,
        risk_percentages=risk_percentages,
        alerts_list=alerts_list[:3]  # Show top 3 alerts
    )


@assistant_bp.route("/assistant/query", methods=["POST"])
def assistant_query():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    query = data.get("query", "").strip()
    student_id = data.get("student_id")

    if not query:
        return jsonify({"success": False, "message": "Empty query"}), 400

    try:
        if student_id:
            response = ai_assistant.ask_ai_about_student(int(student_id), query)
        else:
            response = ai_assistant.ask_ai(query)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@assistant_bp.route("/assistant/suggestions", methods=["POST"])
def assistant_suggestions():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"success": False, "message": "Student ID required"}), 400

    try:
        response = ai_assistant.get_ai_suggestions(int(student_id))
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
