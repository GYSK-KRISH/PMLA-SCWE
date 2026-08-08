"""Attendance module backed by the Attendance table."""

from __future__ import annotations

from typing import Dict, Optional

from .database import execute_modify, execute_select


def mark_attendance(attendance_data: Dict[str, object]) -> bool:
    """Insert an attendance record.

    attendance_data should contain: student_id (int), attendance_date (YYYY-MM-DD) optional, status ('P'|'A').
    """
    q = "INSERT INTO Attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)"
    params = (
        attendance_data.get("student_id"),
        attendance_data.get("attendance_date"),
        attendance_data.get("status", "P"),
    )
    return execute_modify(q, params) == 1


def calculate_attendance_percentage(student_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> float:
    """Calculate attendance percentage for a student between optional dates.

    Dates should be 'YYYY-MM-DD' strings. If omitted, consider all records.
    Returns percentage (0.0-100.0) or 0.0 when no records.
    """
    base = "SELECT status, COUNT(*) as cnt FROM Attendance WHERE student_id=%s"
    params = [student_id]
    if start_date:
        base += " AND attendance_date >= %s"
        params.append(start_date)
    if end_date:
        base += " AND attendance_date <= %s"
        params.append(end_date)
    base += " GROUP BY status"
    rows = execute_select(base, tuple(params))
    if not rows:
        return 0.0
    present = 0
    total = 0
    for r in rows:
        cnt = int(r.get("cnt", 0))
        total += cnt
        if r.get("status") == "P":
            present += cnt
    if total == 0:
        return 0.0
    return (present / total) * 100.0
