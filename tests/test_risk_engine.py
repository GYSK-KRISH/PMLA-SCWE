"""Unit tests for Explainable Learning Risk Engine and Explainability Services.

Version 1.3 — Explainable Predictive Analytics
Tests:
1. Consistently improving student (Low risk, positive narrative)
2. Consistently declining student (High risk, compounding factors, early warnings)
3. Low attendance student (CBSE attendance deficit and warning)
4. Insufficient data student (Safe fallback, INSUFFICIENT DATA status)
5. Invalid values handling (Negative scores, percentages > 100, out-of-range screen time)
6. Duplicate warning prevention & alert cooldown
7. Class risk overview aggregation
8. Database-integrated student risk profile computation
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import constants, risk_engine, explainability
from core.database import initialize_database, execute_non_query, execute_query
from core.student_service import add_student
from core.assessment_service import add_assessment
from core.attendance_service import mark_attendance
from core.wellness_service import calculate_wellness_score


class TestExplainableRiskEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize database before test suite runs."""
        initialize_database()

    def setUp(self):
        """Clean and seed isolated test fixtures."""
        execute_non_query("DELETE FROM Diagnostic_Logs")
        execute_non_query("DELETE FROM Attendance")
        execute_non_query("DELETE FROM Cyber_Audit")
        execute_non_query("DELETE FROM Weekly_Progress")
        execute_non_query("DELETE FROM Learning_Objectives")
        execute_non_query("DELETE FROM Students")

        # Create learning objective
        execute_non_query(
            "INSERT INTO Learning_Objectives (objective_id, topic_name, description) VALUES (%s, %s, %s)",
            (1, "Python Core", "Fundamentals of Python programming")
        )

        # 1. High Risk Declining Student Fixture
        add_student({
            "first_name": "Karan",
            "last_name": "Mehta",
            "class_section": "XII-A",
            "email": "karan.mehta@example.edu"
        })
        rows_k = execute_query("SELECT student_id FROM Students WHERE first_name='Karan'")
        self.declining_student_id = rows_k[0]["student_id"]

        add_assessment({
            "student_id": self.declining_student_id,
            "objective_id": 1,
            "score_obtained": 45,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        # 3 absent, 1 present -> 25% attendance
        mark_attendance({"student_id": self.declining_student_id, "attendance_date": "2026-08-01", "status": "A"})
        mark_attendance({"student_id": self.declining_student_id, "attendance_date": "2026-08-02", "status": "A"})
        mark_attendance({"student_id": self.declining_student_id, "attendance_date": "2026-08-03", "status": "A"})
        mark_attendance({"student_id": self.declining_student_id, "attendance_date": "2026-08-04", "status": "P"})

        # Declining weekly progress: 75 -> 65 -> 50 -> 42 (negative slope)
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.declining_student_id, "2026-08-01", 75.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.declining_student_id, "2026-08-08", 65.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.declining_student_id, "2026-08-15", 50.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.declining_student_id, "2026-08-22", 42.0))

        # Cyber audit with elevated screen exposure and concern score
        execute_non_query(
            "INSERT INTO Cyber_Audit (student_id, daily_screen_time, study_screen_time, recreational_screen_time, "
            "sleep_duration, digital_distraction_level, cyber_safety_awareness, wellness_score, screen_time_hours, audit_date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (self.declining_student_id, 8.5, 1.5, 7.0, 5.5, 4, 2, 45.0, 8.5, "2026-08-20")
        )

        # 2. Insufficient Data Student Fixture

        add_student({
            "first_name": "Sana",
            "last_name": "Khan",
            "class_section": "XII-A",
            "email": "sana.khan@example.edu"
        })
        rows_s = execute_query("SELECT student_id FROM Students WHERE first_name='Sana'")
        self.insufficient_student_id = rows_s[0]["student_id"]

    # =======================================================================
    # PURE METRICS UNIT TESTS (Database-Agnostic)
    # =======================================================================

    def test_consistently_improving_student(self):
        """Test pure risk engine calculation for an exemplary, improving student."""
        metrics = {
            "has_data": True,
            "data_completeness": 100,
            "academic_average": 92.0,
            "attendance_percentage": 96.0,
            "slope": 1.85,
            "trend_direction": constants.TRAJECTORY_IMPROVING,
            "progress_count": 4,
            "wellness_score": 90.0,
            "daily_screen_time": 2.5,
            "learning_health_score": 93.5
        }

        res = risk_engine.calculate_risk_score_from_metrics(metrics)
        self.assertEqual(res["risk_level"], constants.RISK_LEVEL_LOW)
        self.assertLess(res["risk_score"], constants.RISK_SCORE_MEDIUM_THRESHOLD)
        self.assertEqual(res["breakdown"]["academic_points"], 0.0)
        self.assertEqual(res["breakdown"]["attendance_points"], 0.0)
        self.assertEqual(res["breakdown"]["trend_points"], 0.0)
        self.assertEqual(len(res["early_warnings"]), 0)

        # Verify explainability narrative
        factors = explainability.extract_contributing_risk_factors(metrics, res["breakdown"])
        self.assertEqual(len(factors), 0)

        narrative = explainability.generate_why_narrative(metrics, factors, res["risk_level"])
        self.assertTrue(any("consistent mastery" in n.lower() or "healthy" in n.lower() for n in narrative))

    def test_consistently_declining_student(self):
        """Test pure risk engine calculation for a student with compounding critical deficits."""
        metrics = {
            "has_data": True,
            "data_completeness": 100,
            "academic_average": 46.0,          # Critical (< 50%) -> high points
            "attendance_percentage": 65.0,      # Critical (< 75%) -> high points
            "slope": -2.4,                      # Negative slope -> trend points
            "trend_direction": constants.TRAJECTORY_DECLINING,
            "progress_count": 4,
            "wellness_score": 45.0,             # Concern (< 55%) -> wellness points
            "daily_screen_time": 8.5,           # High screen (> 6h)
            "learning_health_score": 44.0       # Critical LHS (< 50)
        }

        res = risk_engine.calculate_risk_score_from_metrics(metrics)
        self.assertEqual(res["risk_level"], constants.RISK_LEVEL_HIGH)
        self.assertGreaterEqual(res["risk_score"], constants.RISK_SCORE_HIGH_THRESHOLD)

        # Check breakdown
        self.assertGreater(res["breakdown"]["academic_points"], 15.0)
        self.assertGreater(res["breakdown"]["attendance_points"], 15.0)
        self.assertGreater(res["breakdown"]["trend_points"], 5.0)
        self.assertGreater(res["breakdown"]["wellness_points"], 4.0)
        self.assertGreater(res["breakdown"]["lhs_points"], 4.0)

        # Check early warnings
        warning_codes = [w["code"] for w in res["early_warnings"]]
        self.assertIn(constants.WARN_ACADEMIC, warning_codes)
        self.assertIn(constants.WARN_ATTENDANCE, warning_codes)
        self.assertIn(constants.WARN_DECLINE, warning_codes)
        self.assertIn(constants.WARN_MULTI_FACTOR, warning_codes)

        # Check explainability factors & narrative
        factors = explainability.extract_contributing_risk_factors(metrics, res["breakdown"])
        self.assertGreaterEqual(len(factors), 3)

        narrative = explainability.generate_why_narrative(metrics, factors, res["risk_level"])
        self.assertTrue(any("academic performance" in n.lower() for n in narrative))
        self.assertTrue(any("attendance" in n.lower() for n in narrative))

        # Check deterministic interventions
        actions = explainability.generate_explainable_recommendations(factors, res["risk_level"])
        action_ids = [a["id"] for a in actions]
        self.assertIn("remedial_support", action_ids)
        self.assertIn("attendance_counseling", action_ids)

    def test_low_attendance_student(self):
        """Test student with strong academics but low attendance below CBSE threshold."""
        metrics = {
            "has_data": True,
            "data_completeness": 80,
            "academic_average": 86.0,
            "attendance_percentage": 62.0,      # Critical (< 75%)
            "slope": 0.5,
            "trend_direction": constants.TRAJECTORY_IMPROVING,
            "progress_count": 3,
            "wellness_score": 80.0,
            "daily_screen_time": 3.0,
            "learning_health_score": 76.0
        }

        res = risk_engine.calculate_risk_score_from_metrics(metrics)
        self.assertGreaterEqual(res["breakdown"]["attendance_points"], 15.0)
        self.assertEqual(res["breakdown"]["academic_points"], 0.0)

        factors = explainability.extract_contributing_risk_factors(metrics, res["breakdown"])
        self.assertEqual(factors[0]["factor_key"], "attendance")
        self.assertEqual(factors[0]["impact"], "high")

        warning_codes = [w["code"] for w in res["early_warnings"]]
        self.assertIn(constants.WARN_ATTENDANCE, warning_codes)

    def test_insufficient_data_student(self):
        """Test student with zero or missing metrics safely returns INSUFFICIENT DATA."""
        metrics = {
            "has_data": False,
            "data_completeness": 0,
            "academic_average": None,
            "attendance_percentage": None,
            "slope": 0.0,
            "trend_direction": constants.TRAJECTORY_INSUFFICIENT,
            "progress_count": 0,
            "wellness_score": None,
            "daily_screen_time": None,
            "learning_health_score": None
        }

        res = risk_engine.calculate_risk_score_from_metrics(metrics)
        self.assertEqual(res["risk_level"], constants.RISK_LEVEL_INSUFFICIENT)
        self.assertIsNone(res["risk_score"])
        self.assertEqual(len(res["early_warnings"]), 0)

        narrative = explainability.generate_why_narrative(metrics, [], res["risk_level"])
        self.assertTrue(any("insufficient" in n.lower() for n in narrative))

    def test_invalid_values_handling(self):
        """Test out-of-boundary values are caught by data quality validation without raising exceptions."""
        metrics = {
            "has_data": True,
            "data_completeness": 100,
            "academic_average": -20.0,          # Out of bounds
            "attendance_percentage": 150.0,     # Out of bounds
            "slope": 0.0,
            "trend_direction": constants.TRAJECTORY_STABLE,
            "progress_count": 2,
            "wellness_score": 200.0,
            "daily_screen_time": 35.0,          # Out of 24h bounds
            "learning_health_score": 50.0
        }

        quality = risk_engine.validate_metrics_data_quality(metrics)
        self.assertFalse(quality["is_valid"])
        self.assertGreater(len(quality["quality_notes"]), 0)

        # Engine should safely sanitize bounded values
        res = risk_engine.calculate_risk_score_from_metrics(metrics)
        self.assertIsNotNone(res["risk_level"])
        self.assertIsInstance(res["risk_score"], int)

    def test_duplicate_warning_prevention(self):
        """Test deduplication cooldown prevents warning floods for the same student."""
        sid = 99999
        code = constants.WARN_ATTENDANCE
        
        # First call should allow dispatch
        first_check = risk_engine.should_dispatch_warning(sid, code, cooldown_seconds=60)
        self.assertTrue(first_check)

        # Immediate second call should be blocked under cooldown
        second_check = risk_engine.should_dispatch_warning(sid, code, cooldown_seconds=60)
        self.assertFalse(second_check)

    # =======================================================================
    # DATABASE INTEGRATION TESTS
    # =======================================================================

    def test_compute_student_risk_profile(self):
        """Test end-to-end student risk profile synthesis from database records."""
        profile = risk_engine.compute_student_risk_profile(self.declining_student_id)
        self.assertIsNotNone(profile)

        self.assertEqual(profile["student"]["first_name"], "Karan")
        self.assertEqual(profile["risk_level"], constants.RISK_LEVEL_HIGH)
        self.assertGreaterEqual(profile["risk_score"], constants.RISK_SCORE_HIGH_THRESHOLD)


        self.assertGreater(len(profile["factors"]), 0)
        self.assertGreater(len(profile["why_explanation"]), 0)
        self.assertGreater(len(profile["recommended_actions"]), 0)
        self.assertEqual(profile["prediction"]["status"], "VALID")

    def test_class_risk_overview_aggregation(self):
        """Test aggregate classroom overview counts and primary concern identification."""
        overview = risk_engine.get_class_risk_overview(class_name="XII", section="A")
        self.assertIsNotNone(overview)

        self.assertEqual(overview["filtered_count"], 2)
        self.assertGreaterEqual(overview["total_high"], 1)
        self.assertGreaterEqual(overview["total_insufficient"], 1)
        self.assertIsInstance(overview["most_common_risk_factor"], str)


if __name__ == "__main__":
    unittest.main()
