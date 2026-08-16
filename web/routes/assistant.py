"""Flask blueprint routing AI Teacher Copilot queries, actions, and decision-support dashboards."""

from __future__ import annotations
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import student_service, analytics, recommendation, ai
from core.database import get_db_status

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/assistant")
def view_assistant():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    ai_status = ai.get_ai_status_summary()
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

            student_alerts = summary.get("risk_reasons", [])
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
        ai_status=ai_status,
        students=students,
        stats=stats,
        risk_counts=risk_counts,
        risk_percentages=risk_percentages,
        alerts_list=alerts_list[:3]
    )


@assistant_bp.route("/assistant/copilot_action", methods=["POST"])
def copilot_action():
    if not session.get("logged_in"):
        return jsonify({"success": False, "response": "Unauthorized access."}), 401

    data = request.get_json() or {}
    action = data.get("action", "general_inquiry")

    try:
        res_dict = ai.dispatch_copilot_action(action, data)
        return jsonify({
            "success": res_dict.get("success", False),
            "action": res_dict.get("action", action),
            "response": res_dict.get("response", ""),
            "provider": res_dict.get("provider"),
            "model": res_dict.get("model"),
            "fallback_used": res_dict.get("fallback_used", False),
            "is_offline_fallback": res_dict.get("is_offline_fallback", False),
            "error": res_dict.get("error")
        })
    except Exception as exc:
        return jsonify({
            "success": False,
            "action": action,
            "response": f"Server execution error: {exc}",
            "is_offline_fallback": True,
            "error": str(exc)
        }), 500


@assistant_bp.route("/assistant/query", methods=["POST"])
def assistant_query():
    """Legacy query endpoint preserved for backward compatibility."""
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    query = data.get("query", "").strip()
    student_id = data.get("student_id")

    if not query:
        return jsonify({"success": False, "message": "Empty query"}), 400

    try:
        res_dict = ai.ask_copilot(query, student_id=int(student_id) if student_id else None)
        return jsonify({
            "success": res_dict.get("success", False),
            "response": res_dict.get("response", ""),
            "provider": res_dict.get("provider"),
            "model": res_dict.get("model"),
            "fallback_used": res_dict.get("fallback_used", False),
            "is_offline_fallback": res_dict.get("is_offline_fallback", False),
            "error": res_dict.get("error")
        })
    except Exception as exc:
        return jsonify({"success": False, "response": str(exc), "error": str(exc)}), 500
