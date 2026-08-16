"""Attendance service handling registries and percentage analytics."""

from __future__ import annotations
from typing import Any
from .database import execute_query, execute_non_query
from .constants import PRESENT, ABSENT, REVERSE_ATTENDANCE_STATUS_MAP, ATTENDANCE_STATUS_MAP


def mark_attendance(attendance_data: dict[str, Any]) -> bool:
    """Insert a single attendance record.
    
    attendance_data: student_id, attendance_date, status ('P'|'A' or 'Present'|'Absent').
    """
    raw_status = attendance_data.get("status", PRESENT)
    # Translate status to P/A codes if full text was supplied
    status = REVERSE_ATTENDANCE_STATUS_MAP.get(raw_status, raw_status)
    if status not in (PRESENT, ABSENT):
        status = PRESENT

    # Insert or update
    student_id = int(attendance_data["student_id"])
    attendance_date = attendance_data.get("attendance_date")
    
    existing = execute_query(
        "SELECT attendance_id FROM Attendance WHERE student_id = %s AND attendance_date = %s",
        (student_id, attendance_date)
    )
    if existing:
        q = "UPDATE Attendance SET status = %s WHERE student_id = %s AND attendance_date = %s"
        return execute_non_query(q, (status, student_id, attendance_date)) >= 0
    else:
        q = "INSERT INTO Attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)"
        return execute_non_query(q, (student_id, attendance_date, status)) == 1


def calculate_attendance_percentage(student_id: int, start_date: str | None = None, end_date: str | None = None) -> float:
    """Calculate the attendance rate for a student."""
    base = "SELECT status, COUNT(*) as cnt FROM Attendance WHERE student_id=%s"
    params: list[Any] = [student_id]
    if start_date:
        base += " AND attendance_date >= %s"
        params.append(start_date)
    if end_date:
        base += " AND attendance_date <= %s"
        params.append(end_date)
    base += " GROUP BY status"
    
    rows = execute_query(base, tuple(params))
    if not rows:
        return 0.0
    present = 0
    total = 0
    for r in rows:
        cnt = int(r.get("cnt", 0))
        total += cnt
        if r.get("status") == PRESENT:
            present += cnt
    if total == 0:
        return 0.0
    return (present / total) * 100.0


def get_students_by_class(class_section: str) -> list[dict[str, Any]]:
    """Retrieve all students currently in a specific class section."""
    return execute_query(
        "SELECT student_id, first_name, last_name, class_section, dob, email, phone "
        "FROM Students WHERE class_section = %s ORDER BY student_id ASC",
        (class_section,)
    )


def get_attendance_for_date_and_class(attendance_date: str, class_section: str) -> dict[int, str]:
    """Retrieve attendance status mapped by student_id for a specific date and class."""
    query = """
        SELECT a.student_id, a.status 
        FROM Attendance a
        JOIN Students s ON a.student_id = s.student_id
        WHERE a.attendance_date = %s AND s.class_section = %s
    """
    rows = execute_query(query, (attendance_date, class_section))
    # Map student_id to readable string ("Present" or "Absent")
    status_map = {}
    for r in rows:
        sid = int(r["student_id"])
        code = r["status"]
        status_map[sid] = ATTENDANCE_STATUS_MAP.get(code, "Present")
    return status_map


def save_attendance(attendance_date: str, class_section: str, attendance_records: dict[int, str]) -> bool:
    """Save or update bulk attendance records for a specific date and class section."""
    for student_id, status_display in attendance_records.items():
        # Map to P/A code
        code = REVERSE_ATTENDANCE_STATUS_MAP.get(status_display, PRESENT)
        
        # Check if already exists for student and date
        existing = execute_query(
            "SELECT attendance_id FROM Attendance WHERE student_id = %s AND attendance_date = %s",
            (student_id, attendance_date)
        )
        if existing:
            execute_non_query(
                "UPDATE Attendance SET status = %s WHERE student_id = %s AND attendance_date = %s",
                (code, student_id, attendance_date)
            )
        else:
            execute_non_query(
                "INSERT INTO Attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)",
                (student_id, attendance_date, code)
            )
    return True


def get_student_attendance(student_id: int) -> list[dict[str, Any]]:
    """Retrieve full attendance history for a student."""
    return execute_query(
        "SELECT attendance_id, student_id, attendance_date, status "
        "FROM Attendance WHERE student_id = %s ORDER BY attendance_date DESC",
        (student_id,)
    )
