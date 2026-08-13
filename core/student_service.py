"""Student database service module."""

from __future__ import annotations
from typing import Any
from .database import execute_query, execute_non_query


def add_student(student_data: dict[str, Any]) -> bool:
    """Insert a new student record into the database."""
    q = (
        "INSERT INTO Students (first_name, last_name, class_section, dob, gender, email, phone, enrollment_date)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    import datetime
    enrollment = student_data.get("enrollment_date") or datetime.date.today().isoformat()
    
    params = (
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
    q = (
        "UPDATE Students SET first_name=%s, last_name=%s, class_section=%s, dob=%s, gender=%s, email=%s, phone=%s"
        " WHERE student_id=%s"
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


def search_students(query: str) -> list[dict[str, Any]]:
    """Search for students by ID, first name, last name, or class section."""
    q = (
        "SELECT student_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date FROM Students "
        "WHERE student_id=%s OR first_name LIKE %s OR last_name LIKE %s OR class_section=%s"
    )
    try:
        sid = int(query)
    except Exception:
        sid = -1
    like = f"%{query}%"
    return execute_query(q, (sid, like, like, query))


def get_all_students() -> list[dict[str, Any]]:
    """Retrieve all students currently stored in the database."""
    return execute_query(
        "SELECT student_id, first_name, last_name, class_section, dob, gender, email, phone, enrollment_date "
        "FROM Students ORDER BY student_id ASC"
    )
