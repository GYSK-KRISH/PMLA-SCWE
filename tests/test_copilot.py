"""Unit tests for PMLA-SCWE AI Teacher Copilot and Decision Support Engine.

Version 1.4 — AI Teacher Copilot
Tests:
1. Gemini provider completion success
2. OpenAI provider completion success
3. Automatic provider fallback (Gemini fails -> OpenAI succeeds)
4. Both providers unavailable -> Deterministic offline rule-based engine
5. Explain student risk action (4 structured sections)
6. Study plan generation (7, 14, 30 days)
7. Identify weak topics action
8. Generate intervention plan action (Teacher review required)
9. Class performance summary action
10. Compare two students action (Constructive comparison)
11. Draft parent-friendly progress summary action
12. Suggest teacher follow-up actions action
13. Missing student ID graceful handling
14. Free-form copilot inquiry and backward-compatible ai_assistant facade
"""

from __future__ import annotations
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import ai, ai_assistant
from core.database import initialize_database, execute_non_query, execute_query
from core.student_service import add_student
from core.assessment_service import add_assessment
from core.attendance_service import mark_attendance


class TestAITeacherCopilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def setUp(self):
        """Seed clean test student fixture."""
        execute_non_query("DELETE FROM Diagnostic_Logs")
        execute_non_query("DELETE FROM Attendance")
        execute_non_query("DELETE FROM Cyber_Audit")
        execute_non_query("DELETE FROM Weekly_Progress")
        execute_non_query("DELETE FROM Learning_Objectives")
        execute_non_query("DELETE FROM Students")

        # Create learning objective
        execute_non_query(
            "INSERT INTO Learning_Objectives (objective_id, topic_name, description) VALUES (%s, %s, %s)",
            (1, "Data Structures", "Lists, Tuples, Dictionaries in Python")
        )

        # Create Student 1 (Aarav Sharma)
        add_student({
            "first_name": "Aarav",
            "last_name": "Sharma",
            "class_section": "XII-A",
            "email": "aarav.sharma@example.edu"
        })
        rows_1 = execute_query("SELECT student_id FROM Students WHERE first_name='Aarav'")
        self.student_id_1 = rows_1[0]["student_id"]

        add_assessment({
            "student_id": self.student_id_1,
            "objective_id": 1,
            "score_obtained": 52,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-01", "status": "P"})
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-02", "status": "A"})
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-03", "status": "P"})
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-04", "status": "P"})

        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id_1, "2026-08-01", 60.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id_1, "2026-08-08", 55.0))

        # Create Student 2 (Diya Patel)
        add_student({
            "first_name": "Diya",
            "last_name": "Patel",
            "class_section": "XII-A",
            "email": "diya.patel@example.edu"
        })
        rows_2 = execute_query("SELECT student_id FROM Students WHERE first_name='Diya'")
        self.student_id_2 = rows_2[0]["student_id"]

        add_assessment({
            "student_id": self.student_id_2,
            "objective_id": 1,
            "score_obtained": 88,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        mark_attendance({"student_id": self.student_id_2, "attendance_date": "2026-08-01", "status": "P"})
        mark_attendance({"student_id": self.student_id_2, "attendance_date": "2026-08-02", "status": "P"})

    # =======================================================================
    # PROVIDER & FALLBACK TESTS
    # =======================================================================

    @patch("core.ai.provider_manager.call_gemini")
    def test_gemini_success(self, mock_gemini):
        """Test successful completion using Google Gemini."""
        mock_gemini.return_value = "### SUMMARY\nStudent is performing well."
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "fake_gemini_key", "OPENAI_API_KEY": ""}):
            res = ai.provider_manager.execute_ai_completion("System prompt", "User prompt")
            self.assertTrue(res["success"])
            self.assertEqual(res["provider"], "gemini")
            self.assertIn("Student is performing well", res["response"])
            self.assertFalse(res["fallback_used"])
            self.assertFalse(res["is_offline_fallback"])

    @patch("core.ai.provider_manager.call_openai")
    def test_openai_success(self, mock_openai):
        """Test successful completion using OpenAI."""
        mock_openai.return_value = "### SUMMARY\nStudent requires remedial practice."
        with patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake_openai_key", "GEMINI_API_KEY": ""}):
            res = ai.provider_manager.execute_ai_completion("System prompt", "User prompt")
            self.assertTrue(res["success"])
            self.assertEqual(res["provider"], "openai")
            self.assertIn("Student requires remedial practice", res["response"])
            self.assertFalse(res["fallback_used"])

    @patch("core.ai.provider_manager.call_openai")
    @patch("core.ai.provider_manager.call_gemini")
    def test_fallback_behavior(self, mock_gemini, mock_openai):
        """Test automated fallback when preferred provider (Gemini) fails and secondary (OpenAI) succeeds."""
        mock_gemini.side_effect = Exception("Gemini quota exceeded")
        mock_openai.return_value = "OpenAI fallback response."

        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "fake_gemini", "OPENAI_API_KEY": "fake_openai"}):
            res = ai.provider_manager.execute_ai_completion("System prompt", "User prompt")
            self.assertTrue(res["success"])
            self.assertEqual(res["provider"], "openai")
            self.assertTrue(res["fallback_used"])
            self.assertIn("OpenAI fallback response", res["response"])

    def test_both_providers_unavailable_activates_deterministic_engine(self):
        """Test that when cloud AI is unconfigured or unavailable, the deterministic offline engine responds."""
        with patch.dict(os.environ, {"AI_PROVIDER": "auto", "GEMINI_API_KEY": "", "OPENAI_API_KEY": ""}):
            res = ai.explain_student_risk(self.student_id_1)
            self.assertTrue(res["success"])
            self.assertTrue(res["is_offline_fallback"])
            self.assertIn("DETERMINISTIC OFFLINE ENGINE ACTIVE", res["response"])
            self.assertIn("EXECUTIVE SUMMARY", res["response"])
            self.assertIn("MAIN CONTRIBUTING FACTORS", res["response"])

    # =======================================================================
    # 8 PREDEFINED COPILOT ACTIONS TESTS
    # =======================================================================

    def test_explain_risk_action(self):
        """Test Explain Student Risk generates structured 4 sections."""
        res = ai.explain_student_risk(self.student_id_1)
        self.assertTrue(res["success"])
        self.assertIn("EXECUTIVE SUMMARY", res["response"])
        self.assertIn("MAIN CONTRIBUTING FACTORS", res["response"])
        self.assertIn("WHAT THE DATA SHOWS", res["response"])
        self.assertIn("RECOMMENDED NEXT STEPS", res["response"])

    def test_study_plan_durations(self):
        """Test Study Plan generation across 7, 14, and 30 days."""
        for duration in (7, 14, 30):
            res = ai.create_study_plan(self.student_id_1, duration_days=duration)
            self.assertTrue(res["success"])
            self.assertIn(f"{duration}-DAY", res["response"].upper())
            self.assertIn("SCHEDULE & MILESTONES", res["response"].upper())

    def test_weak_topics_action(self):
        """Test Identify Weak Topics action."""
        res = ai.identify_weak_topics(self.student_id_1)
        self.assertTrue(res["success"])
        self.assertIn("CRITICAL LEARNING GAPS", res["response"])
        self.assertIn("EVIDENCE FROM ASSESSMENTS", res["response"])
        self.assertIn("TARGETED REMEDIAL STRATEGIES", res["response"])

    def test_generate_intervention_plan_action(self):
        """Test Generate Intervention Plan produces unconfirmed draft with advisory warning."""
        res = ai.generate_intervention_plan(self.student_id_1)
        self.assertTrue(res["success"])
        self.assertIn("INTERVENTION PLAN", res["response"])
        self.assertIn("TEACHER REVIEW REQUIRED", res["response"])
        self.assertIn("EVIDENCE BASE", res["response"])

    def test_class_summary_action(self):
        """Test Class Performance Summary action."""
        res = ai.summarize_class_performance()
        self.assertTrue(res["success"])
        self.assertIn("CLASSROOM", res["response"].upper())
        self.assertIn("RISK", res["response"].upper())

    def test_compare_two_students_action(self):
        """Test Compare Two Students produces constructive side-by-side matrix."""
        res = ai.compare_two_students(self.student_id_1, self.student_id_2)
        self.assertTrue(res["success"])
        self.assertIn("COMPARATIVE", res["response"].upper())
        self.assertIn("Aarav", res["response"])
        self.assertIn("Diya", res["response"])

    def test_parent_summary_action(self):
        """Test Draft Parent Progress Letter generates formal communication draft."""
        res = ai.draft_parent_summary(self.student_id_1)
        self.assertTrue(res["success"])
        self.assertIn("Dear Parent", res["response"])
        self.assertIn("Aarav", res["response"])
        self.assertIn("Warm regards", res["response"])

    def test_suggest_teacher_actions(self):
        """Test Suggest Teacher Actions produces prioritized checklist."""
        res = ai.suggest_teacher_actions(self.student_id_1)
        self.assertTrue(res["success"])
        self.assertIn("ACTION CHECKLIST", res["response"].upper())
        self.assertIn("IMMEDIATE ACTIONS", res["response"].upper())

    # =======================================================================
    # SAFETY & ERROR HANDLING TESTS
    # =======================================================================

    def test_missing_student_handling(self):
        """Test querying non-existent student ID returns clean, graceful notice."""
        res = ai.explain_student_risk(99999)
        self.assertFalse(res["success"])
        self.assertIn("not found", res["response"].lower())

    def test_empty_query_handling(self):
        """Test free-form ask_copilot handles empty strings safely."""
        res = ai.ask_copilot("   ")
        self.assertFalse(res["success"])

    def test_facade_backward_compatibility(self):
        """Test that legacy ai_assistant.ask_ai and get_ai_status work seamlessly."""
        status = ai_assistant.get_ai_status()
        self.assertIn("status", status)
        self.assertIn("active_provider", status)

        legacy_res = ai_assistant.ask_ai("What are the recommendations for student 1?")
        self.assertTrue(legacy_res["success"])


if __name__ == "__main__":
    unittest.main()
