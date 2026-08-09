"""Bulk sample-data seeding for PMLA-SCWE.

This module inserts 100 student records and related rows into the active
database using a single connection so it works quickly with both MySQL and
the SQLite fallback.
"""

from __future__ import annotations

from datetime import date, timedelta
from random import Random
import sqlite3

from .authentication import _hash_password
from .database import execute_select, get_connection, initialize_database_from_file

SEED_USERNAME = "admin"
SEED_PASSWORD = "admin123"

FIRST_NAMES = [
    "Aarav", "Aanya", "Aditya", "Anika", "Arjun", "Diya", "Ishaan", "Kavya", "Karan", "Meera",
    "Nikhil", "Navya", "Rahul", "Riya", "Rohan", "Sana", "Vihaan", "Ananya", "Kabir", "Priya",
]

LAST_NAMES = [
    "Sharma", "Singh", "Verma", "Gupta", "Patel", "Khan", "Mehta", "Rao", "Yadav", "Iyer",
]

CLASSES = ["XII-A", "XII-B", "XI-A", "XI-B", "X-A", "X-B"]
TOPICS = [
    "Pandas Basics",
    "SQL SELECT",
    "SQL JOIN",
    "Data Visualization",
    "Cyber Safety",
    "Python Functions",
    "Digital Wellness",
    "Spreadsheet Skills",
    "AI Literacy",
    "Ethics in Technology",
]

ACHIEVEMENT_BADGES = [
    "Consistent Learner",
    "Cyber Safe",
    "Quiz Ace",
    "Attendance Star",
]


def _count_rows(table: str) -> int:
    rows = execute_select(f"SELECT COUNT(*) AS cnt FROM {table}")
    return int(rows[0].get("cnt", 0)) if rows else 0


def _placeholder(conn) -> str:
    return "?" if isinstance(conn, sqlite3.Connection) else "%s"


def _ensure_admin(cursor, placeholder: str) -> None:
    cursor.execute("SELECT COUNT(*) AS cnt FROM Admin_Login")
    count = int(cursor.fetchone()[0])
    if count == 0:
        cursor.execute(
            f"INSERT INTO Admin_Login (username, password_hash) VALUES ({placeholder}, {placeholder})",
            (SEED_USERNAME, _hash_password(SEED_PASSWORD)),
        )


def _ensure_objectives(cursor, placeholder: str) -> None:
    cursor.execute("SELECT COUNT(*) AS cnt FROM Learning_Objectives")
    count = int(cursor.fetchone()[0])
    if count > 0:
        return
    for topic in TOPICS:
        cursor.execute(
            f"INSERT INTO Learning_Objectives (topic_name, description) VALUES ({placeholder}, {placeholder})",
            (topic, f"Introductory coverage for {topic.lower()}"),
        )


def _fetch_ids(cursor, table: str, column: str) -> set[int]:
    cursor.execute(f"SELECT {column} FROM {table}")
    return {int(row[0]) for row in cursor.fetchall()}


def seed_database(target_students: int = 100) -> dict[str, int]:
    """Wipes the database, resets AUTO_INCREMENT, and seeds exactly target_students with rich profiles."""
    initialize_database_from_file("schema.sql")

    conn = get_connection()
    placeholder = _placeholder(conn)
    cursor = conn.cursor()
    rng = Random(42)

    try:
        # Disable foreign keys and wipe all tables to reset AUTO_INCREMENT to 1
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        except Exception:
            pass
            
        tables = [
            "Attendance", "Diagnostic_Logs", "Weekly_Progress", "Cyber_Audit", 
            "Achievements", "Activity_Log", "Reports_Metadata", "Students", "Admin_Login", "Learning_Objectives"
        ]
        for t in tables:
            cursor.execute(f"DELETE FROM {t}")
            try:
                cursor.execute(f"ALTER TABLE {t} AUTO_INCREMENT = 1")
            except Exception:
                pass
                
        try:
            cursor.execute("DELETE FROM sqlite_sequence")
        except Exception:
            pass
            
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except Exception:
            pass

        _ensure_admin(cursor, placeholder)
        _ensure_objectives(cursor, placeholder)

        student_sql = (
            f"INSERT INTO Students (first_name, last_name, class_section, dob, gender, email, phone, enrollment_date) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )

        for offset in range(target_students):
            number = offset + 1
            first_name = FIRST_NAMES[offset % len(FIRST_NAMES)]
            last_name = LAST_NAMES[offset % len(LAST_NAMES)]
            class_section = CLASSES[offset % len(CLASSES)]
            dob = date(2007, 1, 1) + timedelta(days=(number * 11) % 365)
            gender = ["M", "F", "O"][offset % 3]
            email = f"student{number:03d}@example.com"
            phone = f"99990{number:05d}"[-10:]
            enrollment_date = date.today() - timedelta(days=rng.randint(0, 180))

            cursor.execute(
                student_sql,
                (
                    first_name,
                    last_name,
                    class_section,
                    dob.isoformat(),
                    gender,
                    email,
                    phone,
                    enrollment_date.isoformat(),
                ),
            )

        conn.commit()

        # Build lookup tables for related rows.
        cursor.execute("SELECT student_id FROM Students ORDER BY student_id")
        student_ids = [int(row[0]) for row in cursor.fetchall()]
        cursor.execute("SELECT objective_id FROM Learning_Objectives ORDER BY objective_id")
        objective_ids = [int(row[0]) for row in cursor.fetchall()]

        assessment_sql = (
            f"INSERT INTO Diagnostic_Logs (student_id, objective_id, score_obtained, max_score, test_date, time_taken_minutes) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )
        attendance_sql = (
            f"INSERT INTO Attendance (student_id, attendance_date, status) VALUES ({placeholder}, {placeholder}, {placeholder})"
        )
        audit_sql = (
            f"INSERT INTO Cyber_Audit (student_id, password_strength, screen_time_hours, netiquette_score, privacy_awareness, e_waste_awareness, wellness_score, audit_date) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )
        progress_sql = (
            f"INSERT INTO Weekly_Progress (student_id, week_start, score) VALUES ({placeholder}, {placeholder}, {placeholder})"
        )
        achievement_sql = (
            f"INSERT INTO Achievements (student_id, badge_name, date_awarded, remarks) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )
        activity_sql = f"INSERT INTO Activity_Log (activity) VALUES ({placeholder})"
        report_sql = (
            f"INSERT INTO Reports_Metadata (student_id, report_type, generated_at, file_path) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )

        for index, student_id in enumerate(student_ids):
            objective_id = objective_ids[index % len(objective_ids)]
            base_day = date.today() - timedelta(days=index % 30)

            # 1. Assessment Logs (Academic Average)
            cursor.execute(
                assessment_sql,
                (
                    student_id,
                    objective_id,
                    55 + (index * 7) % 46,
                    100,
                    base_day.isoformat(),
                    25 + (index % 20),
                ),
            )

            # 2. Multi-day Attendance (Calculates realistic percentage)
            for d in range(10):
                is_present = True
                if index % 5 == 0 and d in [2, 5]:  # 80% attendance
                    is_present = False
                elif index % 6 == 0 and d in [1, 3, 5, 7]:  # 60% attendance (High Risk)
                    is_present = False
                status = "P" if is_present else "A"
                cursor.execute(
                    attendance_sql,
                    (
                        student_id,
                        (date.today() - timedelta(days=d)).isoformat(),
                        status,
                    ),
                )

            # 3. Cyber-Wellness habits
            if index % 3 == 0:
                screen_time = 7.5
                wellness_score = 45.0
            elif index % 3 == 1:
                screen_time = 3.0
                wellness_score = 95.0
            else:
                screen_time = 5.0
                wellness_score = 75.0

            cursor.execute(
                audit_sql,
                (
                    student_id,
                    10 + (index % 10),
                    screen_time,
                    10 + (index % 10),
                    12 + (index % 8),
                    11 + (index % 7),
                    wellness_score,
                    date.today().isoformat(),
                ),
            )

            # 4. Multi-week progress logs (For Linear Regression Forecasting)
            if index % 3 == 0:
                scores = [80, 75, 70, 65]  # declining trend
            elif index % 3 == 1:
                scores = [60, 65, 70, 75]  # improving trend
            else:
                scores = [70, 71, 70, 72]  # stable trend
            for w, sc in enumerate(scores):
                cursor.execute(
                    progress_sql,
                    (
                        student_id,
                        (date.today() - timedelta(days=(4-w)*7)).isoformat(),
                        sc,
                    ),
                )

            # 5. Achievements
            if index % 4 == 0:
                cursor.execute(
                    achievement_sql,
                    (
                        student_id,
                        ACHIEVEMENT_BADGES[index % len(ACHIEVEMENT_BADGES)],
                        date.today().isoformat(),
                        "Awarded during sample seeding",
                    ),
                )

            # 6. Reports Metadata
            cursor.execute(
                report_sql,
                (
                    student_id,
                    "Report Card",
                    date.today().isoformat(),
                    f"reports/student_{student_id:03d}.txt",
                ),
            )

            cursor.execute(activity_sql, (f"Seeded sample record for student {student_id}",))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return {
        "students": _count_rows("Students"),
        "learning_objectives": _count_rows("Learning_Objectives"),
        "admin_logins": _count_rows("Admin_Login"),
        "diagnostic_logs": _count_rows("Diagnostic_Logs"),
        "attendance": _count_rows("Attendance"),
        "cyber_audit": _count_rows("Cyber_Audit"),
        "weekly_progress": _count_rows("Weekly_Progress"),
        "achievements": _count_rows("Achievements"),
        "activity_log": _count_rows("Activity_Log"),
        "reports_metadata": _count_rows("Reports_Metadata"),
    }


if __name__ == "__main__":
    print(seed_database(100))
