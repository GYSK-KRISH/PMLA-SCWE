"""Centralized authorization, role-based access control (RBAC), and tenant boundary service.

Provides the AuthenticatedUser context and centralized permission/scope enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from core.database import execute_query

# Standard Role Constants
ROLE_ADMIN = "Admin"
ROLE_TEACHER = "Teacher"
ROLE_VIEWER = "Viewer"
VALID_ROLES = {ROLE_ADMIN, ROLE_TEACHER, ROLE_VIEWER}


@dataclass(slots=True)
class AuthenticatedUser:
    """Immutable, validated user identity and tenant context."""
    user_id: int
    username: str
    full_name: str
    role: str
    organization_id: int | None = None
    school_id: int | None = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthenticatedUser:
        """Construct an AuthenticatedUser context from dictionary representation."""
        raw_is_active = data.get("is_active")
        if raw_is_active is None:
            # Check legacy status field
            status = str(data.get("status", "Active")).strip().lower()
            is_act = status in ("active", "1", "true")
        else:
            is_act = bool(raw_is_active)

        return cls(
            user_id=int(data.get("user_id", 0)),
            username=str(data.get("username", "")).strip().lower(),
            full_name=str(data.get("full_name", "")),
            role=str(data.get("role", ROLE_TEACHER)).capitalize(),
            organization_id=data.get("organization_id"),
            school_id=data.get("school_id"),
            is_active=is_act,
        )

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> AuthenticatedUser:
        """Construct context directly from a database Users row."""
        return cls.from_dict(row)


def _to_user_obj(user: AuthenticatedUser | dict[str, Any] | None) -> AuthenticatedUser | None:
    """Normalize input into an AuthenticatedUser instance."""
    if user is None:
        return None
    if isinstance(user, AuthenticatedUser):
        return user
    if isinstance(user, dict):
        return AuthenticatedUser.from_dict(user)
    return None


def get_authenticated_user_context(user_id: int) -> AuthenticatedUser | None:
    """Secure server-side re-verification of user context from database.

    Loads the latest database state to prevent trusting client-tampered session values.
    """
    if not user_id:
        return None

    rows = execute_query(
        "SELECT user_id, username, full_name, role, status, is_active, organization_id, school_id "
        "FROM Users WHERE user_id = %s",
        (user_id,)
    )
    if not rows:
        return None

    row = dict(rows[0])
    user = AuthenticatedUser.from_db_row(row)
    return user if user.is_active else None


# =========================================================================
# Role & Capability Checking
# =========================================================================

def is_admin(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role == ROLE_ADMIN)


def is_teacher(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role == ROLE_TEACHER)


def is_viewer(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role == ROLE_VIEWER)


def can_manage_users(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """Only Active Admins may manage system users."""
    return is_admin(user)


def can_manage_organizations(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """Only Active Admins may manage organizations and schools."""
    return is_admin(user)


def can_modify_students(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """Admins and Teachers can create, edit, or delete students (Viewers are read-only)."""
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role in (ROLE_ADMIN, ROLE_TEACHER))


def can_record_attendance(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """Admins and Teachers can record attendance."""
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role in (ROLE_ADMIN, ROLE_TEACHER))


def can_create_interventions(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """Admins and Teachers can create and update teacher interventions."""
    u = _to_user_obj(user)
    return bool(u and u.is_active and u.role in (ROLE_ADMIN, ROLE_TEACHER))


def can_generate_reports(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """All active authenticated users (Admin, Teacher, Viewer) can generate reports."""
    u = _to_user_obj(user)
    return bool(u and u.is_active)


def can_view_analytics(user: AuthenticatedUser | dict[str, Any] | None) -> bool:
    """All active authenticated users (Admin, Teacher, Viewer) can view analytics."""
    u = _to_user_obj(user)
    return bool(u and u.is_active)


# =========================================================================
# Tenant Scope Boundary Validation
# =========================================================================

def has_school_access(
    user: AuthenticatedUser | dict[str, Any] | None,
    school_id: int | None
) -> bool:
    """Validates whether a user is authorized to access data for a specific school.

    Phase 1 Scope:
    - Admin: School-wide authorized access within their organization boundary.
    - Teacher: Access strictly within their assigned school.
    - Viewer: Read-only access strictly within their assigned school.
    """
    u = _to_user_obj(user)
    if not u or not u.is_active:
        return False

    if school_id is None:
        return True

    # Admin access
    if u.role == ROLE_ADMIN:
        if u.school_id is None or u.school_id == school_id:
            return True
        # If admin is scoped to an org, verify school belongs to the same org
        if u.organization_id is not None:
            school_rows = execute_query(
                "SELECT organization_id FROM Schools WHERE school_id = %s",
                (school_id,)
            )
            if school_rows and school_rows[0].get("organization_id") == u.organization_id:
                return True
        return u.school_id == school_id

    # Teacher / Viewer access (strictly school-scoped)
    return u.school_id is not None and int(u.school_id) == int(school_id)


def has_org_access(
    user: AuthenticatedUser | dict[str, Any] | None,
    org_id: int | None
) -> bool:
    """Validates whether a user is authorized for an organization."""
    u = _to_user_obj(user)
    if not u or not u.is_active:
        return False
    if org_id is None:
        return True
    return u.organization_id is not None and int(u.organization_id) == int(org_id)
