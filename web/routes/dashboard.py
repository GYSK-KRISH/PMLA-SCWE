"""Flask blueprint routing school stats overview, risk lists, and alerts for command center."""

from __future__ import annotations
import datetime
from flask import Blueprint, render_template, redirect, url_for, session

from core import student_service, analytics, recommendation
from core.database import get_db_status, execute_select

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def view_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()

    # Load metrics from core dashboard service
    from core.dashboard_service import get_dashboard_summary
    data = get_dashboard_summary()

    # Class Performance Trend query (remains here for web Chart.js compilation)
    trend_labels = []
    trend_data = []
    try:
        trend_rows = execute_select(
            "SELECT week_start, AVG(score) as avg_score FROM Weekly_Progress GROUP BY week_start ORDER BY week_start ASC"
        )
        for r in trend_rows:
            trend_labels.append(str(r["week_start"]))
            trend_data.append(round(float(r["avg_score"]), 1))
    except Exception:
        pass

    return render_template(
        "dashboard.html",
        active_tab="dashboard",
        db_status=db_status,
        stats=data["stats"],
        needs_attention=data["needs_attention"],
        support_list=data["support_list"],
        today_attendance=data["today_attendance"],
        ai_insight=data["ai_insight"],
        activity_rows=data["activity_timeline"],
        trend_labels=trend_labels,
        trend_data=trend_data
    )
