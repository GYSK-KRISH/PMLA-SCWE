"""Assessment module backed by the Diagnostic_Logs table."""

from __future__ import annotations

from typing import Dict, List, Any

from .database import execute_modify, execute_select


def add_assessment(assessment_data: Dict[str, Any]) -> bool:
    """Insert a diagnostic log (assessment).

    assessment_data: student_id, objective_id (optional), score_obtained, max_score (optional), test_date (YYYY-MM-DD optional)
    """
    q = (
        "INSERT INTO Diagnostic_Logs (student_id, objective_id, score_obtained, max_score, test_date)"
        " VALUES (%s,%s,%s,%s,%s)"
    )
    params = (
        assessment_data.get("student_id"),
        assessment_data.get("objective_id"),
        assessment_data.get("score_obtained"),
        assessment_data.get("max_score", 100),
        assessment_data.get("test_date"),
    )
    return execute_modify(q, params) == 1


def get_assessment_history(student_id: int) -> List[Dict[str, Any]]:
    q = "SELECT log_id, student_id, objective_id, score_obtained, max_score, test_date FROM Diagnostic_Logs WHERE student_id=%s ORDER BY test_date DESC"
    return execute_select(q, (student_id,))
