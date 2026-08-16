"""Smart Notification and Decision-Support Center Service for PMLA-SCWE.

Version 1.6 — Smart Notification and Intervention Center
Features:
- Priority classifications: HIGH, MEDIUM, INFO, SUCCESS / IMPROVEMENT.
- Intelligent deduplication engine with severity escalation and time-window cooldowns.
- Structured teacher decision-support workflow (Alert -> Profile -> Intervention -> Track -> Resolve).
- Positive milestone notifications for verified student improvements.
- Filtered retrieval, unread counters, and batch status operations.
"""

from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Any

from core.database import execute_query, execute_non_query, get_db_status, log_activity


# Priority Constants
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_INFO = "INFO"
PRIORITY_SUCCESS = "SUCCESS"
PRIORITIES = [PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_INFO, PRIORITY_SUCCESS]

# Alert Type Constants
ALERT_ATTENDANCE = "ATTENDANCE"
ALERT_ACADEMIC_DECLINE = "ACADEMIC_DECLINE"
ALERT_RISK_ESCALATION = "RISK_ESCALATION"
ALERT_MILESTONE_IMPROVEMENT = "MILESTONE_IMPROVEMENT"
ALERT_WELLBEING = "WELLBEING_ALERT"
ALERT_INTERVENTION_DUE = "INTERVENTION_DUE"
ALERT_SYSTEM = "SYSTEM"
ALERT_TYPES = [
    ALERT_ATTENDANCE, ALERT_ACADEMIC_DECLINE, ALERT_RISK_ESCALATION,
    ALERT_MILESTONE_IMPROVEMENT, ALERT_WELLBEING, ALERT_INTERVENTION_DUE, ALERT_SYSTEM
]

# Action Status Constants
STATUS_OPEN = "OPEN"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_RESOLVED = "RESOLVED"
STATUS_DISMISSED = "DISMISSED"
ACTION_STATUSES = [STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_RESOLVED, STATUS_DISMISSED]


def create_notification(
    title: str,
    message: str,
    priority: str = PRIORITY_INFO,
    alert_type: str = ALERT_SYSTEM,
    student_id: int | None = None,
    source: str = "Analytics Engine",
    dedup_key: str | None = None,
    action_status: str = STATUS_OPEN,
    cooldown_days: int = 7
) -> dict[str, Any]:
    """Creates a notification with intelligent deduplication and severity escalation support."""
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Deduplication Check
    if dedup_key:
        cutoff = (now_dt - timedelta(days=cooldown_days)).strftime("%Y-%m-%d %H:%M:%S")
        existing = execute_query(
            "SELECT notification_id, priority, is_read, action_status, created_at "
            "FROM Notifications WHERE dedup_key = %s AND created_at >= %s "
            "ORDER BY notification_id DESC LIMIT 1",
            (dedup_key, cutoff)
        )
        if existing:
            prev = existing[0]
            prev_prio = prev.get("priority", PRIORITY_INFO)

            # Severity Escalation check (e.g. MEDIUM -> HIGH)
            if prev_prio != PRIORITY_HIGH and priority == PRIORITY_HIGH:
                execute_non_query(
                    "UPDATE Notifications SET priority = %s, title = %s, message = %s, is_read = 0, "
                    "action_status = %s, created_at = %s WHERE notification_id = %s",
                    (priority, title, message, STATUS_OPEN, now_str, prev["notification_id"])
                )
                return {
                    "success": True,
                    "notification_id": prev["notification_id"],
                    "action": "escalated",
                    "priority": priority
                }

            # Cooldown active and no escalation -> skip duplicate creation
            return {
                "success": True,
                "notification_id": prev["notification_id"],
                "action": "skipped_duplicate",
                "priority": prev_prio
            }

    q = (
        "INSERT INTO Notifications ("
        "  student_id, alert_type, priority, title, message, is_read, source, dedup_key, action_status, created_at"
        ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    params = (
        student_id,
        alert_type,
        priority,
        title,
        message,
        0,
        source,
        dedup_key,
        action_status,
        now_str
    )
    execute_non_query(q, params)

    rows = execute_query(
        "SELECT notification_id FROM Notifications WHERE title=%s ORDER BY notification_id DESC LIMIT 1",
        (title,)
    )
    new_id = rows[0]["notification_id"] if rows else None

    return {
        "success": True,
        "notification_id": new_id,
        "action": "created",
        "priority": priority
    }


def get_notifications(
    priority: str | None = None,
    alert_type: str | None = None,
    action_status: str | None = None,
    student_id: int | None = None,
    is_read: int | None = None,
    limit: int = 100
) -> list[dict[str, Any]]:
    """Retrieves notifications with optional multi-criteria filters."""
    clauses = []
    params = []

    if priority and priority != "All":
        clauses.append("n.priority = %s")
        params.append(priority)

    if alert_type and alert_type != "All":
        clauses.append("n.alert_type = %s")
        params.append(alert_type)

    if action_status and action_status != "All":
        clauses.append("n.action_status = %s")
        params.append(action_status)

    if student_id is not None:
        clauses.append("n.student_id = %s")
        params.append(student_id)

    if is_read is not None:
        clauses.append("n.is_read = %s")
        params.append(is_read)

    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    q = (
        f"SELECT n.*, s.first_name, s.last_name, s.class_section "
        f"FROM Notifications n "
        f"LEFT JOIN Students s ON n.student_id = s.student_id "
        f"{where_sql} "
        f"ORDER BY n.is_read ASC, "
        f"CASE n.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'SUCCESS' THEN 3 ELSE 4 END, "
        f"n.created_at DESC "
        f"LIMIT {limit}"
    )

    rows = execute_query(q, tuple(params) if params else None)
    results = []
    for r in rows:
        d = dict(r)
        fn = d.get("first_name") or ""
        ln = d.get("last_name") or ""
        d["student_name"] = f"{fn} {ln}".strip() if (fn or ln) else None
        results.append(d)
    return results


def get_unread_notification_count() -> int:
    """Returns count of active unread notifications."""
    rows = execute_query("SELECT COUNT(*) as cnt FROM Notifications WHERE is_read = 0")
    return int(rows[0].get("cnt", 0)) if rows else 0


def get_high_priority_count() -> int:
    """Returns count of unread HIGH priority alerts requiring immediate teacher attention."""
    rows = execute_query("SELECT COUNT(*) as cnt FROM Notifications WHERE is_read = 0 AND priority = 'HIGH'")
    return int(rows[0].get("cnt", 0)) if rows else 0


def mark_notification_as_read(notification_id: int) -> bool:
    """Marks a single notification alert as read."""
    affected = execute_non_query("UPDATE Notifications SET is_read = 1 WHERE notification_id = %s", (notification_id,))
    return affected > 0


def mark_all_notifications_as_read() -> int:
    """Marks all unread notifications as read."""
    return execute_non_query("UPDATE Notifications SET is_read = 1 WHERE is_read = 0")


def update_notification_action_status(notification_id: int, new_status: str) -> bool:
    """Updates an alert's action lifecycle status (OPEN, IN_PROGRESS, RESOLVED, DISMISSED)."""
    if new_status not in ACTION_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {ACTION_STATUSES}")

    is_read_flag = 1 if new_status in (STATUS_RESOLVED, STATUS_DISMISSED) else 0
    affected = execute_non_query(
        "UPDATE Notifications SET action_status = %s, is_read = %s WHERE notification_id = %s",
        (new_status, is_read_flag, notification_id)
    )
    return affected > 0


def scan_and_generate_smart_alerts() -> dict[str, int]:
    """Scans student analytics, risk profiles, attendance, and interventions to generate grounded alerts."""
    from core import student_service
    from core.student_profile_service import get_student_360_profile

    students = student_service.get_all_students()
    created_cnt = 0
    skipped_cnt = 0

    for s in students:
        sid = s["student_id"]
        profile = get_student_360_profile(sid)
        if not profile or not profile["profile_status"]["has_data"]:
            continue

        s_name = profile["student"]["name"]
        c_sec = profile["student"]["class_section"]
        att = profile["attendance"]
        acad = profile["academic"]
        lh = profile["learning_health"]
        well = profile["wellness"]
        pred = profile["prediction"]
        risk = profile.get("risk_engine", {})
        r_lvl = risk.get("risk_level", "LOW")
        r_score = risk.get("risk_score")

        # 1. Critical CBSE Attendance Deficit (< 75%)
        att_pct = att.get("percentage")
        if att_pct is not None and att_pct < 75.0:
            res = create_notification(
                title=f"CBSE Attendance Deficit: #{sid} {s_name}",
                message=f"Student attendance is critically low at {att_pct:.1f}% ({att.get('absent_count', 0)} absent days). Mandatory follow-up required.",
                priority=PRIORITY_HIGH,
                alert_type=ALERT_ATTENDANCE,
                student_id=sid,
                dedup_key=f"att_crit_{sid}"
            )
            if res.get("action") == "created":
                created_cnt += 1
            else:
                skipped_cnt += 1

        # 2. High Risk Escalation Alert
        if r_lvl == "HIGH":
            primary_fac = risk.get("factors", [{}])[0].get("name", "Multi-Factor Deficits") if risk.get("factors") else "Critical Deficit"
            res = create_notification(
                title=f"High Risk Profile Flagged: #{sid} {s_name}",
                message=f"Student flagged at HIGH RISK (Composite Score: {r_score}/100). Primary issue: {primary_fac}.",
                priority=PRIORITY_HIGH,
                alert_type=ALERT_RISK_ESCALATION,
                student_id=sid,
                dedup_key=f"risk_high_{sid}"
            )
            if res.get("action") == "created":
                created_cnt += 1
            else:
                skipped_cnt += 1

        # 3. Learning Health Score Drop (< 50)
        lhs_val = lh.get("score")
        if lhs_val is not None and lhs_val < 50.0:
            res = create_notification(
                title=f"Critical LHS Health Drop: #{sid} {s_name}",
                message=f"Composite Learning Health Score dropped to {lhs_val:.1f}/100. Remedial pacing recommended.",
                priority=PRIORITY_MEDIUM,
                alert_type=ALERT_ACADEMIC_DECLINE,
                student_id=sid,
                dedup_key=f"lhs_drop_{sid}"
            )
            if res.get("action") == "created":
                created_cnt += 1
            else:
                skipped_cnt += 1

        # 4. Positive Milestone Notification (Slope >= +2.0 pts/wk or High Score Improvement)
        slope = pred.get("slope", 0.0)
        if slope >= 2.0 and acad.get("average_score", 0) >= 70.0:
            res = create_notification(
                title=f"🌟 Learning Progress Milestone: #{sid} {s_name}",
                message=f"Student demonstrated strong positive trajectory with a growth rate of +{slope:.2f} pts/wk (Avg: {acad.get('average_score', 0):.1f}%).",
                priority=PRIORITY_SUCCESS,
                alert_type=ALERT_MILESTONE_IMPROVEMENT,
                student_id=sid,
                dedup_key=f"milestone_pos_{sid}"
            )
            if res.get("action") == "created":
                created_cnt += 1
            else:
                skipped_cnt += 1

    return {"created": created_cnt, "skipped_duplicates": skipped_cnt}
