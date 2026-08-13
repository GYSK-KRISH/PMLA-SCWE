"""Flask blueprint routing administrator authentication."""

from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session

from core import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.view_dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = auth_service.login_user(username, password)
            if user:
                session["logged_in"] = True
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["full_name"] = user["full_name"]
                return redirect(url_for("dashboard.view_dashboard"))
            else:
                error = "Invalid username or password."
        except Exception as e:
            error = f"Database connectivity error: {e}"

    # Inject status info
    from core.database import get_db_status
    db_status = get_db_status()

    return render_template("login.html", error=error, db_status=db_status)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
