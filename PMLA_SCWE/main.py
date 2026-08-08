"""Application entry point for PMLA-SCWE."""

from __future__ import annotations

from .analytics import calculate_learning_health_score
from .config import MENU_TITLE
from . import authentication, student, attendance, assessment
from .database import initialize_database_from_file, execute_select
from datetime import date, datetime
import re


def _prompt_nonempty(prompt: str) -> str:
    v = input(prompt).strip()
    while not v:
        print("This field is required. Please enter a value.")
        v = input(prompt).strip()
    return v


def _prompt_optional(prompt: str) -> str | None:
    v = input(prompt).strip()
    return v or None


def _parse_int(s: str) -> int | None:
    try:
        return int(s)
    except Exception:
        return None


def _parse_float(s: str) -> float | None:
    try:
        return float(s)
    except Exception:
        return None


def _parse_date(s: str) -> str | None:
    if not s:
        return None
    try:
        # accept YYYY-MM-DD only
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except Exception:
        return None


def _validate_email(e: str) -> bool:
    if not e:
        return False
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e) is not None


def display_menu() -> None:
    print(MENU_TITLE)
    print("1. Login")
    print("2. Add Student")
    print("3. List Students")
    print("4. Attendance")
    print("5. Assessment")
    print("9. Exit")


def do_login() -> bool:
    attempts = 3
    while attempts > 0:
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        password = input("Password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        try:
            if authentication.login(username, password):
                print("Login successful.")
                return True
        except Exception:
            print("An error occurred while attempting to log in. Check database connection.")
            return False
        attempts -= 1
        print(f"Login failed. Attempts remaining: {attempts}")
    print("Login attempts exhausted.")
    return False


def do_add_student() -> None:
    print("Add Student")
    first_name = _prompt_nonempty("First name: ")
    last_name = _prompt_nonempty("Last name: ")
    class_section = _prompt_nonempty("Class/Section: ")
    dob_in = _prompt_optional("Date of birth (YYYY-MM-DD) [optional]: ")
    dob = _parse_date(dob_in) if dob_in else None
    if dob_in and not dob:
        print("Invalid date format. Use YYYY-MM-DD. Date ignored.")
        dob = None
    gender = _prompt_optional("Gender (M/F/O) [optional]: ")
    if gender and gender.upper() not in ("M", "F", "O"):
        print("Invalid gender. Use M, F, or O. Value ignored.")
        gender = None
    email = _prompt_optional("Email [optional]: ")
    if email and not _validate_email(email):
        print("Invalid email format. Email ignored.")
        email = None
    phone = _prompt_optional("Phone [optional]: ")
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "class_section": class_section,
        "dob": dob,
        "gender": gender and gender.upper(),
        "email": email,
        "phone": phone,
    }
    try:
        ok = student.add_student(data)
        print("Student added." if ok else "Failed to add student. See logs or DB for details.")
    except Exception:
        print("Unexpected error while adding student. Check DB connection.")


def do_list_students() -> None:
    rows = execute_select("SELECT student_id, first_name, last_name, class_section, email, phone FROM Students")
    if not rows:
        print("No students found.")
        return
    print("Students:")
    for r in rows:
        print(f"{r.get('student_id')}: {r.get('first_name')} {r.get('last_name')} - {r.get('class_section')} - {r.get('email')}")


def do_mark_attendance() -> None:
    print("Mark Attendance")
    sid_raw = input("Student ID: ").strip()
    sid = _parse_int(sid_raw)
    if sid is None:
        print("Invalid student id; must be a number.")
        return
    date_raw = input("Date (YYYY-MM-DD) [today]: ").strip()
    if not date_raw:
        date_val = date.today().isoformat()
    else:
        date_val = _parse_date(date_raw)
        if not date_val:
            print("Invalid date format; use YYYY-MM-DD.")
            return
    status = input("Status (P/A) [P]: ").strip().upper() or "P"
    if status not in ("P", "A"):
        print("Invalid status. Use 'P' or 'A'.")
        return
    ok = attendance.mark_attendance({
        "student_id": sid,
        "attendance_date": date_val,
        "status": status,
    })
    print("Attendance recorded." if ok else "Failed to record attendance.")


def do_attendance_percentage() -> None:
    print("Attendance Percentage")
    try:
        sid = int(input("Student ID: ").strip())
    except Exception:
        print("Invalid student id")
        return
    pct = attendance.calculate_attendance_percentage(sid)
    print(f"Attendance: {pct:.2f}%")


def do_add_assessment() -> None:
    print("Add Assessment")
    sid_raw = input("Student ID: ").strip()
    sid = _parse_int(sid_raw)
    if sid is None:
        print("Invalid student id; must be a number.")
        return
    oid_raw = input("Objective ID [optional]: ").strip()
    oid = _parse_int(oid_raw) if oid_raw else None
    score_raw = input("Score obtained: ").strip()
    score = _parse_float(score_raw)
    if score is None or score < 0:
        print("Invalid score; must be a non-negative number.")
        return
    max_raw = input("Max score [100]: ").strip() or "100"
    max_score = _parse_float(max_raw)
    if max_score is None or max_score <= 0:
        print("Invalid max score; must be a positive number.")
        return
    if score > max_score:
        print("Score cannot be greater than max score.")
        return
    date_raw = input("Test date (YYYY-MM-DD) [today]: ").strip()
    test_date = date.today().isoformat() if not date_raw else _parse_date(date_raw)
    if date_raw and not test_date:
        print("Invalid date format; use YYYY-MM-DD.")
        return
    ok = assessment.add_assessment({
        "student_id": sid,
        "objective_id": oid,
        "score_obtained": score,
        "max_score": float(max_score),
        "test_date": test_date,
    })
    print("Assessment added." if ok else "Failed to add assessment. Check inputs or DB.")


def do_assessment_history() -> None:
    print("Assessment History")
    try:
        sid = int(input("Student ID: ").strip())
    except Exception:
        print("Invalid student id")
        return
    rows = assessment.get_assessment_history(sid)
    if not rows:
        print("No assessments found.")
        return
    for r in rows:
        print(f"{r.get('test_date')} - {r.get('objective_id')} - {r.get('score_obtained')}/{r.get('max_score')}")


def run() -> None:
    # Ensure DB schema exists for testing (SQLite fallback will create tables)
    initialize_database_from_file("schema.sql")
    # Ensure at least one admin exists for testing; create default if missing
    try:
        cnt = execute_select("SELECT COUNT(*) AS cnt FROM Admin_Login")
        if not cnt or cnt[0].get("cnt", 0) == 0:
            created = authentication.create_admin("admin", "admin123")
            if created:
                print("Default admin created: username=admin password=admin123")
    except Exception:
        pass
    logged_in = False
    while True:
        display_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            logged_in = do_login()
        elif choice == "2":
            if not logged_in:
                print("Please login first.")
                continue
            do_add_student()
        elif choice == "3":
            if not logged_in:
                print("Please login first.")
                continue
            do_list_students()
        elif choice == "4":
            if not logged_in:
                print("Please login first.")
                continue
            print("1. Mark Attendance\n2. Attendance %")
            sub = input("Select: ").strip()
            if sub == "1":
                do_mark_attendance()
            elif sub == "2":
                do_attendance_percentage()
            else:
                print("Invalid sub-option")
        elif choice == "5":
            if not logged_in:
                print("Please login first.")
                continue
            print("1. Add Assessment\n2. Assessment History")
            sub = input("Select: ").strip()
            if sub == "1":
                do_add_assessment()
            elif sub == "2":
                do_assessment_history()
            else:
                print("Invalid sub-option")
        elif choice == "9":
            print("Exiting.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    run()
