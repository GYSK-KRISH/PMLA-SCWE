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
    """Seed the database with 100 students if fewer than that already exist."""
    initialize_database_from_file("schema.sql")

    conn = get_connection()
    placeholder = _placeholder(conn)
    cursor = conn.cursor()
    rng = Random(42)

    try:
        _ensure_admin(cursor, placeholder)
        _ensure_objectives(cursor, placeholder)

        existing_students = _count_rows("Students")
        to_add = max(0, target_students - existing_students)
        start_index = existing_students + 1

        student_sql = (
            f"INSERT INTO Students (first_name, last_name, class_section, dob, gender, email, phone, enrollment_date) "
            f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
        )

        for offset in range(to_add):
            number = start_index + offset
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

        existing_assessments = _fetch_ids(cursor, "Diagnostic_Logs", "student_id")
        existing_attendance = _fetch_ids(cursor, "Attendance", "student_id")
        existing_audit = _fetch_ids(cursor, "Cyber_Audit", "student_id")
        existing_progress = _fetch_ids(cursor, "Weekly_Progress", "student_id")
        existing_achievements = _fetch_ids(cursor, "Achievements", "student_id")
        existing_activity = _fetch_ids(cursor, "Activity_Log", "log_id") if _count_rows("Activity_Log") else set()
        existing_reports = _fetch_ids(cursor, "Reports_Metadata", "student_id")

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

            if student_id not in existing_assessments:
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

            if student_id not in existing_attendance:
                cursor.execute(
                    attendance_sql,
                    (
                        student_id,
                        (date.today() - timedelta(days=index % 14)).isoformat(),
                        "P" if index % 5 != 0 else "A",
                    ),
                )

            if student_id not in existing_audit:
                cursor.execute(
                    audit_sql,
                    (
                        student_id,
                        10 + (index % 10),
                        round(2.0 + (index % 8) * 0.5, 1),
                        10 + (index % 10),
                        12 + (index % 8),
                        11 + (index % 7),
                        60 + (index % 35),
                        date.today().isoformat(),
                    ),
                )

            if student_id not in existing_progress:
                cursor.execute(
                    progress_sql,
                    (
                        student_id,
                        (date.today() - timedelta(days=7)).isoformat(),
                        60 + (index % 40),
                    ),
                )

            if student_id not in existing_achievements and index % 4 == 0:
                cursor.execute(
                    achievement_sql,
                    (
                        student_id,
                        ACHIEVEMENT_BADGES[index % len(ACHIEVEMENT_BADGES)],
                        date.today().isoformat(),
                        "Awarded during sample seeding",
                    ),
                )

            if student_id not in existing_reports:
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
