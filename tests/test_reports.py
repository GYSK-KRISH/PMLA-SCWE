"""Unit tests for PMLA-SCWE Professional Report Generation Engine.

Version 1.5 — Professional Report Generation Engine
Tests:
1. Valid student PDF report generation
2. Missing student ID graceful handling
3. Student with limited/zero initial data PDF generation
4. Class-wide performance PDF report generation
5. CSV data export for individual and class reports
6. Live report preview text generator
7. Deterministic report generation when AI is offline
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import report_service, reports
from core.database import initialize_database, execute_non_query, execute_query
from core.student_service import add_student
from core.assessment_service import add_assessment
from core.attendance_service import mark_attendance


class TestReportService(unittest.TestCase):
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
            (1, "Linear Regression", "Mathematical foundations of predictive learning models")
        )

        # 1. Complete Student Fixture
        add_student({
            "first_name": "Rohan",
            "last_name": "Verma",
            "class_section": "XII-A",
            "email": "rohan.verma@example.edu"
        })
        rows_1 = execute_query("SELECT student_id FROM Students WHERE first_name='Rohan'")
        self.student_id_1 = rows_1[0]["student_id"]

        add_assessment({
            "student_id": self.student_id_1,
            "objective_id": 1,
            "score_obtained": 78,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-01", "status": "P"})
        mark_attendance({"student_id": self.student_id_1, "attendance_date": "2026-08-02", "status": "P"})

        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id_1, "2026-08-01", 70.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id_1, "2026-08-08", 78.0))

        # 2. Minimal / Zero Data Student Fixture
        add_student({
            "first_name": "Neha",
            "last_name": "Gupta",
            "class_section": "XII-B",
            "email": "neha.gupta@example.edu"
        })
        rows_2 = execute_query("SELECT student_id FROM Students WHERE first_name='Neha'")
        self.student_id_2 = rows_2[0]["student_id"]

    def test_valid_student_pdf_generation(self):
        """Test individual student PDF report generation produces a valid non-empty file."""
        out_path = "reports/test_student_rohan.pdf"
        if os.path.exists(out_path):
            os.remove(out_path)

        res_path = report_service.generate_student_pdf_report(
            student_id=self.student_id_1,
            output_path=out_path,
            options={"include_ai_summary": True, "include_charts": True}
        )

        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 5000)  # > 5 KB valid PDF

    def test_missing_student_handling(self):
        """Test querying non-existent student raises a clean ValueError."""
        with self.assertRaises(ValueError):
            report_service.generate_student_pdf_report(student_id=99999)

    def test_student_with_limited_data_pdf_generation(self):
        """Test newly enrolled student with zero analytical history still generates safe PDF."""
        out_path = "reports/test_student_neha_minimal.pdf"
        if os.path.exists(out_path):
            os.remove(out_path)

        res_path = report_service.generate_student_pdf_report(
            student_id=self.student_id_2,
            output_path=out_path
        )
        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 2000)

    def test_class_pdf_generation(self):
        """Test class-wide performance PDF generation."""
        out_path = "reports/test_class_xii_report.pdf"
        if os.path.exists(out_path):
            os.remove(out_path)

        res_path = report_service.generate_class_pdf_report(
            class_name="XII",
            section="A",
            output_path=out_path,
            options={"include_charts": True}
        )
        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 5000)

    def test_csv_export_student_and_class(self):
        """Test CSV export for student and class cohorts."""
        student_csv = report_service.export_report_csv(
            report_type=report_service.REPORT_TYPE_STUDENT_INTELLIGENCE,
            student_id=self.student_id_1,
            output_path="reports/test_student.csv"
        )
        self.assertTrue(os.path.exists(student_csv))
        with open(student_csv, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Rohan", content)
            self.assertIn("Academic Average", content)

        class_csv = report_service.export_report_csv(
            report_type=report_service.REPORT_TYPE_CLASS_PERFORMANCE,
            class_name="All",
            section="All",
            output_path="reports/test_class.csv"
        )
        self.assertTrue(os.path.exists(class_csv))
        with open(class_csv, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("PMLA-SCWE CLASSROOM PERFORMANCE REPORT", content)
            self.assertIn("Student ID", content)

    def test_report_preview_text(self):
        """Test formatted Markdown live preview text generation."""
        preview = report_service.generate_report_preview_text(
            report_type=report_service.REPORT_TYPE_STUDENT_INTELLIGENCE,
            student_id=self.student_id_1
        )
        self.assertIn("PMLA-SCWE STUDENT INTELLIGENCE REPORT", preview)
        self.assertIn("Rohan", preview)
        self.assertIn("Executive Summary", preview)
        self.assertIn("NOTICE:", preview)

    def test_legacy_facade_compatibility(self):
        """Test legacy core.reports exports function properly."""
        summary = reports.get_class_summary_data()
        self.assertIn("total_students", summary)
        self.assertIn("risk_distribution", summary)

        csv_path = reports.export_class_report_csv()
        self.assertTrue(os.path.exists(csv_path))


if __name__ == "__main__":
    unittest.main()
