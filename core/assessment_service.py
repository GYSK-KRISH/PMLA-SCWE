"""Assessment service managing student academic test results."""

from __future__ import annotations
from typing import Any
from .database import execute_query, execute_non_query


def add_assessment(assessment_data: dict[str, Any]) -> bool:
    """Insert a diagnostic log (assessment).
    
    assessment_data contains: student_id, objective_id (optional), score_obtained, max_score (optional), test_date.
    """
    q = (
        "INSERT INTO Diagnostic_Logs (student_id, objective_id, score_obtained, max_score, test_date)"
        " VALUES (%s, %s, %s, %s, %s)"
    )
    params = (
        assessment_data.get("student_id"),
        assessment_data.get("objective_id"),
        assessment_data.get("score_obtained"),
        assessment_data.get("max_score", 100),
        assessment_data.get("test_date"),
    )
    return execute_non_query(q, params) == 1


def get_assessment_history(student_id: int) -> list[dict[str, Any]]:
    """Retrieve historical academic assessment marks for a student."""
    q = (
        "SELECT log_id, student_id, objective_id, score_obtained, max_score, test_date "
        "FROM Diagnostic_Logs WHERE student_id=%s ORDER BY test_date DESC"
    )
    return execute_query(q, (student_id,))
