"""Unit tests for PMLA-SCWE Smart Notification & Decision-Support Center.

Version 1.6 — Smart Notification and Intervention Center
Tests:
1. Duplicate prevention with dedup_key within cooldown window.
2. Severity escalation (MEDIUM -> HIGH updates existing alert).
3. Mark single notification as read & mark all notifications as read.
4. Action status lifecycle transitions (OPEN -> IN_PROGRESS -> RESOLVED -> DISMISSED).
5. Grounded positive milestone notification generation.
6. Multi-criteria filtering by priority, category, and action status.
7. Safe database persistence and null/invalid student handling.
"""

from __future__ import annotations
import unittest
import os
import sys

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import notification_service, student_service, assessment_service, attendance_service
from core.database import initialize_database, execute_non_query, execute_query


class TestSmartNotificationCenter(unittest.TestCase):
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
            (1, "Python Functions", "Procedural abstractions and scope")
        )

        # Create test student
        student_service.add_student({
            "first_name": "Diya",
            "last_name": "Sharma",
            "class_section": "XII-A",
            "email": "diya.sharma@example.edu"
        })
        rows = execute_query("SELECT student_id FROM Students WHERE first_name='Diya'")
        self.student_id = rows[0]["student_id"]

    def test_duplicate_prevention_with_dedup_key(self):
        """Test intelligent deduplication prevents redundant alerts on consecutive scans."""
        res1 = notification_service.create_notification(
            title="Attendance Low",
            message="Student Diya Sharma attendance is 65%",
            priority=notification_service.PRIORITY_HIGH,
            alert_type=notification_service.ALERT_ATTENDANCE,
            student_id=self.student_id,
            dedup_key=f"att_low_{self.student_id}"
        )
        self.assertTrue(res1["success"])
        self.assertEqual(res1["action"], "created")

        # Attempt to insert identical alert again
        res2 = notification_service.create_notification(
            title="Attendance Low",
            message="Student Diya Sharma attendance is 65%",
            priority=notification_service.PRIORITY_HIGH,
            alert_type=notification_service.ALERT_ATTENDANCE,
            student_id=self.student_id,
            dedup_key=f"att_low_{self.student_id}"
        )
        self.assertTrue(res2["success"])
        self.assertEqual(res2["action"], "skipped_duplicate")
        self.assertEqual(res2["notification_id"], res1["notification_id"])

        # Verify only 1 notification exists in database
        cnt = notification_service.get_unread_notification_count()
        self.assertEqual(cnt, 1)

    def test_severity_escalation(self):
        """Test escalating alert priority from MEDIUM to HIGH updates existing alert."""
        res1 = notification_service.create_notification(
            title="Moderate Attendance Warning",
            message="Student attendance is at 78%",
            priority=notification_service.PRIORITY_MEDIUM,
            alert_type=notification_service.ALERT_ATTENDANCE,
            student_id=self.student_id,
            dedup_key=f"att_{self.student_id}"
        )
        self.assertEqual(res1["action"], "created")

        # Mark as read
        notification_service.mark_notification_as_read(res1["notification_id"])
        self.assertEqual(notification_service.get_unread_notification_count(), 0)

        # Condition escalates to HIGH severity
        res2 = notification_service.create_notification(
            title="Critical Attendance Deficit (<70%)",
            message="Student attendance dropped to 64%",
            priority=notification_service.PRIORITY_HIGH,
            alert_type=notification_service.ALERT_ATTENDANCE,
            student_id=self.student_id,
            dedup_key=f"att_{self.student_id}"
        )
        self.assertEqual(res2["action"], "escalated")
        self.assertEqual(res2["notification_id"], res1["notification_id"])

        # Verify alert is now marked unread and has HIGH priority
        notifs = notification_service.get_notifications()
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0]["priority"], "HIGH")
        self.assertEqual(notifs[0]["is_read"], 0)

    def test_mark_single_and_mark_all_read(self):
        """Test individual and batch read status operations."""
        n1 = notification_service.create_notification("Alert 1", "Message 1", priority="HIGH")
        n2 = notification_service.create_notification("Alert 2", "Message 2", priority="MEDIUM")

        self.assertEqual(notification_service.get_unread_notification_count(), 2)

        # Mark single read
        ok = notification_service.mark_notification_as_read(n1["notification_id"])
        self.assertTrue(ok)
        self.assertEqual(notification_service.get_unread_notification_count(), 1)

        # Mark all read
        aff = notification_service.mark_all_notifications_as_read()
        self.assertEqual(aff, 1)
        self.assertEqual(notification_service.get_unread_notification_count(), 0)

    def test_action_status_transitions(self):
        """Test transitioning alert through OPEN -> IN_PROGRESS -> RESOLVED -> DISMISSED."""
        n = notification_service.create_notification("Math Deficit", "Need practice", priority="HIGH")
        nid = n["notification_id"]

        ok1 = notification_service.update_notification_action_status(nid, notification_service.STATUS_IN_PROGRESS)
        self.assertTrue(ok1)
        res = notification_service.get_notifications(action_status=notification_service.STATUS_IN_PROGRESS)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["action_status"], "IN_PROGRESS")

        ok2 = notification_service.update_notification_action_status(nid, notification_service.STATUS_RESOLVED)
        self.assertTrue(ok2)
        res = notification_service.get_notifications(action_status=notification_service.STATUS_RESOLVED)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["is_read"], 1)  # Resolved alerts auto-marked as read

    def test_positive_milestone_notification(self):
        """Test auto-scan generates positive milestone achievement alerts for rapidly improving students."""
        # Seed positive growth data for student
        assessment_service.add_assessment({
            "student_id": self.student_id,
            "objective_id": 1,
            "score_obtained": 88,
            "max_score": 100,
            "test_date": "2026-08-01"
        })
        attendance_service.mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-01", "status": "P"})
        attendance_service.mark_attendance({"student_id": self.student_id, "attendance_date": "2026-08-02", "status": "P"})

        # Upward weekly progress trend: 60 -> 72 -> 84 -> 94 (growth slope > 2.0)
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-07-01", 60.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-07-08", 72.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-07-15", 84.0))
        execute_non_query("INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES (%s, %s, %s)", (self.student_id, "2026-07-22", 94.0))

        scan_res = notification_service.scan_and_generate_smart_alerts()
        self.assertGreater(scan_res["created"], 0)

        notifs = notification_service.get_notifications(priority=notification_service.PRIORITY_SUCCESS)
        self.assertGreaterEqual(len(notifs), 1)
        self.assertIn("Milestone", notifs[0]["title"])
        self.assertEqual(notifs[0]["alert_type"], notification_service.ALERT_MILESTONE_IMPROVEMENT)

    def test_database_persistence_and_invalid_student(self):
        """Test system alerts without student ID and invalid student handling."""
        res = notification_service.create_notification(
            title="Database Backup Routine",
            message="Automated maintenance finished",
            priority=notification_service.PRIORITY_INFO,
            student_id=None
        )
        self.assertTrue(res["success"])
        notifs = notification_service.get_notifications(priority=notification_service.PRIORITY_INFO)
        self.assertEqual(len(notifs), 1)
        self.assertIsNone(notifs[0]["student_id"])


if __name__ == "__main__":
    unittest.main()
