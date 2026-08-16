"""Tenant service managing Organizations and Schools for PMLA-SCWE multi-school architecture.

Provides dynamic resolution of default legacy tenants and administrative CRUD operations.
"""

from __future__ import annotations

from typing import Any
from core.database import execute_query, execute_non_query

DEFAULT_ORG_CODE = "DEFAULT_ORG"
DEFAULT_ORG_NAME = "PMLA-SCWE Default Organization"

DEFAULT_SCHOOL_CODE = "DEFAULT_SCHOOL"
DEFAULT_SCHOOL_NAME = "Default School"


def get_default_organization() -> dict[str, Any]:
    """Retrieves or dynamically provisions the default organization.

    Guarantees that an organization boundary always exists.
    """
    rows = execute_query(
        "SELECT organization_id, name, code, is_active, created_at "
        "FROM Organizations WHERE code = %s LIMIT 1",
        (DEFAULT_ORG_CODE,)
    )
    if rows:
        return dict(rows[0])

    # Fallback/Auto-provision if table exists but record doesn't
    try:
        execute_non_query(
            "INSERT INTO Organizations (name, code, is_active) VALUES (%s, %s, %s)",
            (DEFAULT_ORG_NAME, DEFAULT_ORG_CODE, 1)
        )
        new_rows = execute_query(
            "SELECT organization_id, name, code, is_active, created_at "
            "FROM Organizations WHERE code = %s LIMIT 1",
            (DEFAULT_ORG_CODE,)
        )
        if new_rows:
            return dict(new_rows[0])
    except Exception:
        pass

    # Safety fallback object if database schema is being created
    return {
        "organization_id": 1,
        "name": DEFAULT_ORG_NAME,
        "code": DEFAULT_ORG_CODE,
        "is_active": 1,
        "created_at": None,
    }


def get_default_school() -> dict[str, Any]:
    """Retrieves or dynamically provisions the default school.

    Guarantees that a school tenant boundary always exists.
    """
    rows = execute_query(
        "SELECT school_id, organization_id, name, code, is_active, created_at "
        "FROM Schools WHERE code = %s LIMIT 1",
        (DEFAULT_SCHOOL_CODE,)
    )
    if rows:
        return dict(rows[0])

    # Auto-provision under default org
    org = get_default_organization()
    org_id = org["organization_id"]

    try:
        execute_non_query(
            "INSERT INTO Schools (organization_id, name, code, is_active) VALUES (%s, %s, %s, %s)",
            (org_id, DEFAULT_SCHOOL_NAME, DEFAULT_SCHOOL_CODE, 1)
        )
        new_rows = execute_query(
            "SELECT school_id, organization_id, name, code, is_active, created_at "
            "FROM Schools WHERE code = %s LIMIT 1",
            (DEFAULT_SCHOOL_CODE,)
        )
        if new_rows:
            return dict(new_rows[0])
    except Exception:
        pass

    return {
        "school_id": 1,
        "organization_id": org_id,
        "name": DEFAULT_SCHOOL_NAME,
        "code": DEFAULT_SCHOOL_CODE,
        "is_active": 1,
        "created_at": None,
    }


def get_organization(org_id: int) -> dict[str, Any] | None:
    """Retrieve an organization by its primary ID."""
    rows = execute_query(
        "SELECT organization_id, name, code, is_active, created_at "
        "FROM Organizations WHERE organization_id = %s",
        (org_id,)
    )
    return dict(rows[0]) if rows else None


def get_organization_by_code(code: str) -> dict[str, Any] | None:
    """Retrieve an organization by its unique short code."""
    rows = execute_query(
        "SELECT organization_id, name, code, is_active, created_at "
        "FROM Organizations WHERE code = %s",
        (code.strip().upper(),)
    )
    return dict(rows[0]) if rows else None


def get_school(school_id: int) -> dict[str, Any] | None:
    """Retrieve a school by its primary ID."""
    rows = execute_query(
        "SELECT school_id, organization_id, name, code, is_active, created_at "
        "FROM Schools WHERE school_id = %s",
        (school_id,)
    )
    return dict(rows[0]) if rows else None


def get_school_by_code(code: str) -> dict[str, Any] | None:
    """Retrieve a school by its unique short code."""
    rows = execute_query(
        "SELECT school_id, organization_id, name, code, is_active, created_at "
        "FROM Schools WHERE code = %s",
        (code.strip().upper(),)
    )
    return dict(rows[0]) if rows else None


def list_organizations(active_only: bool = False) -> list[dict[str, Any]]:
    """List all organizations."""
    q = "SELECT organization_id, name, code, is_active, created_at FROM Organizations"
    params = ()
    if active_only:
        q += " WHERE is_active = 1"
    q += " ORDER BY organization_id ASC"
    return [dict(r) for r in execute_query(q, params)]


def list_schools(organization_id: int | None = None, active_only: bool = False) -> list[dict[str, Any]]:
    """List schools, optionally filtered by organization ID."""
    q = "SELECT school_id, organization_id, name, code, is_active, created_at FROM Schools"
    clauses = []
    params: list[Any] = []
    if organization_id is not None:
        clauses.append("organization_id = %s")
        params.append(organization_id)
    if active_only:
        clauses.append("is_active = 1")
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY school_id ASC"
    return [dict(r) for r in execute_query(q, tuple(params))]


def create_organization(name: str, code: str, is_active: bool = True) -> int | None:
    """Create a new organization and return its ID."""
    name = name.strip()
    code = code.strip().upper()
    if not name or not code:
        return None

    try:
        execute_non_query(
            "INSERT INTO Organizations (name, code, is_active) VALUES (%s, %s, %s)",
            (name, code, 1 if is_active else 0)
        )
        row = get_organization_by_code(code)
        return row["organization_id"] if row else None
    except Exception:
        return None


def create_school(organization_id: int, name: str, code: str, is_active: bool = True) -> int | None:
    """Create a new school within an organization and return its ID."""
    name = name.strip()
    code = code.strip().upper()
    if not name or not code or not organization_id:
        return None

    # Validate org exists
    org = get_organization(organization_id)
    if not org:
        return None

    try:
        execute_non_query(
            "INSERT INTO Schools (organization_id, name, code, is_active) VALUES (%s, %s, %s, %s)",
            (organization_id, name, code, 1 if is_active else 0)
        )
        row = get_school_by_code(code)
        return row["school_id"] if row else None
    except Exception:
        return None


def update_organization(org_id: int, name: str, is_active: bool) -> bool:
    """Update organization details."""
    name = name.strip()
    if not name:
        return False
    affected = execute_non_query(
        "UPDATE Organizations SET name = %s, is_active = %s WHERE organization_id = %s",
        (name, 1 if is_active else 0, org_id)
    )
    return affected > 0


def update_school(school_id: int, name: str, is_active: bool) -> bool:
    """Update school details."""
    name = name.strip()
    if not name:
        return False
    affected = execute_non_query(
        "UPDATE Schools SET name = %s, is_active = %s WHERE school_id = %s",
        (name, 1 if is_active else 0, school_id)
    )
    return affected > 0
