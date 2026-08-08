"""Authentication module.

Implements simple password hashing and DB-backed authentication.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from .database import execute_select, execute_modify
from .database import execute_query, execute_non_query


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login(username: str, password: str) -> bool:
    rows = execute_query("SELECT password_hash FROM Admin_Login WHERE username=%s", (username,))
    if not rows:
        return False
    first_row = rows[0]
    stored = first_row.get("password_hash") if isinstance(first_row, dict) else first_row[0]
    return stored == _hash_password(password)


def logout() -> bool:
    return True


def change_password(username: str, old_password: str, new_password: str) -> bool:
    if not login(username, old_password):
        return False
    new_hash = _hash_password(new_password)
    affected = execute_non_query("UPDATE Admin_Login SET password_hash=%s WHERE username=%s", (new_hash, username))
    return affected > 0


def create_admin(username: str, password: str) -> bool:
    hashed = _hash_password(password)
    try:
        affected = execute_non_query("INSERT INTO Admin_Login (username, password_hash) VALUES (%s, %s)", (username, hashed))
        return affected > 0
    except Exception:
        return False
