"""Safe cross-platform project setup and verification utility for PMLA-SCWE.

Provides interactive, non-destructive environment setup, dependency verification,
database diagnostics, schema initialization, and seeder management.
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

# ANSI colors for terminal rendering
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"


def print_status(status_type: str, message: str, color: str) -> None:
    print(f"{color}{COLOR_BOLD}[{status_type}]{COLOR_RESET} {message}")


def check_python_environment() -> bool:
    print(f"\n{COLOR_BOLD}[1/5] Checking Python Environment...{COLOR_RESET}")
    python_ver = sys.version.split()[0]
    major, minor = sys.version_info[:2]
    print_status("INFO", f"Python version: {python_ver} (Executable: {sys.executable})", COLOR_CYAN)
    
    if (major, minor) < (3, 10):
        print_status("FAIL", "PMLA-SCWE requires Python 3.10 or higher.", COLOR_RED)
        return False

    in_venv = (sys.prefix != sys.base_prefix) or ("VIRTUAL_ENV" in os.environ)
    if in_venv:
        print_status("PASS", "Virtual environment is active.", COLOR_GREEN)
        return True
    else:
        print_status("WARNING", "Virtual environment (.venv) is NOT currently active.", COLOR_YELLOW)
        print("         Recommended: activate .venv before running applications.")
        return True


def check_project_structure(root: Path) -> bool:
    print(f"\n{COLOR_BOLD}[2/5] Verifying Project Structure...{COLOR_RESET}")
    required_dirs = ["core", "desktop", "web", "database", "tests", "documentation"]
    missing = []
    for d in required_dirs:
        dir_path = root / d
        if dir_path.is_dir():
            print_status("PASS", f"Directory '{d}/' verified.", COLOR_GREEN)
        else:
            print_status("FAIL", f"Directory '{d}/' is MISSING!", COLOR_RED)
            missing.append(d)
    
    authoritative_schema = root / "database" / "schema.sql"
    if authoritative_schema.exists():
        print_status("PASS", "Authoritative schema 'database/schema.sql' found.", COLOR_GREEN)
    else:
        print_status("FAIL", "Authoritative schema 'database/schema.sql' is MISSING!", COLOR_RED)
        missing.append("database/schema.sql")

    return len(missing) == 0


def check_dependencies(root: Path) -> bool:
    print(f"\n{COLOR_BOLD}[3/5] Verifying Dependencies...{COLOR_RESET}")
    req_file = root / "requirements.txt"
    if not req_file.exists():
        print_status("WARNING", "requirements.txt not found.", COLOR_YELLOW)
        return False

    libraries_map = {
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "mysql-connector-python": "mysql.connector",
        "openai": "openai",
        "google-genai": "google.genai",
        "SpeechRecognition": "speech_recognition",
        "pyttsx3": "pyttsx3",
        "PySide6": "PySide6",
        "Flask": "flask",
        "python-dotenv": "dotenv",
        "reportlab": "reportlab",
    }

    all_installed = True
    for line in req_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lib_name = line.split("==")[0].split(">=")[0].strip()
        import_name = libraries_map.get(lib_name, lib_name)
        try:
            if import_name == "google.genai":
                from google import genai
            else:
                __import__(import_name)
            print_status("PASS", f"Package '{lib_name}' is installed.", COLOR_GREEN)
        except ImportError:
            print_status("FAIL", f"Package '{lib_name}' is MISSING!", COLOR_RED)
            all_installed = False

    if not all_installed:
        print("\n   --> To install missing dependencies, run: pip install -r requirements.txt\n")

    return all_installed


def check_configuration_and_database(root: Path) -> dict[str, Any]:
    print(f"\n{COLOR_BOLD}[4/5] Checking Configuration & Database Connectivity...{COLOR_RESET}")
    sys.path.insert(0, str(root))

    env_file = root / ".env"
    env_example = root / ".env.example"

    if env_file.exists():
        print_status("PASS", ".env configuration file is present.", COLOR_GREEN)
    elif env_example.exists():
        print_status("WARNING", ".env not found. A template exists at .env.example.", COLOR_YELLOW)
    else:
        print_status("WARNING", ".env and .env.example not found.", COLOR_YELLOW)

    from core.database import get_db_status, _SQLITE_DB_PATH
    db_status = get_db_status()
    print_status("INFO", f"Active Database Backend: {db_status.get('display', 'Unknown')}", COLOR_CYAN)

    if db_status.get("backend") == "MySQL" and db_status.get("available"):
        print_status("PASS", "MySQL Primary backend is reachable and authenticated.", COLOR_GREEN)
    else:
        print_status("INFO", f"SQLite Fallback file: {_SQLITE_DB_PATH}", COLOR_CYAN)
        if _SQLITE_DB_PATH.exists():
            print_status("PASS", "SQLite fallback database file exists and is operational.", COLOR_GREEN)
        else:
            print_status("WARNING", "SQLite fallback database file not yet created (will initialize on first run).", COLOR_YELLOW)

    return db_status


def interactive_database_options(root: Path) -> None:
    print(f"\n{COLOR_BOLD}[5/5] Database Initialization & Seeding Options{COLOR_RESET}")
    print("--------------------------------------------------")
    print("1. Verify/Initialize Database Schema (Non-destructive)")
    print("2. Run Version 2.0 Phase 1 Migration Pipeline (Idempotent)")
    print("3. Seed 100 Mock Demonstration Students (Requires explicit 'YES' confirmation)")
    print("4. Skip database operations and finish")
    print("--------------------------------------------------")

    try:
        choice = input("Select an option [1-4, default=1]: ").strip() or "1"
    except (KeyboardInterrupt, EOFError):
        print("\n[INFO] Setup finished.")
        return

    if choice == "1":
        from core.database import initialize_database
        print("\n[INFO] Initializing database schema...")
        if initialize_database():
            print_status("PASS", "Database schema initialized successfully.", COLOR_GREEN)
        else:
            print_status("FAIL", "Failed to initialize database schema.", COLOR_RED)

    elif choice == "2":
        from core.migration_service import run_v2_phase1_migration
        print("\n[INFO] Executing Version 2.0 Phase 1 Migration Pipeline...")
        report = run_v2_phase1_migration(create_backup=True)
        if report.get("success"):
            print_status("PASS", f"Migration completed successfully. Version: {report.get('version')}", COLOR_GREEN)
            if report.get("already_applied"):
                print_status("INFO", "Migration was already previously applied.", COLOR_CYAN)
        else:
            print_status("FAIL", f"Migration encountered errors: {report.get('errors')}", COLOR_RED)

    elif choice == "3":
        print("\n" + "!" * 55)
        print("WARNING: This will delete existing operational student records and seed 100 mock students!")
        print("!" * 55)
        try:
            confirm = input("Type 'YES' to confirm mock data reset: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Seeding cancelled.")
            return

        if confirm == "YES":
            from seed_data import seed_database
            print("\n[INFO] Seeding 100 demonstration student profiles...")
            try:
                seed_database(100)
                print_status("PASS", "Clean mock demonstration database seeded successfully.", COLOR_GREEN)
            except Exception as e:
                print_status("FAIL", f"Error seeding mock database: {e}", COLOR_RED)
        else:
            print("[INFO] Seeding cancelled. No database changes were made.")

    else:
        print("[INFO] Skipping database operations.")


def main():
    parser = argparse.ArgumentParser(description="PMLA-SCWE Project Setup and Verification Utility")
    parser.add_argument("--non-interactive", action="store_true", help="Run checks only without interactive database prompts")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent

    print(f"\n{COLOR_CYAN}{COLOR_BOLD}==================================================")
    print(" PMLA-SCWE PROJECT SETUP & VERIFICATION UTILITY")
    print(" Checkpoint: Version 2.0 Phase 1 (Multi-School Tenancy)")
    print(f"=================================================={COLOR_RESET}")

    p_ok = check_python_environment()
    s_ok = check_project_structure(root)
    d_ok = check_dependencies(root)
    db_status = check_configuration_and_database(root)

    print(f"\n{COLOR_BOLD}==================================================")
    print(" SETUP VERIFICATION SUMMARY")
    print("==================================================")
    print(f"Python Environment:    [{'PASS' if p_ok else 'FAIL'}]")
    print(f"Project Structure:     [{'PASS' if s_ok else 'FAIL'}]")
    print(f"Dependencies:          [{'PASS' if d_ok else 'FAIL'}]")
    print(f"Database Backend:      [{db_status.get('backend', 'Unknown')}] ({db_status.get('mode', 'Standby')})")
    print("==================================================")

    if not args.non_interactive:
        interactive_database_options(root)

    print(f"\n{COLOR_GREEN}{COLOR_BOLD}[SUCCESS] Setup verification complete.{COLOR_RESET}\n")
    print("Next steps:")
    print("  - Launch PySide6 Desktop GUI:  python main.py")
    print("  - Launch Flask Web Console:    python main.py --web")
    print("  - Run Unit Test Suite:         python -m unittest discover -s tests -p \"test_*.py\"")
    print("  - Run Phase 1 Smoke Test:      python tests/smoke_test_v2.py\n")


if __name__ == "__main__":
    main()
