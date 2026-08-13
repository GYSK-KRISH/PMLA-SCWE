"""Flask blueprint routing student analytics, LHS summaries, and insights."""

from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session

from core import student_service, analytics, recommendation
from core.database import get_db_status

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
def student_analytics():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    student_id_raw = request.args.get("student_id", "").strip()

    student_id = None
    summary = None
    insights = []
    plan = []

    if student_id_raw:
        try:
            student_id = int(student_id_raw)
        except ValueError:
            pass

    # If no student ID was searched, load the first student in the database by default
    if not student_id:
        students = student_service.get_all_students()
        if students:
            student_id = students[0]["student_id"]

    if student_id:
        summary = analytics.get_student_analytics_summary(student_id)
        if summary:
            insights = recommendation.explain_learning_insights(summary)
            plan = recommendation.generate_intervention_plan(summary)

    return render_template(
        "analytics.html",
        active_tab="analytics",
        db_status=db_status,
        student_id=student_id,
        summary=summary,
        insights=insights,
        plan=plan
    )
