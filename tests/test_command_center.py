"""Unit tests for PMLA-SCWE Academic Intelligence Command Center Service.

Version 1.7 — Academic Intelligence Command Center & Smart Notification Engine
Tests:
1. Complete executive command center aggregation from live database records.
2. Safe fallbacks for newly initialized/empty databases.
3. Grounded smart teacher action recommendations.
4. Priority student ranking and risk tier stratification.
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import command_center_service, student_service, assessment_service, attendance_service, intervention_service
from core.database import initialize_database, execute_non_query, execute_query


class TestCommandCenterService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def setUp(self):
        """Seed clean database fixtures."""
        execute_non_query("DELETE FROM Notifications")
        execute_non_query("DELETE FROM Interventions")
        execute_non_query("DELETE FROM Diagnostic_Logs")
        execute_non_query("DELETE FROM Attendance")
        execute_non_query("DELETE FROM Cyber_Audit")
        execute_non_query("DELETE FROM Weekly_Progress")
        execute_non_query("DELETE FROM Learning_Objectives")
        execute_non_query("DELETE FROM Students")

        # Create learning objective
        execute_non_query(
            "INSERT INTO Learning_Objectives (objective_id, topic_name, description) VALUES (%s, %s, %s)",
            (1, "Data Structures", "Lists, Tuples, Dictionaries")
        )

        # Create 2 test students: One high risk, one high performing
        student_service.add_student({
            "first_name": "Rohan",
            "last_name": "Gupta",
            "class_section": "XII-A",
            "email": "rohan.gupta@example.edu"
        })
        student_service.add_student({
            "first_name": "Ananya",
            "last_name": "Iyer",
            "class_section": "XII-A",
            "email": "ananya.iyer@example.edu"
        })

        rows = execute_query("SELECT student_id, first_name FROM Students ORDER BY student_id ASC")
        self.s1_id = rows[0]["student_id"]  # Rohan (High Risk)
        self.s2_id = rows[1]["student_id"]  # Ananya (Healthy)

        # Rohan: 25% test score, 25% attendance, declining weekly progress -> High Risk
        assessment_service.add_assessment({"student_id": self.s1_id, "objective_id": 1, "score_obtained": 25, "max_score": 100, "test_date": "2026-08-01"})
        attendance_service.mark_attendance({"student_id": self.s1_id, "attendance_date": "2026-08-01", "status": "P"})
        attendance_service.mark_attendance({"student_id": self.s1_id, "attendance_date": "2026-08-02", "status": "A"})
        attendance_service.mark_attendance({"student_id": self.s1_id, "attendance_date": "2026-08-03", "status": "A"})
        attendance_service.mark_attendance({"student_id": self.s1_id, "attendance_date": "2026-08-04", "status": "A"})
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.s1_id, "2026-07-01", 55.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.s1_id, "2026-07-08", 40.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.s1_id, "2026-07-15", 25.0))

        # Ananya: 95% test score, 100% attendance -> Healthy
        assessment_service.add_assessment({"student_id": self.s2_id, "objective_id": 1, "score_obtained": 95, "max_score": 100, "test_date": "2026-08-01"})
        attendance_service.mark_attendance({"student_id": self.s2_id, "attendance_date": "2026-08-01", "status": "P"})
        attendance_service.mark_attendance({"student_id": self.s2_id, "attendance_date": "2026-08-02", "status": "P"})

    def test_command_center_aggregation(self):
        """Test executive data aggregation produces all required summary structures."""
        data = command_center_service.get_executive_command_center_data()

        self.assertIn("summary", data)
        self.assertEqual(data["summary"]["total_students"], 2)
        self.assertAlmostEqual(data["summary"]["class_average_performance"], 60.0, places=1)
        self.assertGreater(data["summary"]["class_learning_health_score"], 0)


        self.assertIn("health_distribution", data)
        self.assertIn("top_priority_students", data)
        self.assertIn("smart_teacher_actions", data)
        self.assertIn("intervention_outcomes", data)

    def test_priority_ranking(self):
        """Test priority student list correctly surfaces high-risk student at top."""
        data = command_center_service.get_executive_command_center_data()
        prio_list = data["top_priority_students"]

        self.assertGreaterEqual(len(prio_list), 1)
        # Rohan should be first
        self.assertEqual(prio_list[0]["student_id"], self.s1_id)
        self.assertEqual(prio_list[0]["risk_level"], "HIGH")

    def test_smart_teacher_actions_grounding(self):
        """Test recommendations are dynamically derived from current cohort deficits."""
        data = command_center_service.get_executive_command_center_data()
        actions = data["smart_teacher_actions"]

        self.assertGreaterEqual(len(actions), 1)
        # Action recommending intervention for Rohan
        action_titles = [a["title"] for a in actions]
        self.assertTrue(any("Remedial" in t or "Intervention" in t or "Review" in t for t in action_titles))

    def test_empty_database_safety(self):
        """Test empty database returns structured zero-value defaults safely."""
        execute_non_query("DELETE FROM Diagnostic_Logs")
        execute_non_query("DELETE FROM Attendance")
        execute_non_query("DELETE FROM Students")

        data = command_center_service.get_executive_command_center_data()
        self.assertEqual(data["summary"]["total_students"], 0)
        self.assertEqual(data["summary"]["class_average_performance"], 0.0)
        self.assertEqual(len(data["top_priority_students"]), 0)


if __name__ == "__main__":
    unittest.main()
