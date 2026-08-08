"""Student management module backed by the Students table."""

from __future__ import annotations

from typing import Dict, List, Any

from .database import execute_select, execute_modify


def add_student(student_data: Dict[str, Any]) -> bool:
    q = (
        "INSERT INTO Students (first_name, last_name, class_section, dob, gender, email, phone)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s)"
    )
    params = (
        student_data.get("first_name"),
        student_data.get("last_name"),
        student_data.get("class_section"),
        student_data.get("dob"),
        student_data.get("gender"),
        student_data.get("email"),
        student_data.get("phone"),
    )
    return execute_modify(q, params) == 1


def update_student(student_id: int, student_data: Dict[str, Any]) -> bool:
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
    return execute_modify(q, params) == 1


def delete_student(student_id: int) -> bool:
    q = "DELETE FROM Students WHERE student_id=%s"
    return execute_modify(q, (student_id,)) == 1


def search_students(query: str) -> List[Dict[str, Any]]:
    q = (
        "SELECT student_id, first_name, last_name, class_section, email, phone FROM Students "
        "WHERE student_id=%s OR first_name LIKE %s OR last_name LIKE %s OR class_section=%s"
    )
    # allow numeric id search
    try:
        sid = int(query)
    except Exception:
        sid = -1
    like = f"%{query}%"
    return execute_select(q, (sid, like, like, query))
