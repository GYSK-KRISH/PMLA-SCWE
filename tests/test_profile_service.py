"""Unit tests for Student 360° Intelligence Profile Service.

Version 1.2 — Student 360° Intelligence Profile
Tests:
- Complete student data profile
- Minimal student data (no assessments / wellness)
- Student with missing assessments
- Student with missing wellness records
- Invalid student ID handling
- Chronological timeline ordering (newest first)
- Structured deterministic intervention generation
- Data completeness and confidence level scoring
- Missing data safety (missing metrics are None, not 0)
- Learning Health Score dynamic normalization
- Prediction fallback behavior
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import initialize_database, execute_non_query, execute_query
from core.student_service import add_student
from core.assessment_service import add_assessment
from core.attendance_service import mark_attendance
from core.wellness_service import calculate_wellness_score
from core.student_profile_service import get_student_360_profile


class TestStudentProfileService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize database before test suite runs."""
        initialize_database()


    def setUp(self):
        """Clean and seed test fixtures for isolation."""
        execute_non_query("DELETE FROM Diagnostic_Logs")
        execute_non_query("DELETE FROM Attendance")
        execute_non_query("DELETE FROM Cyber_Audit")
        execute_non_query("DELETE FROM Weekly_Progress")
        execute_non_query("DELETE FROM Achievements")
        execute_non_query("DELETE FROM Students")

        # 1. Ensure a learning objective exists for foreign key
        execute_non_query("DELETE FROM Learning_Objectives")
        execute_non_query(
            "INSERT INTO Learning_Objectives (objective_id, topic_name, description) VALUES (%s, %s, %s)",
            (1, "Python Basics", "Introduction to Python syntax and variables")
        )


        # 2. Full student fixture
        add_student({
            "first_name": "Rahul",
            "last_name": "Sharma",
            "class_section": "XII-A",
            "dob": "2008-05-15",
            "gender": "M",
            "email": "rahul.sharma@example.edu",
            "phone": "+91 9876543210"
        })
        rows = execute_query("SELECT student_id FROM Students WHERE first_name='Rahul'")
        self.full_student_id = rows[0]["student_id"]

        # Populate assessments
        add_assessment({
            "student_id": self.full_student_id,
            "objective_id": 1,
            "score_obtained": 85,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        add_assessment({
            "student_id": self.full_student_id,
            "objective_id": 1,
            "score_obtained": 90,
            "max_score": 100,
            "test_date": "2026-08-08"
        })


        # Populate attendance
        mark_attendance({"student_id": self.full_student_id, "attendance_date": "2026-08-01", "status": "P"})
        mark_attendance({"student_id": self.full_student_id, "attendance_date": "2026-08-02", "status": "P"})
        mark_attendance({"student_id": self.full_student_id, "attendance_date": "2026-08-03", "status": "P"})
        mark_attendance({"student_id": self.full_student_id, "attendance_date": "2026-08-04", "status": "A"})

        # Populate weekly progress
        execute_non_query(
            "INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)",
            (self.full_student_id, "2026-08-01", 82.0)
        )
        execute_non_query(
            "INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)",
            (self.full_student_id, "2026-08-08", 88.0)
        )

        # Populate cyber audit
        audit_payload = {
            "student_id": self.full_student_id,
            "audit_date": "2026-08-10",
            "daily_screen_time": 3.0,
            "study_screen_time": 2.0,
            "recreational_screen_time": 1.0,
            "sleep_duration": 8.0,
            "digital_distraction_level": 1,
            "cyber_safety_awareness": 5
        }
        w_score = calculate_wellness_score(audit_payload)
        execute_non_query(
            "INSERT INTO Cyber_Audit (student_id, audit_date, daily_screen_time, study_screen_time, "
            "recreational_screen_time, sleep_duration, digital_distraction_level, cyber_safety_awareness, "
            "wellness_score, screen_time_hours) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (self.full_student_id, "2026-08-10", 3.0, 2.0, 1.0, 8.0, 1, 5, w_score, 3.0)
        )

        # 2. Minimal student fixture (newly registered, no records)
        add_student({
            "first_name": "Aarav",
            "last_name": "Patel",
            "class_section": "XI-B",
            "dob": "2009-02-20",
            "gender": "M",
            "email": "aarav.patel@example.edu",
            "phone": "+91 9123456780"
        })
        rows_m = execute_query("SELECT student_id FROM Students WHERE first_name='Aarav'")
        self.minimal_student_id = rows_m[0]["student_id"]

    def test_profile_complete_data(self):
        """Test full 360 profile synthesis with complete academic, attendance, progress, and wellness data."""
        profile = get_student_360_profile(self.full_student_id)
        self.assertIsNotNone(profile)

        # Verify Student Demographics
        self.assertEqual(profile["student"]["name"], "Rahul Sharma")
        self.assertEqual(profile["student"]["class_section"], "XII-A")
        self.assertEqual(profile["student"]["class"], "XII")
        self.assertEqual(profile["student"]["section"], "A")

        # Verify Data Completeness
        self.assertEqual(profile["profile_status"]["data_completeness"], 100)
        self.assertEqual(profile["profile_status"]["confidence_level"], "High Confidence")

        # Verify Academic
        self.assertTrue(profile["academic"]["has_data"])
        self.assertEqual(profile["academic"]["average_score"], 87.5)
        self.assertEqual(profile["academic"]["total_assessments"], 2)

        # Verify Attendance
        self.assertTrue(profile["attendance"]["has_data"])
        self.assertEqual(profile["attendance"]["percentage"], 75.0)
        self.assertEqual(profile["attendance"]["present_count"], 3)
        self.assertEqual(profile["attendance"]["absent_count"], 1)

        # Verify Wellness
        self.assertTrue(profile["wellness"]["has_data"])
        self.assertEqual(profile["wellness"]["wellness_score"], 100.0)

        # Verify Learning Health Score
        self.assertTrue(profile["learning_health"]["has_data"])
        self.assertGreater(profile["learning_health"]["score"], 80.0)

    def test_profile_minimal_data(self):
        """Test newly registered student with zero analytical data returns safe missing indicators."""
        profile = get_student_360_profile(self.minimal_student_id)
        self.assertIsNotNone(profile)

        # Data completeness should be 0%
        self.assertEqual(profile["profile_status"]["data_completeness"], 0)
        self.assertEqual(profile["profile_status"]["confidence_level"], "Insufficient Data")

        # Missing data fields should NOT be zero
        self.assertFalse(profile["academic"]["has_data"])
        self.assertIsNone(profile["academic"]["average_score"])
        self.assertEqual(profile["academic"]["display"], "Not enough data yet")

        self.assertFalse(profile["attendance"]["has_data"])
        self.assertIsNone(profile["attendance"]["percentage"])
        self.assertEqual(profile["attendance"]["display"], "Not enough data yet")

        self.assertFalse(profile["wellness"]["has_data"])
        self.assertIsNone(profile["wellness"]["wellness_score"])
        self.assertEqual(profile["wellness"]["display"], "Not enough data yet")

        self.assertFalse(profile["learning_health"]["has_data"])
        self.assertIsNone(profile["learning_health"]["score"])
        self.assertEqual(profile["learning_health"]["risk_level"], "PENDING")

    def test_profile_missing_data_not_zero(self):
        """Verify missing metrics explicitly have has_data=False and None scores instead of misleading zeros."""
        profile = get_student_360_profile(self.minimal_student_id)
        self.assertIsNone(profile["academic"]["average_score"])
        self.assertIsNone(profile["attendance"]["percentage"])
        self.assertIsNone(profile["wellness"]["wellness_score"])
        self.assertIsNone(profile["weekly_progress"]["current_score"])

    def test_profile_lhs_normalization(self):
        """Verify Learning Health Score dynamically normalizes when only partial components exist."""
        # Create student with only assessments (weight 40%) and attendance (weight 20%) -> Available weight = 60%
        add_student({
            "first_name": "Neha",
            "last_name": "Verma",
            "class_section": "X-C"
        })
        sid = execute_query("SELECT student_id FROM Students WHERE first_name='Neha'")[0]["student_id"]

        add_assessment({
            "student_id": sid,
            "score_obtained": 80,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        mark_attendance({"student_id": sid, "attendance_date": "2026-08-01", "status": "P"})

        profile = get_student_360_profile(sid)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["profile_status"]["data_completeness"], 60)
        self.assertEqual(profile["profile_status"]["confidence_level"], "Moderate Confidence")

        # Academic avg = 80 (contrib = 32), Attendance = 100 (contrib = 20) -> sum = 52
        # Normalized LHS = (52 / 60) * 100 = 86.7
        self.assertTrue(profile["learning_health"]["has_data"])
        self.assertEqual(profile["learning_health"]["score"], 86.7)
        self.assertEqual(profile["learning_health"]["risk_level"], "LOW")

    def test_profile_invalid_id(self):
        """Verify non-existent student ID returns None gracefully."""
        profile = get_student_360_profile(999999)
        self.assertIsNone(profile)

    def test_profile_timeline_ordering(self):
        """Verify timeline events are sorted chronologically descending (newest first)."""
        profile = get_student_360_profile(self.full_student_id)
        self.assertIsNotNone(profile)
        timeline = profile["timeline"]
        self.assertGreater(len(timeline), 0)

        timestamps = [event["timestamp"] for event in timeline]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_profile_recommendations_generation(self):
        """Verify deterministic structured intervention generation with priorities."""
        profile = get_student_360_profile(self.full_student_id)
        self.assertIsNotNone(profile)
        interventions = profile["interventions"]
        self.assertIsInstance(interventions, list)
        self.assertGreater(len(interventions), 0)

        for iv in interventions:
            self.assertIn("id", iv)
            self.assertIn("priority", iv)
            self.assertIn(iv["priority"], ["HIGH", "MEDIUM", "LOW"])
            self.assertIn("title", iv)
            self.assertIn("description", iv)
            self.assertIn("completed", iv)

    def test_profile_prediction_safe_fallback(self):
        """Verify prediction handles students with single or zero weekly records safely."""
        profile_min = get_student_360_profile(self.minimal_student_id)
        self.assertFalse(profile_min["prediction"]["has_data"])
        self.assertIsNone(profile_min["prediction"]["predicted_score"])


if __name__ == "__main__":
    unittest.main()
