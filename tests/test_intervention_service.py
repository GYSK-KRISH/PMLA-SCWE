"""Unit tests for PMLA-SCWE Teacher Intervention Tracking & Outcome Intelligence.

Version 1.6 — Intervention Tracking & Outcome Intelligence
Tests:
1. Create intervention with automatic baseline metric snapshot.
2. Status transitions (PENDING -> IN_PROGRESS -> ESCALATED).
3. Outcome evaluation with positive recovery deltas and Highly Effective tier.
4. Outcome evaluation with flat/declining metrics and Needs Review tier.
5. Student 360 profile integration with recorded interventions and timeline events.
6. Cohort intervention metrics aggregation and resolution rate calculation.
7. Deletion of intervention records.
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import intervention_service, intervention_analytics, student_profile_service
from core.database import initialize_database, execute_non_query, execute_query
from core.student_service import add_student
from core.assessment_service import add_assessment
from core.attendance_service import mark_attendance


class TestInterventionService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def setUp(self):
        """Seed clean student test fixture."""
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
            (1, "Algebraic Equations", "Core polynomial and quadratic problem sets")
        )

        # Create test student (Karan Mehta)
        add_student({
            "first_name": "Karan",
            "last_name": "Mehta",
            "class_section": "XII-A",
            "email": "karan.mehta@example.edu"
        })
        rows = execute_query("SELECT student_id FROM Students WHERE first_name='Karan'")
        self.student_id = rows[0]["student_id"]

        add_assessment({
            "student_id": self.student_id,
            "objective_id": 1,
            "score_obtained": 48,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-01", "status": "P"})
        mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-02", "status": "A"})
        mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-03", "status": "A"})
        mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-04", "status": "P"})

        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-08-01", 50.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-08-08", 48.0))

    def test_create_intervention_with_baseline_snapshot(self):
        """Test intervention creation automatically captures baseline metrics."""
        res = intervention_service.create_intervention(
            student_id=self.student_id,
            title="1-on-1 Algebra Remedial Sessions",
            risk_factor="Low Mathematics Score (48%)",
            action_type="Remedial Practice",
            priority="HIGH",
            target_date="2026-09-01",
            teacher_notes="Schedule 30-min tutoring twice weekly."
        )

        self.assertTrue(res["success"])
        self.assertIsNotNone(res["intervention_id"])
        self.assertEqual(res["status"], "PENDING")

        iv = intervention_service.get_intervention_by_id(res["intervention_id"])
        self.assertIsNotNone(iv)
        self.assertEqual(iv["title"], "1-on-1 Algebra Remedial Sessions")
        self.assertEqual(iv["priority"], "HIGH")
        self.assertAlmostEqual(iv["pre_academic_score"], 48.0, places=1)
        self.assertAlmostEqual(iv["pre_attendance_rate"], 50.0, places=1)

    def test_update_intervention_status(self):
        """Test lifecycle status transitions."""
        res = intervention_service.create_intervention(
            student_id=self.student_id,
            title="Attendance Pacing Check-in",
            risk_factor="Low Attendance"
        )
        iv_id = res["intervention_id"]

        ok1 = intervention_service.update_intervention_status(iv_id, "IN_PROGRESS", "Student attended first check-in.")
        self.assertTrue(ok1)
        iv1 = intervention_service.get_intervention_by_id(iv_id)
        self.assertEqual(iv1["status"], "IN_PROGRESS")
        self.assertIn("first check-in", iv1["teacher_notes"])

        ok2 = intervention_service.update_intervention_status(iv_id, "ESCALATED")
        self.assertTrue(ok2)
        iv2 = intervention_service.get_intervention_by_id(iv_id)
        self.assertEqual(iv2["status"], "ESCALATED")

    def test_evaluate_intervention_outcome_positive(self):
        """Test outcome evaluation with positive recovery metrics."""
        res = intervention_service.create_intervention(
            student_id=self.student_id,
            title="Intensive Problem Set Revision",
            risk_factor="Low Diagnostics",
            priority="HIGH"
        )
        iv_id = res["intervention_id"]

        # Simulate post-intervention score improvements
        post_overrides = {
            "risk_score": 32.0,       # Risk reduced from ~75 to 32 (-43 pts)
            "academic_score": 72.0,   # Academic improved from 48% to 72% (+24%)
            "attendance_rate": 85.0,  # Attendance improved from 50% to 85% (+35%)
            "lhs_score": 74.0         # LHS improved from ~48 to 74 (+26 pts)
        }

        eval_res = intervention_service.evaluate_intervention_outcome(
            intervention_id=iv_id,
            teacher_notes="Student mastered polynomial factoring. Marked improvement.",
            post_metrics_override=post_overrides
        )

        self.assertTrue(eval_res["success"])
        self.assertGreaterEqual(eval_res["effectiveness_score"], 60.0)
        self.assertIn(eval_res["effectiveness_tier"], (
            intervention_analytics.TIER_HIGHLY_EFFECTIVE,
            intervention_analytics.TIER_EFFECTIVE
        ))
        self.assertGreater(eval_res["deltas"]["academic"], 0)
        self.assertGreater(eval_res["deltas"]["risk"], 0)

        # Verify persisted state
        iv = intervention_service.get_intervention_by_id(iv_id)
        self.assertEqual(iv["status"], "COMPLETED")
        self.assertIsNotNone(iv["completed_date"])
        self.assertAlmostEqual(iv["post_academic_score"], 72.0, places=1)

    def test_evaluate_intervention_outcome_needs_review(self):
        """Test outcome evaluation when student metrics do not improve."""
        res = intervention_service.create_intervention(
            student_id=self.student_id,
            title="Screen Time Habit Pacing",
            risk_factor="Digital Distraction"
        )
        iv_id = res["intervention_id"]

        # Simulate non-improving metrics
        post_overrides = {
            "risk_score": 80.0,
            "academic_score": 44.0,
            "attendance_rate": 45.0,
            "lhs_score": 40.0
        }

        eval_res = intervention_service.evaluate_intervention_outcome(
            intervention_id=iv_id,
            teacher_notes="Deficit persisted. Recommending parent conference.",
            post_metrics_override=post_overrides
        )

        self.assertTrue(eval_res["success"])
        self.assertEqual(eval_res["effectiveness_tier"], intervention_analytics.TIER_NEEDS_REVIEW)
        self.assertLess(eval_res["effectiveness_score"], 25.0)

    def test_student_profile_integration(self):
        """Test Student 360 profile contains recorded interventions and timeline history."""
        intervention_service.create_intervention(
            student_id=self.student_id,
            title="Math Coaching",
            risk_factor="Low Test Score"
        )

        profile = student_profile_service.get_student_360_profile(self.student_id)
        self.assertIn("recorded_interventions", profile)
        self.assertEqual(len(profile["recorded_interventions"]), 1)
        self.assertEqual(profile["recorded_interventions"][0]["title"], "Math Coaching")

        # Verify timeline events
        timeline_types = [t["type"] for t in profile["timeline"]]
        self.assertIn("intervention", timeline_types)

    def test_cohort_intervention_analytics_aggregation(self):
        """Test classroom cohort aggregation metrics."""
        # Create 2 interventions
        res1 = intervention_service.create_intervention(student_id=self.student_id, title="Action 1", risk_factor="Risk 1")
        res2 = intervention_service.create_intervention(student_id=self.student_id, title="Action 2", risk_factor="Risk 2")

        # Complete Action 1 with positive results
        intervention_service.evaluate_intervention_outcome(
            intervention_id=res1["intervention_id"],
            post_metrics_override={"risk_score": 25.0, "academic_score": 80.0, "attendance_rate": 90.0, "lhs_score": 80.0}
        )

        all_ivs = intervention_service.get_all_interventions()
        agg = intervention_analytics.aggregate_cohort_intervention_metrics(all_ivs)

        self.assertEqual(agg["total_interventions"], 2)
        self.assertEqual(agg["active_count"], 1)
        self.assertEqual(agg["completed_count"], 1)
        self.assertEqual(agg["resolution_rate"], 100.0)

    def test_delete_intervention(self):
        """Test deletion of an intervention record."""
        res = intervention_service.create_intervention(student_id=self.student_id, title="To Delete", risk_factor="None")
        iv_id = res["intervention_id"]

        ok = intervention_service.delete_intervention(iv_id)
        self.assertTrue(ok)
        self.assertIsNone(intervention_service.get_intervention_by_id(iv_id))


if __name__ == "__main__":
    unittest.main()
