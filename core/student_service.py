"""Student database service module.

Version 2.0: Multi-School Tenant Integration and Dynamic School Resolution.
"""

from __future__ import annotations

import datetime
from typing import Any
from .database import execute_query, execute_non_query
from core import tenant_service


def add_student(student_data: dict[str, Any]) -> bool:
    """Insert a new student record with tenant scope into the database."""
    school_id = student_data.get("school_id")
    if not school_id:
        def_school = tenant_service.get_default_school()
        school_id = def_school["school_id"]

    q = (
        "INSERT INTO Students (school_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    enrollment = student_data.get("enrollment_date") or datetime.date.today().isoformat()

    params = (
        school_id,
        student_data.get("first_name"),
        student_data.get("last_name"),
        student_data.get("class_section"),
        student_data.get("dob"),
        student_data.get("gender", "O"),
        student_data.get("email"),
        student_data.get("phone"),
        enrollment,
    )
    return execute_non_query(q, params) == 1


def update_student(student_id: int, student_data: dict[str, Any]) -> bool:
    """Update details of an existing student."""
    school_id = student_data.get("school_id")
    if school_id is not None:
        q = (
            "UPDATE Students SET school_id=%s, first_name=%s, last_name=%s, class_section=%s, "
            "dob=%s, gender=%s, email=%s, phone=%s WHERE student_id=%s"
        )
        params = (
            school_id,
            student_data.get("first_name"),
            student_data.get("last_name"),
            student_data.get("class_section"),
            student_data.get("dob"),
            student_data.get("gender"),
            student_data.get("email"),
            student_data.get("phone"),
            student_id,
        )
    else:
        q = (
            "UPDATE Students SET first_name=%s, last_name=%s, class_section=%s, "
            "dob=%s, gender=%s, email=%s, phone=%s WHERE student_id=%s"
        )
        params = (
            student_data.get("first_name"),
            student_data.get("last_name"),
            student_data.get("class_section"),
            student_data.get("dob"),
            student_data.get("gender"),
            student_data.get("email"),
            student_data.get("phone"),
            student_id,
        )
    return execute_non_query(q, params) == 1


def delete_student(student_id: int) -> bool:
    """Remove a student record from the database."""
    q = "DELETE FROM Students WHERE student_id=%s"
    return execute_non_query(q, (student_id,)) == 1


def search_students(query: str, school_id: int | None = None) -> list[dict[str, Any]]:
    """Search for students by ID, first name, last name, or class section, optionally within a school."""
    base_q = (
        "SELECT student_id, school_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date "
        "FROM Students WHERE (student_id=%s OR first_name LIKE %s OR last_name LIKE %s OR class_section=%s)"
    )
    try:
        sid = int(query)
    except Exception:
        sid = -1
    like = f"%{query}%"

    params: list[Any] = [sid, like, like, query]
    if school_id is not None:
        base_q += " AND school_id = %s"
        params.append(school_id)

    return [dict(r) for r in execute_query(base_q, tuple(params))]


def get_all_students(school_id: int | None = None) -> list[dict[str, Any]]:
    """Retrieve all students, optionally scoped to a specific school."""
    q = (
        "SELECT student_id, school_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date "
        "FROM Students"
    )
    params: tuple[Any, ...] = ()
    if school_id is not None:
        q += " WHERE school_id = %s"
        params = (school_id,)
    q += " ORDER BY student_id ASC"
    return [dict(r) for r in execute_query(q, params)]


def get_student_by_id(student_id: int) -> dict[str, Any] | None:
    """Retrieve a single student record by their primary ID."""
    rows = execute_query(
        "SELECT student_id, school_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date "
        "FROM Students WHERE student_id=%s",
        (student_id,)
    )
    return dict(rows[0]) if rows else None
