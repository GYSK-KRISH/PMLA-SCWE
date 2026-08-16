"""Flask blueprint routing student analytics, Explainable Risk Engine, and class overview."""

from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session

from core import student_service, analytics, recommendation, risk_engine
from core.database import get_db_status

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
def student_analytics():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    student_id_raw = request.args.get("student_id", "").strip()
    class_filter = request.args.get("class_name", "All").strip()
    sec_filter = request.args.get("section", "All").strip()
    risk_filter = request.args.get("risk_filter", "All").strip()

    student_id = None
    risk_profile = None
    summary = None
    insights = []
    plan = []

    if student_id_raw:
        try:
            student_id = int(student_id_raw)
        except ValueError:
            pass

    # Fetch aggregate class risk overview
    class_overview = risk_engine.get_class_risk_overview(class_filter, sec_filter, risk_filter)

    # If no student ID was searched, select the first student from the filtered class overview or database
    if not student_id:
        if class_overview["roster"]:
            student_id = class_overview["roster"][0]["student_id"]
        else:
            students = student_service.get_all_students()
            if students:
                student_id = students[0]["student_id"]

    if student_id:
        risk_profile = risk_engine.compute_student_risk_profile(student_id)
        summary = analytics.get_student_analytics_summary(student_id)
        if risk_profile:
            insights = risk_profile.get("why_explanation", [])
            plan = risk_profile.get("recommended_actions", [])

    return render_template(
        "analytics.html",
        active_tab="analytics",
        db_status=db_status,
        student_id=student_id,
        class_overview=class_overview,
        risk_profile=risk_profile,
        summary=summary,
        insights=insights,
        plan=plan,
        selected_class=class_filter,
        selected_sec=sec_filter,
        selected_risk=risk_filter
    )
