"""Test script for Cyber-Wellness Audit Stage 1 functionality."""

import sys
from datetime import date
from PMLA_SCWE import database, student, cyber_audit


def run_tests():
    print("=== Initializing Test DB ===")
    database.initialize_database_from_file("schema.sql")
    
    # Ensure we have at least one test student
    db_students = database.execute_select("SELECT student_id FROM Students LIMIT 1")
    if db_students:
        student_id = db_students[0]["student_id"]
    else:
        student.add_student({
            "first_name": "Test",
            "last_name": "Student",
            "class_section": "12-A",
            "dob": "2008-01-01",
            "gender": "M",
            "email": "test@student.com",
            "phone": "1234567890"
        })
        db_students = database.execute_select("SELECT student_id FROM Students ORDER BY student_id DESC LIMIT 1")
        student_id = db_students[0]["student_id"]

    print(f"Using student_id={student_id} for tests.")

    # 1. Test Wellness Score Calculations
    print("\n--- 1. Testing wellness score calculation ---")
    
    # Case A: Perfect score
    data_perfect = {
        "sleep_duration": 8.0,
        "recreational_screen_time": 1.5,
        "digital_distraction_level": 1,
        "cyber_safety_awareness": 5
    }
    score_perfect = cyber_audit.calculate_wellness_score(data_perfect)
    print(f"Perfect case score (Expected: 100.0): {score_perfect}")
    assert score_perfect == 100.0, f"Expected 100.0, got {score_perfect}"
    
    # Case B: Mixed score
    # sleep_duration = 6.0 -> sleep_score = 100 - (7 - 6) * 15 = 85
    # recreational_screen_time = 4.0 -> rec_score = 100 - (4 - 2) * 15 = 70
    # digital_distraction_level = 3 -> distraction_score = (5 - 3) * 25 = 50
    # cyber_safety_awareness = 3 -> safety_score = 3 * 20 = 60
    # Expected: (85 + 70 + 50 + 60) / 4 = 66.25
    data_mixed = {
        "sleep_duration": 6.0,
        "recreational_screen_time": 4.0,
        "digital_distraction_level": 3,
        "cyber_safety_awareness": 3
    }
    score_mixed = cyber_audit.calculate_wellness_score(data_mixed)
    print(f"Mixed case score (Expected: 66.25): {score_mixed}")
    assert score_mixed == 66.25, f"Expected 66.25, got {score_mixed}"
    
    # 2. Test Input Validation
    print("\n--- 2. Testing data validation ---")
    
    # Valid data
    valid_data = {
        "student_id": student_id,
        "daily_screen_time": 5.0,
        "study_screen_time": 3.0,
        "recreational_screen_time": 2.0,
        "sleep_duration": 8.0,
        "digital_distraction_level": 2,
        "cyber_safety_awareness": 4
    }
    errors = cyber_audit.validate_audit_data(valid_data)
    print(f"Valid data errors (Expected: []): {errors}")
    assert len(errors) == 0, f"Expected no errors, got {errors}"
    
    # Invalid student
    invalid_student_data = valid_data.copy()
    invalid_student_data["student_id"] = 999999
    errors = cyber_audit.validate_audit_data(invalid_student_data)
    print(f"Non-existent student errors: {errors}")
    assert any("does not exist" in e or "Student ID" in e for e in errors), "Expected non-existent student error"

    # Daily screen time sum mismatch
    mismatch_screen = valid_data.copy()
    mismatch_screen["daily_screen_time"] = 10.0 # study=3, rec=2, daily=10 is mismatch
    errors = cyber_audit.validate_audit_data(mismatch_screen)
    print(f"Mismatch screen time errors: {errors}")
    assert any("Daily screen time must equal" in e for e in errors), "Expected mismatch screen error"
    
    # Out of range values
    out_of_range = valid_data.copy()
    out_of_range["sleep_duration"] = -5.0
    out_of_range["digital_distraction_level"] = 6
    errors = cyber_audit.validate_audit_data(out_of_range)
    print(f"Out of range errors: {errors}")
    assert len(errors) >= 2, f"Expected sleep and distraction errors, got {errors}"

    # 3. Test Database Insertion
    print("\n--- 3. Testing database insertion ---")
    
    # Remove existing audits for this student first to start clean
    database.execute_non_query("DELETE FROM Cyber_Audit WHERE student_id = %s", (student_id,))
    
    audit_data_to_add = {
        "student_id": student_id,
        "daily_screen_time": 6.5,
        "study_screen_time": 3.5,
        "recreational_screen_time": 3.0,
        "sleep_duration": 7.5,
        "digital_distraction_level": 2,
        "cyber_safety_awareness": 4,
        "remarks": "Feeling good, slightly distracted",
        "audit_date": date.today().isoformat()
    }
    
    # Expected score:
    # sleep = 7.5 (100)
    # recreational = 3.0 -> 100 - (3.0 - 2.0)*15 = 85
    # distraction = 2 -> (5 - 2)*25 = 75
    # safety = 4 -> 4*20 = 80
    # Expected: (100 + 85 + 75 + 80) / 4 = 85.0
    
    inserted = cyber_audit.add_cyber_audit(audit_data_to_add)
    print(f"Insertion result (Expected: True): {inserted}")
    assert inserted is True, "Database insertion failed"

    # 4. Test Audit History & Latest Retrieval
    print("\n--- 4. Testing history and latest retrieval ---")
    
    history = cyber_audit.get_student_audits(student_id)
    print(f"Audit History count (Expected: 1): {len(history)}")
    assert len(history) == 1, f"Expected 1 history record, got {len(history)}"
    assert history[0]["wellness_score"] == 85.0, f"Expected wellness score 85.0, got {history[0]['wellness_score']}"
    assert history[0]["daily_screen_time"] == 6.5
    assert history[0]["remarks"] == "Feeling good, slightly distracted"
    
    latest = cyber_audit.get_latest_audit(student_id)
    assert latest is not None, "Latest audit returned None"
    print(f"Latest wellness score retrieved (Expected: 85.0): {latest['wellness_score']}")
    assert latest["wellness_score"] == 85.0
    
    print("\n=== ALL TESTS PASSED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_tests()
