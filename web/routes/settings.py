"""Flask blueprint routing for account settings, notifications, and user management."""

from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from core import user_service, notification_service
from core.database import get_db_status

settings_bp = Blueprint("settings", __name__)


@settings_bp.before_request
def check_auth():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))


@settings_bp.route("/profile")
def profile():
    db_status = get_db_status()
    # Auto-generate notifications count in header
    unread_cnt = notification_service.get_unread_notification_count()
    return render_template(
        "profile.html",
        active_tab="profile",
        db_status=db_status,
        unread_cnt=unread_cnt
    )


@settings_bp.route("/password", methods=["GET", "POST"])
def change_password():
    db_status = get_db_status()
    unread_cnt = notification_service.get_unread_notification_count()
    
    if request.method == "POST":
        old_pass = request.form.get("current_password", "")
        new_pass = request.form.get("new_password", "")
        confirm_pass = request.form.get("confirm_password", "")
        
        if new_pass != confirm_pass:
            flash("New passwords do not match.", "error")
        elif len(new_pass.strip()) < 4:
            flash("Password must be at least 4 characters.", "error")
        else:
            uid = session.get("user_id")
            if user_service.change_user_password(uid, old_pass, new_pass):
                flash("Password updated successfully!", "success")
                return redirect(url_for("settings.profile"))
            else:
                flash("Incorrect current password.", "error")
                
    return render_template(
        "change_password.html",
        active_tab="profile",
        db_status=db_status,
        unread_cnt=unread_cnt
    )


@settings_bp.route("/users")
def users():
    if session.get("role") != "Admin":
        flash("Access Denied: Only administrators can manage accounts.", "error")
        return redirect(url_for("dashboard.view_dashboard"))
        
    db_status = get_db_status()
    unread_cnt = notification_service.get_unread_notification_count()
    user_list = user_service.list_users()
    
    return render_template(
        "users.html",
        active_tab="profile",
        db_status=db_status,
        unread_cnt=unread_cnt,
        users=user_list
    )


@settings_bp.route("/users/add", methods=["POST"])
def add_user():
    if session.get("role") != "Admin":
        return redirect(url_for("dashboard.view_dashboard"))
        
    username = request.form.get("username", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "Teacher")
    status = request.form.get("status", "Active")
    
    if user_service.create_user(username, full_name, password, role, status):
        flash("User account created successfully.", "success")
    else:
        flash("Failed to create user (username may already exist).", "error")
        
    return redirect(url_for("settings.users"))


@settings_bp.route("/users/edit/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    if session.get("role") != "Admin":
        return redirect(url_for("dashboard.view_dashboard"))
        
    username = request.form.get("username", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    role = request.form.get("role", "Teacher")
    status = request.form.get("status", "Active")
    
    if user_service.update_user(user_id, username, full_name, role, status):
        flash("User settings updated.", "success")
    else:
        flash("Failed to update user.", "error")
        
    return redirect(url_for("settings.users"))


@settings_bp.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "Admin":
        return redirect(url_for("dashboard.view_dashboard"))
        
    # Prevent deleting admin
    user = user_service.get_user(user_id)
    if user and user["username"] == "admin":
        flash("Cannot delete system root admin account.", "error")
    elif user_service.delete_user(user_id):
        flash("User account deleted successfully.", "success")
    else:
        flash("Failed to delete user.", "error")
        
    return redirect(url_for("settings.users"))

