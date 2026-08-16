"""Flask blueprint for Smart Notification & Decision-Support Center."""

from __future__ import annotations
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from core import notification_service
from core.database import get_db_status

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications")
def view_notifications():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    # Auto-scan live analytics for grounded alerts (with deduplication)
    notification_service.scan_and_generate_smart_alerts()

    prio_filter = request.args.get("priority", "All")
    type_filter = request.args.get("alert_type", "All")
    status_filter = request.args.get("action_status", "All")

    notifs = notification_service.get_notifications(
        priority=prio_filter if prio_filter != "All" else None,
        alert_type=type_filter if type_filter != "All" else None,
        action_status=status_filter if status_filter != "All" else None
    )

    unread_cnt = notification_service.get_unread_notification_count()
    high_prio_cnt = notification_service.get_high_priority_count()
    db_status = get_db_status()

    return render_template(
        "notifications.html",
        active_tab="notifications",
        notifications=notifs,
        unread_count=unread_cnt,
        high_priority_count=high_prio_cnt,
        selected_priority=prio_filter,
        selected_type=type_filter,
        selected_status=status_filter,
        priorities=notification_service.PRIORITIES,
        alert_types=notification_service.ALERT_TYPES,
        action_statuses=notification_service.ACTION_STATUSES,
        db_status=db_status
    )


@notifications_bp.route("/notifications/mark_read", methods=["POST"])
def mark_read():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    nid = data.get("notification_id")
    if not nid:
        return jsonify({"success": False, "message": "Missing notification_id"}), 400

    ok = notification_service.mark_notification_as_read(int(nid))
    return jsonify({"success": ok})


@notifications_bp.route("/notifications/mark_all_read", methods=["POST"])
def mark_all_read():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    affected = notification_service.mark_all_notifications_as_read()
    return jsonify({"success": True, "affected": affected})


@notifications_bp.route("/notifications/status", methods=["POST"])
def update_status():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    nid = data.get("notification_id")
    new_st = data.get("action_status")

    if not nid or not new_st:
        return jsonify({"success": False, "message": "Missing parameters"}), 400

    try:
        ok = notification_service.update_notification_action_status(int(nid), new_st)
        return jsonify({"success": ok})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@notifications_bp.route("/notifications/api/unread_count", methods=["GET"])
def get_unread_count():
    if not session.get("logged_in"):
        return jsonify({"unread_cnt": 0, "high_cnt": 0})

    return jsonify({
        "unread_cnt": notification_service.get_unread_notification_count(),
        "high_cnt": notification_service.get_high_priority_count()
    })
