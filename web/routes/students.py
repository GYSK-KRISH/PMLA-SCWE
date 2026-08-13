"""Flask blueprint routing student registrations and directories."""

from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session

from core import student_service
from core.database import get_db_status

students_bp = Blueprint("students", __name__)


@students_bp.route("/students")
def list_students():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    query = request.args.get("q", "").strip()

    if query:
        students = student_service.search_students(query)
    else:
        students = student_service.get_all_students()

    return render_template(
        "students.html",
        active_tab="students",
        db_status=db_status,
        students=students,
        search_query=query
    )
