"""Authentication and authorization services using secure PBKDF2 password derivation."""

from __future__ import annotations
import hashlib
import secrets
from core.database import execute_query, execute_non_query

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


def login_user(username: str, password: str) -> dict | None:
    """Authenticate credentials against the Users table. Returns user dictionary if successful."""
    username = username.strip().lower()
    
    # 1. Try checking the new Users table first
    try:
        rows = execute_query("SELECT user_id, username, full_name, role, status, password_hash FROM Users WHERE username=%s", (username,))
        if rows:
            user_data = rows[0]
            if user_data.get("status") == "Active" and verify_password(password, user_data.get("password_hash")):
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_non_query("UPDATE Users SET last_login=%s WHERE user_id=%s", (timestamp, user_data["user_id"]))
                return {
                    "user_id": user_data["user_id"],
                    "username": user_data["username"],
                    "full_name": user_data["full_name"],
                    "role": user_data["role"],
                    "status": user_data["status"]
                }
    except Exception:
        pass

    # 2. Legacy fallback to Admin_Login
    try:
        rows = execute_query("SELECT admin_id, username, password_hash FROM Admin_Login WHERE username=%s", (username,))
        if rows:
            admin_data = rows[0]
            if verify_password(password, admin_data.get("password_hash")):
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_non_query("UPDATE Admin_Login SET last_login=%s WHERE username=%s", (timestamp, username))
                return {
                    "user_id": admin_data["admin_id"],
                    "username": admin_data["username"],
                    "full_name": "Administrator",
                    "role": "Admin",
                    "status": "Active"
                }
    except Exception:
        pass

    return None


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
    affected = execute_non_query("UPDATE Admin_Login SET password_hash=%s WHERE username=%s", (new_hash, username))
    # Update Users table as well if they match
    try:
        execute_non_query("UPDATE Users SET password_hash=%s WHERE username=%s", (new_hash, username))
    except Exception:
        pass
    return affected > 0 or True


def create_admin(username: str, password: str) -> bool:
    """Legacy helper to seed standard admin credentials."""
    hashed = hash_password(password)
    try:
        # Save to both Admin_Login and Users table to keep them in sync
        execute_non_query(
            "INSERT INTO Admin_Login (username, password_hash) VALUES (%s, %s)",
            (username, hashed)
        )
    except Exception:
        pass

    try:
        execute_non_query(
            "INSERT INTO Users (username, full_name, password_hash, role, status) VALUES (%s, %s, %s, %s, %s)",
            (username, "System Administrator", hashed, "Admin", "Active")
        )
    except Exception:
        pass
        
    return True
