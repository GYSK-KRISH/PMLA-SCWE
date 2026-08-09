"""Application entry point for PMLA-SCWE."""

from __future__ import annotations

from .config import MENU_TITLE
from . import authentication, student, attendance, assessment, analytics, recommendation
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
    print("6. Predictive Analytics & Insights")
    print("7. Cyber Wellness Audit")
    print("8. AI Assistant")
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

def do_add_cyber_audit() -> None:
    print("Add Cyber Audit")
    sid_raw = input("Student ID: ").strip()
    sid = _parse_int(sid_raw)
    if sid is None:
        print("Invalid student id; must be a number.")
        return

    daily_raw = input("Daily screen time (hours): ").strip()
    daily = _parse_float(daily_raw)
    if daily is None:
        print("Invalid daily screen time; must be a number.")
        return
        
    study_raw = input("Study screen time (hours): ").strip()
    study = _parse_float(study_raw)
    if study is None:
        print("Invalid study screen time; must be a number.")
        return
        
    rec_raw = input("Recreational screen time (hours): ").strip()
    rec = _parse_float(rec_raw)
    if rec is None:
        print("Invalid recreational screen time; must be a number.")
        return
        
    sleep_raw = input("Sleep duration (hours): ").strip()
    sleep = _parse_float(sleep_raw)
    if sleep is None:
        print("Invalid sleep duration; must be a number.")
        return
        
    distract_raw = input("Digital distraction level (1-5): ").strip()
    distract = _parse_int(distract_raw)
    if distract is None:
        print("Invalid digital distraction level; must be an integer.")
        return
        
    safety_raw = input("Cyber safety awareness (1-5): ").strip()
    safety = _parse_int(safety_raw)
    if safety is None:
        print("Invalid cyber safety awareness; must be an integer.")
        return

    remarks = input("Remarks [optional]: ").strip() or None

    audit_data = {
        "student_id": sid,
        "daily_screen_time": daily,
        "study_screen_time": study,
        "recreational_screen_time": rec,
        "sleep_duration": sleep,
        "digital_distraction_level": distract,
        "cyber_safety_awareness": safety,
        "remarks": remarks,
        "audit_date": date.today().isoformat()
    }

    from . import cyber_audit
    errors = cyber_audit.validate_audit_data(audit_data)
    if errors:
        print("Validation errors occurred:")
        for err in errors:
            print(f"- {err}")
        return

    ok = cyber_audit.add_cyber_audit(audit_data)
    if ok:
        latest = cyber_audit.get_latest_audit(sid)
        score = latest["wellness_score"] if latest else 0.0
        print(f"Cyber audit added. Calculated Wellness Score: {score:.2f}%")
    else:
        print("Failed to add cyber audit. Check database or logs.")


def do_view_cyber_audit_history() -> None:
    print("View Audit History")
    sid_raw = input("Student ID: ").strip()
    sid = _parse_int(sid_raw)
    if sid is None:
        print("Invalid student id; must be a number.")
        return

    from .database import execute_select
    res = execute_select("SELECT COUNT(*) AS cnt FROM Students WHERE student_id = %s", (sid,))
    if not res or res[0].get("cnt", 0) == 0:
        print(f"Student ID {sid} does not exist.")
        return

    from . import cyber_audit
    history = cyber_audit.get_student_audits(sid)
    if not history:
        print("No audit history found for this student.")
        return

    print(f"\nAudit History for Student {sid}:")
    print("-" * 80)
    for h in history:
        print(f"Date: {h.get('audit_date')}")
        print(f"  Daily/Study/Rec Screen: {h.get('daily_screen_time')}h / {h.get('study_screen_time')}h / {h.get('recreational_screen_time')}h")
        print(f"  Sleep Duration: {h.get('sleep_duration')}h")
        print(f"  Distraction Level: {h.get('digital_distraction_level')}/5  |  Safety Awareness: {h.get('cyber_safety_awareness')}/5")
        print(f"  Wellness Score: {h.get('wellness_score') or 0.0:.2f}%")
        if h.get('remarks'):
            print(f"  Remarks: {h.get('remarks')}")
        print("-" * 80)


def do_cyber_wellness_audit() -> None:
    while True:
        print("\nCyber Wellness Audit Menu")
        print("1. Add Cyber Audit")
        print("2. View Audit History")
        print("3. Back to Main Menu")
        sub = input("Select: ").strip()
        if sub == "1":
            do_add_cyber_audit()
        elif sub == "2":
            do_view_cyber_audit_history()
        elif sub == "3":
            break
        else:
            print("Invalid option. Please choose 1, 2, or 3.")


def do_predictive_analytics() -> None:
    while True:
        print("\nPredictive Analytics & Insights Menu")
        print("1. View Single Student Analytics")
        print("2. Class-wide Risk Report & Teacher Alerts")
        print("3. Back to Main Menu")
        sub = input("Select an option: ").strip()
        if sub == "1":
            try:
                sid = int(input("Enter Student ID: ").strip())
            except ValueError:
                print("Invalid student ID. Must be an integer.")
                continue
            summary = analytics.get_student_analytics_summary(sid)
            if not summary:
                print(f"Student ID {sid} not found in the database.")
                continue
            
            # Generate insights and plan
            insights = recommendation.explain_learning_insights(summary)
            plan = recommendation.generate_intervention_plan(summary)
            
            # Print the formatted report
            print("\n============================================================")
            print("             PMLA-SCWE PREDICTIVE ANALYTICS")
            print("============================================================")
            print(f"Student ID       : {summary['student_id']}")
            print(f"Student Name     : {summary['first_name']} {summary['last_name']}")
            print(f"Class/Section    : {summary['class_section']}")
            print("\nACADEMIC ANALYTICS")
            print("------------------------------------------------------------")
            print(f"Average Score    : {summary['academic_average']:.2f}% ({summary['academic_status']})")
            print(f"Weekly Trend     : {summary['trend_direction']}")
            print(f"Predicted Score  : {summary['predicted_score']:.2f}%")
            print("\nATTENDANCE")
            print("------------------------------------------------------------")
            print(f"Attendance       : {summary['attendance_percentage']:.2f}% ({summary['attendance_status']})")
            print("\nCYBER-WELLNESS")
            print("------------------------------------------------------------")
            print(f"Wellness Score   : {summary['wellness_score']:.2f}% ({summary['wellness_status']})")
            print(f"Screen Time      : {summary['screen_time_hours']:.1f} hours/day")
            print("\nLEARNING HEALTH")
            print("------------------------------------------------------------")
            print(f"Health Score     : {summary['health_score']:.2f}")
            print(f"Risk Level       : {summary['risk_level']}")
            print("\nEXPLAINABLE INSIGHTS")
            print("------------------------------------------------------------")
            for ins in insights:
                print(f"• {ins}")
            print("\nINTERVENTION PLAN")
            print("------------------------------------------------------------")
            for p in plan:
                print(f"• {p}")
            print("============================================================\n")

            # Student-level reporting sub-options
            while True:
                print("Student Action Sub-Menu:")
                print("  1. Generate & Save Visual Charts")
                print("  2. Export Report to CSV & Text Formats")
                print("  3. Back to Analytics Menu")
                choice_sub = input("Select an option: ").strip()
                if choice_sub == "1":
                    from . import graphs
                    print("Generating visual charts...")
                    p1 = graphs.plot_student_progress(sid)
                    p2 = graphs.plot_attendance(sid)
                    p3 = graphs.plot_cyber_wellness(sid)
                    p4 = graphs.plot_learning_health(sid)
                    print("Charts saved successfully under 'reports/' directory:")
                    print(f"  - Progress Chart: {p1}")
                    print(f"  - Attendance Chart: {p2}")
                    print(f"  - Cyber Wellness Chart: {p3}")
                    print(f"  - Learning Health Chart: {p4}")
                elif choice_sub == "2":
                    from . import reports
                    print("Exporting report files...")
                    csv_path = reports.export_student_report_csv(sid)
                    txt_path = f"reports/student_{sid}_report.txt"
                    text_content = reports.build_student_report(summary)
                    with open(txt_path, "w", encoding="utf-8") as tf:
                        tf.write(text_content)
                    print("Student reports exported successfully:")
                    print(f"  - CSV Format: {csv_path}")
                    print(f"  - Text Format: {txt_path}")
                elif choice_sub == "3":
                    break
                else:
                    print("Invalid option. Please choose 1, 2, or 3.")
            
        elif sub == "2":
            # Class-wide Risk Report & Teacher Alerts
            student_rows = execute_select("SELECT student_id FROM Students ORDER BY student_id")
            if not student_rows:
                print("No students found in the database.")
                continue
                
            high_risk_list = []
            alerts_map = {}
            
            for row in student_rows:
                sid = int(row["student_id"])
                summary = analytics.get_student_analytics_summary(sid)
                if not summary:
                    continue
                alerts = recommendation.generate_teacher_alerts(summary)
                if summary["risk_level"] == "HIGH":
                    high_risk_list.append((summary, len(alerts)))
                if alerts:
                    alerts_map[f"{summary['first_name']} {summary['last_name']} (ID: {summary['student_id']})"] = alerts
            
            print("\n============================================================")
            print("              CLASS-WIDE RISK REPORT")
            print("============================================================")
            print("\nHIGH-RISK STUDENTS")
            print("------------------------------------------------------------")
            print(f"{'ID':<6}{'NAME':<20}{'HEALTH':<11}{'RISK':<11}{'ALERTS':<6}")
            for summary, alert_count in high_risk_list:
                name = f"{summary['first_name']} {summary['last_name']}"
                print(f"{summary['student_id']:<6}{name:<20}{summary['health_score']:<11.1f}{summary['risk_level']:<11}{alert_count:<6}")
            if not high_risk_list:
                print("No high-risk students identified.")
                
            print("\nACTIVE TEACHER ALERTS")
            print("------------------------------------------------------------")
            if alerts_map:
                for student_display, alerts in alerts_map.items():
                    print(f"\n{student_display}")
                    for alert in alerts:
                        print(f"  [!] {alert}")
            else:
                print("No active alerts generated.")
            print("============================================================\n")

            # Class-level reporting sub-options
            while True:
                print("Class Action Sub-Menu:")
                print("  1. Generate Class-wide Performance Scatter Chart")
                print("  2. Export Class-wide Report to CSV & Text Formats")
                print("  3. Back to Analytics Menu")
                choice_sub = input("Select an option: ").strip()
                if choice_sub == "1":
                    from . import graphs
                    print("Generating class performance scatter chart...")
                    p_class = graphs.plot_class_performance()
                    print(f"Class chart saved successfully: {p_class}")
                elif choice_sub == "2":
                    from . import reports
                    print("Exporting class-wide report...")
                    csv_path = reports.export_class_report_csv()
                    txt_path = "reports/class_report.txt"
                    class_summary = reports.get_class_summary_data()
                    text_content = reports.build_teacher_report(class_summary)
                    with open(txt_path, "w", encoding="utf-8") as tf:
                        tf.write(text_content)
                    print("Class reports exported successfully:")
                    print(f"  - CSV Format: {csv_path}")
                    print(f"  - Text Format: {txt_path}")
                elif choice_sub == "3":
                    break
                else:
                    print("Invalid option. Please choose 1, 2, or 3.")
            
        elif sub == "3":
            break
        else:
            print("Invalid option. Please choose 1, 2, or 3.")

def do_ai_assistant_menu() -> None:
    while True:
        print("\n=== AI Assistant Menu ===")
        print("1. Type a Question")
        print("2. Voice Command")
        print("3. Ask About Student")
        print("4. Student Suggestions")
        print("5. Back")
        choice = input("Select an option: ").strip()
        
        from . import ai_assistant
        
        if choice == "1":
            q = input("\nWhat would you like to ask the AI? ").strip()
            if not q:
                print("Question cannot be empty.")
                continue
            print("Consulting AI Assistant...")
            response = ai_assistant.ask_ai(q)
            print(f"\nAI Response:\n{response}")
            ai_assistant.speak_response(response)
            
        elif choice == "2":
            voice_text = ai_assistant.listen_for_command()
            if voice_text.startswith("[Error:"):
                print(voice_text)
                continue
            print(f"Recognized Speech: '{voice_text}'")
            
            match = re.search(r"student\s*(?:id)?\s*(\d+)", voice_text, re.IGNORECASE)
            if match:
                sid = int(match.group(1))
                print(f"Detected query relates to Student ID {sid}.")
                
                from .database import execute_select
                res = execute_select("SELECT COUNT(*) AS cnt FROM Students WHERE student_id = %s", (sid,))
                if not res or res[0].get("cnt", 0) == 0:
                    print(f"Student ID {sid} does not exist in the database.")
                    continue
                    
                if "suggestion" in voice_text.lower():
                    print("Consulting AI Assistant for suggestions...")
                    response = ai_assistant.get_ai_suggestions(sid)
                else:
                    print("Consulting AI Assistant with student data...")
                    response = ai_assistant.ask_ai_about_student(sid, voice_text)
            else:
                print("Consulting AI Assistant for general query...")
                response = ai_assistant.ask_ai(voice_text)
                
            print(f"\nAI Response:\n{response}")
            ai_assistant.speak_response(response)
            
        elif choice == "3":
            sid_raw = input("\nEnter Student ID: ").strip()
            sid = _parse_int(sid_raw)
            if sid is None:
                print("Invalid student ID; must be a number.")
                continue
                
            from .database import execute_select
            res = execute_select("SELECT COUNT(*) AS cnt FROM Students WHERE student_id = %s", (sid,))
            if not res or res[0].get("cnt", 0) == 0:
                print(f"Student ID {sid} does not exist in the database.")
                continue
                
            q = input("Enter your question about this student: ").strip()
            if not q:
                print("Question cannot be empty.")
                continue
            print("Consulting AI Assistant with student data...")
            response = ai_assistant.ask_ai_about_student(sid, q)
            print(f"\nAI Response:\n{response}")
            ai_assistant.speak_response(response)
            
        elif choice == "4":
            sid_raw = input("\nEnter Student ID: ").strip()
            sid = _parse_int(sid_raw)
            if sid is None:
                print("Invalid student ID; must be a number.")
                continue
                
            from .database import execute_select
            res = execute_select("SELECT COUNT(*) AS cnt FROM Students WHERE student_id = %s", (sid,))
            if not res or res[0].get("cnt", 0) == 0:
                print(f"Student ID {sid} does not exist in the database.")
                continue
                
            print("Generating AI suggestions...")
            response = ai_assistant.get_ai_suggestions(sid)
            print(f"\nAI Suggestions:\n{response}")
            ai_assistant.speak_response(response)
            
        elif choice == "5":
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, 4, or 5.")


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
        elif choice == "6":
            if not logged_in:
                print("Please login first.")
                continue
            do_predictive_analytics()
        elif choice == "7":
            if not logged_in:
                print("Please login first.")
                continue
            do_cyber_wellness_audit()
        elif choice == "8":
            if not logged_in:
                print("Please login first.")
                continue
            do_ai_assistant_menu()
        elif choice == "9":
            print("Exiting.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    run()
