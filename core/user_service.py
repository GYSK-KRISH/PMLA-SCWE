"""Service layer managing user accounts, authentication checks, and access privileges."""

from __future__ import annotations
import datetime
from core.database import execute_query, execute_non_query
from core.auth_service import hash_password, verify_password


def list_users() -> list[dict]:
    """Retrieves all users sorted by user_id."""
    return execute_query("SELECT user_id, username, full_name, role, status, created_at, last_login FROM Users ORDER BY user_id ASC")


def get_user(user_id: int) -> dict | None:
    """Retrieves a single user account context by ID."""
    rows = execute_query("SELECT user_id, username, full_name, role, status, created_at, last_login FROM Users WHERE user_id = %s", (user_id,))
    return rows[0] if rows else None


def create_user(username: str, full_name: str, password_t: str, role: str = "Teacher", status: str = "Active") -> bool:
    """Creates a new secure user record in the database."""
    username = username.strip().lower()
    if not username or not full_name or not password_t:
        return False
        
    p_hash = hash_password(password_t)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        affected = execute_non_query(
            "INSERT INTO Users (username, full_name, password_hash, role, status, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, full_name, p_hash, role, status, now_str)
        )
        return affected > 0
    except Exception:
        return False


def update_user(user_id: int, username: str, full_name: str, role: str, status: str) -> bool:
    """Updates user information."""
    username = username.strip().lower()
    if not username or not full_name:
        return False
        
    try:
        affected = execute_non_query(
            "UPDATE Users SET username = %s, full_name = %s, role = %s, status = %s WHERE user_id = %s",
            (username, full_name, role, status, user_id)
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
        
    # Load stored hash
    rows = execute_query("SELECT password_hash FROM Users WHERE user_id = %s", (user_id,))
    if not rows:
        return False
        
    stored_hash = rows[0].get("password_hash")
    if not verify_password(old_password, stored_hash):
        return False
        
    new_hash = hash_password(new_password)
    affected = execute_non_query("UPDATE Users SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
    return affected > 0
