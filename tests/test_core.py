"""Unit tests for the centralized PMLA-SCWE core services."""

from __future__ import annotations
import unittest
import datetime
from core import database, auth_service, student_service, attendance_service, wellness_service


class TestCoreServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize test database using SQLite fallback/MySQL transparently
        database.initialize_database()

    def setUp(self):
        # Clean up database tables for testing
        database.execute_non_query("DELETE FROM Cyber_Audit")
        database.execute_non_query("DELETE FROM Attendance")
        database.execute_non_query("DELETE FROM Students")
        database.execute_non_query("DELETE FROM Admin_Login")

        # Create test administrator
        auth_service.create_admin("admin", "admin123")

        # Create default test student
        student_data = {
            "first_name": "Test",
            "last_name": "Student",
            "class_section": "XII-A",
            "dob": "2008-05-15",
            "gender": "F",
            "email": "test@student.com",
            "phone": "9876543210"
        }
        student_service.add_student(student_data)
        res = database.execute_query("SELECT student_id FROM Students ORDER BY student_id DESC LIMIT 1")
        self.student_id = res[0]["student_id"]

    def test_authentication_pbkdf2(self):
        # Test password hashing
        password = "my_secure_password_123"
        hashed = auth_service.hash_password(password)
        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        
        # Test verification success
        self.assertTrue(auth_service.verify_password(password, hashed))
        
        # Test verification failure
        self.assertFalse(auth_service.verify_password("incorrect_password", hashed))

        # Test login
        self.assertTrue(auth_service.login("admin", "admin123"))
        self.assertFalse(auth_service.login("admin", "wrongpassword"))

    def test_student_crud(self):
        # Register student
        payload = {
            "first_name": "Vedant",
            "last_name": "Sharma",
            "class_section": "XII-B",
            "dob": "2009-02-12",
            "gender": "M",
            "email": "vedant@sharma.com",
            "phone": "9999000011"
        }
        self.assertTrue(student_service.add_student(payload))
        
        # Search student
        res = student_service.search_students("Vedant")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["last_name"], "Sharma")
        self.assertEqual(res[0]["class_section"], "XII-B")

        # Update student
        sid = res[0]["student_id"]
        payload["first_name"] = "Vedant (Updated)"
        self.assertTrue(student_service.update_student(sid, payload))
        
        updated_res = student_service.search_students(str(sid))
        self.assertEqual(updated_res[0]["first_name"], "Vedant (Updated)")

        # Delete student
        self.assertTrue(student_service.delete_student(sid))
        self.assertEqual(len(student_service.search_students(str(sid))), 0)

    def test_attendance_service(self):
        date_str = datetime.date.today().isoformat()
        
        # Mark single attendance row
        self.assertTrue(attendance_service.mark_attendance({
            "student_id": self.student_id,
            "attendance_date": date_str,
            "status": "Present"
        }))
        
        # Fetch class attendance registry status
        status_map = attendance_service.get_attendance_for_date_and_class(date_str, "XII-A")
        self.assertEqual(status_map.get(self.student_id), "Present")

        # Bulk save attendance upsert
        records = {self.student_id: "Absent"}
        self.assertTrue(attendance_service.save_attendance(date_str, "XII-A", records))
        
        new_status_map = attendance_service.get_attendance_for_date_and_class(date_str, "XII-A")
        self.assertEqual(new_status_map.get(self.student_id), "Absent")

        # Percentage rate computation
        pct = attendance_service.calculate_attendance_percentage(self.student_id)
        self.assertEqual(pct, 0.0) # since status was changed to Absent

    def test_wellness_calculations(self):
        # Ideal scenario
        data_ideal = {
            "sleep_duration": 8.0,
            "recreational_screen_time": 1.5,
            "digital_distraction_level": 1,
            "cyber_safety_awareness": 5
        }
        score = wellness_service.calculate_wellness_score(data_ideal)
        self.assertEqual(score, 100.0)

        # Concern scenario
        # sleep = 6.0 -> 85
        # rec_screen = 4.0 -> 70
        # distraction = 3 -> 50
        # safety = 3 -> 60
        # Avg: (85+70+50+60)/4 = 66.25
        data_concern = {
            "sleep_duration": 6.0,
            "recreational_screen_time": 4.0,
            "digital_distraction_level": 3,
            "cyber_safety_awareness": 3
        }
        score_concern = wellness_service.calculate_wellness_score(data_concern)
        self.assertEqual(score_concern, 66.25)

    def test_wellness_validations(self):
        # Invalid data validation checks
        payload_invalid = {
            "student_id": 999999,  # Non-existent ID
            "daily_screen_time": 10.0,
            "study_screen_time": 4.0,
            "recreational_screen_time": 4.0, # sum mismatch: 4+4 != 10
            "sleep_duration": 25.0, # out of range hours
            "digital_distraction_level": 6, # out of range index
            "cyber_safety_awareness": 0 # out of range index
        }
        errors = wellness_service.validate_audit_data(payload_invalid)
        self.assertTrue(len(errors) >= 5)


if __name__ == "__main__":
    unittest.main()
