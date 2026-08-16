"""Service layer managing user accounts, authentication checks, and access privileges.

Version 2.0: Multi-School Tenant Integration, Role Verification, and Active Status Synchronization.
"""

from __future__ import annotations

import datetime
from typing import Any

from core.database import execute_query, execute_non_query
from core.auth_service import hash_password, verify_password
from core import tenant_service


def list_users(
    school_id: int | None = None,
    organization_id: int | None = None,
    active_only: bool = False
) -> list[dict[str, Any]]:
    """Retrieves users with tenant context, optionally filtered by school or organization."""
    q = (
        "SELECT user_id, username, full_name, role, status, is_active, "
        "organization_id, school_id, created_at, updated_at, last_login "
        "FROM Users"
    )
    clauses = []
    params: list[Any] = []

    if school_id is not None:
        clauses.append("school_id = %s")
        params.append(school_id)
    if organization_id is not None:
        clauses.append("organization_id = %s")
        params.append(organization_id)
    if active_only:
        clauses.append("(is_active = 1 OR LOWER(status) = 'active')")

    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY user_id ASC"

    rows = execute_query(q, tuple(params))
    results = []
    for r in rows:
        d = dict(r)
        # Ensure status and is_active consistency
        if d.get("is_active") is None:
            d["is_active"] = 1 if str(d.get("status", "Active")).lower() == "active" else 0
        if not d.get("status"):
            d["status"] = "Active" if d.get("is_active") else "Inactive"
        results.append(d)
    return results


def get_user(user_id: int) -> dict[str, Any] | None:
    """Retrieves a single user account context by ID."""
    rows = execute_query(
        "SELECT user_id, username, full_name, role, status, is_active, "
        "organization_id, school_id, created_at, updated_at, last_login "
        "FROM Users WHERE user_id = %s",
        (user_id,)
    )
    if not rows:
        return None
    d = dict(rows[0])
    if d.get("is_active") is None:
        d["is_active"] = 1 if str(d.get("status", "Active")).lower() == "active" else 0
    if not d.get("status"):
        d["status"] = "Active" if d.get("is_active") else "Inactive"
    return d


def create_user(
    username: str,
    full_name: str,
    password_t: str,
    role: str = "Teacher",
    status: str = "Active",
    organization_id: int | None = None,
    school_id: int | None = None,
    is_active: bool | None = None
) -> bool:
    """Creates a new secure user record with tenant context in the database."""
    username = username.strip().lower()
    if not username or not full_name or not password_t:
        return False

    p_hash = hash_password(password_t)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Synchronize status and is_active
    if is_active is None:
        act_val = 1 if status.strip().lower() in ("active", "1", "true") else 0
    else:
        act_val = 1 if is_active else 0
    status_val = "Active" if act_val == 1 else "Inactive"

    # Dynamically resolve default tenant IDs if not provided
    if not organization_id:
        organization_id = tenant_service.get_default_organization()["organization_id"]
    if not school_id:
        school_id = tenant_service.get_default_school()["school_id"]

    try:
        affected = execute_non_query(
            "INSERT INTO Users (username, full_name, password_hash, role, status, is_active, "
            "organization_id, school_id, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (username, full_name, p_hash, role, status_val, act_val, organization_id, school_id, now_str, now_str)
        )
        return affected > 0
    except Exception:
        return False


def update_user(
    user_id: int,
    username: str,
    full_name: str,
    role: str,
    status: str,
    organization_id: int | None = None,
    school_id: int | None = None,
    is_active: bool | None = None
) -> bool:
    """Updates user information while maintaining tenant and active status consistency."""
    username = username.strip().lower()
    if not username or not full_name:
        return False

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_active is None:
        act_val = 1 if status.strip().lower() in ("active", "1", "true") else 0
    else:
        act_val = 1 if is_active else 0
    status_val = "Active" if act_val == 1 else "Inactive"

    try:
        if organization_id is not None and school_id is not None:
            affected = execute_non_query(
                "UPDATE Users SET username = %s, full_name = %s, role = %s, status = %s, "
                "is_active = %s, organization_id = %s, school_id = %s, updated_at = %s "
                "WHERE user_id = %s",
                (username, full_name, role, status_val, act_val, organization_id, school_id, now_str, user_id)
            )
        else:
            affected = execute_non_query(
                "UPDATE Users SET username = %s, full_name = %s, role = %s, status = %s, "
                "is_active = %s, updated_at = %s WHERE user_id = %s",
                (username, full_name, role, status_val, act_val, now_str, user_id)
            )
        return affected > 0
    except Exception:
        return False


def delete_user(user_id: int) -> bool:
    """Deletes a user account from the system."""
    try:
        affected = execute_non_query("DELETE FROM Users WHERE user_id = %s", (user_id,))
        return affected > 0
    except Exception:
        return False


def change_user_password(user_id: int, old_password: str, new_password: str) -> bool:
    """Verifies the old password and hashes the new one to update user records."""
    if not new_password or len(new_password.strip()) < 4:
        return False

    rows = execute_query("SELECT password_hash FROM Users WHERE user_id = %s", (user_id,))
    if not rows:
        return False

    stored_hash = rows[0].get("password_hash")
    if not verify_password(old_password, stored_hash):
        return False

    new_hash = hash_password(new_password)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    affected = execute_non_query(
        "UPDATE Users SET password_hash = %s, updated_at = %s WHERE user_id = %s",
        (new_hash, now_str, user_id)
    )
    return affected > 0
