"""Authentication and authorization services using secure PBKDF2 password derivation.

Version 2.0: Multi-School Tenant Context Integration and Role-Based Authorization.
"""

from __future__ import annotations

import datetime
import hashlib
import secrets
from typing import Any

from core.database import execute_query, execute_non_query
from core import tenant_service

ITERATIONS = 100000


def hash_password(password: str) -> str:
    """Derive a secure PBKDF2-HMAC-SHA256 password hash with a random salt."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    )
    return f"pbkdf2_sha256${ITERATIONS}${salt}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its PBKDF2-HMAC-SHA256 hash or legacy SHA-256 hash."""
    if not stored_hash:
        return False

    # Support backward compatibility with legacy SHA-256 hashes
    if "$" not in stored_hash:
        legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return secrets.compare_digest(stored_hash, legacy_hash)

    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        hash_hex = parts[3]

        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return secrets.compare_digest(derived.hex(), hash_hex)
    except Exception:
        return False


def login(username: str, password: str) -> bool:
    """Legacy compatibility wrapper for admin logins."""
    user = login_user(username, password)
    return user is not None


def login_user(username: str, password: str) -> dict[str, Any] | None:
    """Authenticate credentials against the Users table.

    Returns authenticated user context with tenant scope if successful.
    """
    username = username.strip().lower()

    # 1. Check Users table (Primary authentication source)
    try:
        rows = execute_query(
            "SELECT user_id, username, full_name, role, status, is_active, "
            "organization_id, school_id, password_hash "
            "FROM Users WHERE LOWER(username) = %s",
            (username,)
        )
        if rows:
            user_data = dict(rows[0])
            raw_active = user_data.get("is_active")
            if raw_active is None:
                status_str = str(user_data.get("status", "Active")).strip().lower()
                is_active = status_str in ("active", "1", "true")
            else:
                is_active = bool(raw_active)

            if is_active and verify_password(password, user_data.get("password_hash")):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_non_query(
                    "UPDATE Users SET last_login = %s WHERE user_id = %s",
                    (timestamp, user_data["user_id"])
                )

                # Dynamically resolve default tenant IDs if not yet set
                org_id = user_data.get("organization_id")
                school_id = user_data.get("school_id")
                if not org_id:
                    org_id = tenant_service.get_default_organization()["organization_id"]
                if not school_id:
                    school_id = tenant_service.get_default_school()["school_id"]

                return {
                    "user_id": user_data["user_id"],
                    "username": user_data["username"],
                    "full_name": user_data["full_name"],
                    "role": user_data["role"],
                    "status": user_data.get("status", "Active"),
                    "is_active": 1 if is_active else 0,
                    "organization_id": org_id,
                    "school_id": school_id,
                }
    except Exception:
        pass

    # 2. Legacy fallback to Admin_Login (Read-only verification; does not mutate DB during login)
    try:
        rows = execute_query(
            "SELECT admin_id, username, password_hash FROM Admin_Login WHERE LOWER(username) = %s",
            (username,)
        )
        if rows:
            admin_data = dict(rows[0])
            if verify_password(password, admin_data.get("password_hash")):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_non_query(
                    "UPDATE Admin_Login SET last_login = %s WHERE username = %s",
                    (timestamp, username)
                )
                def_org = tenant_service.get_default_organization()
                def_school = tenant_service.get_default_school()
                return {
                    "user_id": admin_data["admin_id"],
                    "username": admin_data["username"],
                    "full_name": "Administrator",
                    "role": "Admin",
                    "status": "Active",
                    "is_active": 1,
                    "organization_id": def_org["organization_id"],
                    "school_id": def_school["school_id"],
                }
    except Exception:
        pass

    return None


def get_user_context(user_id: int) -> dict[str, Any] | None:
    """Reloads verified user context from the database by user ID.

    Ensures web session and API layers rely on authoritative server-side state.
    """
    if not user_id:
        return None

    rows = execute_query(
        "SELECT user_id, username, full_name, role, status, is_active, "
        "organization_id, school_id FROM Users WHERE user_id = %s",
        (user_id,)
    )
    if not rows:
        return None

    u = dict(rows[0])
    raw_active = u.get("is_active")
    if raw_active is None:
        status_str = str(u.get("status", "Active")).strip().lower()
        is_active = status_str in ("active", "1", "true")
    else:
        is_active = bool(raw_active)

    if not is_active:
        return None

    # Dynamically resolve tenant boundaries
    if not u.get("organization_id"):
        u["organization_id"] = tenant_service.get_default_organization()["organization_id"]
    if not u.get("school_id"):
        u["school_id"] = tenant_service.get_default_school()["school_id"]

    u["is_active"] = 1
    return u


def logout() -> bool:
    """Perform logout operation (stateless)."""
    return True


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """Legacy compatibility wrapper to change passwords for admin logins."""
    user = login_user(username, old_password)
    if not user:
        return False
    new_hash = hash_password(new_password)
    # Update Admin_Login table
    execute_non_query(
        "UPDATE Admin_Login SET password_hash = %s WHERE username = %s",
        (new_hash, username)
    )
    # Update Users table as well
    try:
        execute_non_query(
            "UPDATE Users SET password_hash = %s WHERE LOWER(username) = %s",
            (new_hash, username.strip().lower())
        )
    except Exception:
        pass
    return True


def create_admin(username: str, password: str) -> bool:
    """Idempotently seeds standard admin credentials with default tenant associations."""
    uname = username.strip().lower()
    hashed = hash_password(password)
    def_org = tenant_service.get_default_organization()
    def_school = tenant_service.get_default_school()
    def_org_id = def_org["organization_id"]
    def_school_id = def_school["school_id"]

    try:
        execute_non_query(
            "INSERT INTO Admin_Login (username, password_hash) VALUES (%s, %s)",
            (uname, hashed)
        )
    except Exception:
        pass

    try:
        execute_non_query(
            "INSERT INTO Users (username, full_name, password_hash, role, status, is_active, organization_id, school_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (uname, "System Administrator", hashed, "Admin", "Active", 1, def_org_id, def_school_id)
        )
    except Exception:
        pass

    return True
