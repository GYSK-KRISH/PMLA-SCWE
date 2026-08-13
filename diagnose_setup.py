"""Diagnostics and Setup Verification Script for PMLA-SCWE.

Runs a complete 5-stage check:
1. Python environment
2. Required packages
3. Configuration
4. Database connection
5. Database schema
"""

from __future__ import annotations
import os
import sys
import socket
from pathlib import Path

# ANSI colors for nice terminal rendering
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"


def print_status(status_type: str, message: str, color: str) -> None:
    print(f"{color}{COLOR_BOLD}[{status_type}]{COLOR_RESET} {message}")


def run_diagnostics():
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}==================================================")
    print(" PMLA-SCWE ENVIRONMENT DIAGNOSTICS")
    print(f"=================================================={COLOR_RESET}\n")

    stages = {"env": True, "deps": True, "config": True, "db_conn": True, "db_schema": True}

    # ----------------------------------------------------
    # Stage [1/5]: Python Environment Check
    # ----------------------------------------------------
    print(f"{COLOR_BOLD}[1/5] Checking Python Environment...{COLOR_RESET}")
    python_ver = sys.version.split()[0]
    print_status("INFO", f"Python version: {python_ver} (Executable: {sys.executable})", COLOR_CYAN)

    in_venv = (sys.prefix != sys.base_prefix) or ("VIRTUAL_ENV" in os.environ)
    if in_venv:
        print_status("PASS", "Virtual environment is active.", COLOR_GREEN)
    else:
        print_status("FAIL", "Virtual environment (VENV) is NOT active!", COLOR_RED)
        print("\n   --> ACTION REQUIRED to activate VENV on Windows VS Code:")
        print("      1. Open the command palette in VS Code (Ctrl + Shift + P).")
        print("      2. Type and select: 'Python: Select Interpreter'.")
        print("      3. Choose the option pointing to '.venv\\Scripts\\python.exe'.")
        print("      4. Open a NEW terminal (Ctrl + Shift + `) to trigger auto-activation.\n")
        stages["env"] = False

    # ----------------------------------------------------
    # Stage [2/5]: Required Packages Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}[2/5] Checking Required Packages...{COLOR_RESET}")
    req_file_path = Path(__file__).resolve().parent / "requirements.txt"
    
    libraries_map = {
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "mysql-connector-python": "mysql.connector",
        "openai": "openai",
        "google-genai": "google.genai",
        "SpeechRecognition": "speech_recognition",
        "pyttsx3": "pyttsx3",
        "customtkinter": "customtkinter",
        "Flask": "flask",
        "python-dotenv": "dotenv"
    }

    if not req_file_path.exists():
        print_status("WARNING", f"requirements.txt not found at {req_file_path}. Skipping checks.", COLOR_YELLOW)
    else:
        missing_libs = []
        for line in req_file_path.read_text().splitlines():
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
                print_status("PASS", f"Module '{lib_name}' is installed.", COLOR_GREEN)
            except ImportError:
                print_status("FAIL", f"Module '{lib_name}' is MISSING!", COLOR_RED)
                missing_libs.append(lib_name)
                stages["deps"] = False

        if missing_libs:
            print("\n   --> ACTION REQUIRED to install missing packages:")
            print("      pip install -r requirements.txt\n")

    # ----------------------------------------------------
    # Stage [3/5]: Configuration Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}[3/5] Checking Configuration...{COLOR_RESET}")
    sys.path.append(str(Path(__file__).resolve().parent))
    
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        print_status("PASS", ".env configuration file is present.", COLOR_GREEN)
    else:
        print_status("WARNING", ".env file not found (AI assistant keys might be missing).", COLOR_YELLOW)

    try:
        from core import config
        cfg = config.DATABASE_CONFIG
        print_status("INFO", f"Config parameters -> host={cfg['host']}, user={cfg['user']}, database={cfg['database']}, port={cfg['port']}", COLOR_CYAN)
    except Exception as e:
        print_status("FAIL", f"Could not load database configuration: {e}", COLOR_RED)
        stages["config"] = False

    # ----------------------------------------------------
    # Stage [4/5]: Database Connection Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}[4/5] Checking Database Connection...{COLOR_RESET}")
    
    # 1. MySQL check (Port 3306)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    mysql_port_open = s.connect_ex(("127.0.0.1", 3306)) == 0
    s.close()

    mysql_connected = False
    if mysql_port_open:
        print_status("PASS", "MySQL server is listening on port 3306.", COLOR_GREEN)
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                port=cfg["port"]
            )
            print_status("PASS", "Successfully authenticated with MySQL server.", COLOR_GREEN)
            mysql_connected = True
            conn.close()
        except Exception as e:
            print_status("FAIL", f"MySQL authentication failed: {e}", COLOR_RED)
            print("      Ensure password in 'core/config.py' matches local MySQL root password.")
    else:
        print_status("INFO", "MySQL port 3306 is closed. App will run in SQLite fallback mode.", COLOR_CYAN)

    # 2. SQLite fallback check
    sqlite_db_path = Path(__file__).resolve().parent / "pmla_scwe_fallback.db"
    sqlite_ok = False
    if sqlite_db_path.exists():
        print_status("PASS", f"SQLite fallback database found: {sqlite_db_path}", COLOR_GREEN)
        sqlite_ok = True
    else:
        print_status("INFO", "SQLite fallback database file not found yet (will auto-create on first run).", COLOR_CYAN)
        sqlite_ok = True

    if not mysql_connected and not sqlite_ok:
        stages["db_conn"] = False

    # ----------------------------------------------------
    # Stage [5/5]: Database Schema Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}[5/5] Checking Database Schema...{COLOR_RESET}")
    
    EXPECTED_TABLES = [
        "Admin_Login",
        "Students",
        "Learning_Objectives",
        "Diagnostic_Logs",
        "Cyber_Audit",
        "Weekly_Progress",
        "Achievements",
        "Attendance",
        "Activity_Log",
        "Reports_Metadata",
        "Users",
        "Notifications"
    ]

    schema_passed = True

    if mysql_connected:
        print(f"{COLOR_CYAN}Checking MySQL database schema tables...{COLOR_RESET}")
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                port=cfg["port"]
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            existing_tables = [t[0].lower() for t in cursor.fetchall()]
            
            for table in EXPECTED_TABLES:
                if table.lower() in existing_tables:
                    print(f"  [PASS] {table}")
                else:
                    print(f"  [FAIL] {table} -- MISSING")
                    schema_passed = False
            
            cursor.close()
            conn.close()
        except Exception as e:
            print_status("FAIL", f"Error checking MySQL schema: {e}", COLOR_RED)
            schema_passed = False
    else:
        # SQLite check
        if sqlite_db_path.exists():
            print(f"{COLOR_CYAN}Checking SQLite fallback schema tables...{COLOR_RESET}")
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [t[0].lower() for t in cursor.fetchall()]
                
                for table in EXPECTED_TABLES:
                    if table.lower() in existing_tables:
                        print(f"  [PASS] {table}")
                    else:
                        print(f"  [FAIL] {table} -- MISSING")
                        schema_passed = False
                
                cursor.close()
                conn.close()
            except Exception as e:
                print_status("FAIL", f"Error checking SQLite schema: {e}", COLOR_RED)
                schema_passed = False
        else:
            print_status("INFO", "Skipping schema validation (run the app or seeder to generate schema).", COLOR_CYAN)

    if not schema_passed:
        stages["db_schema"] = False

    # ----------------------------------------------------
    # Diagnostic Report Summary
    # ----------------------------------------------------
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}==================================================")
    print(" SETUP DIAGNOSTIC RESULT")
    print(f"=================================================={COLOR_RESET}\n")

    def print_result(name: str, passed: bool):
        mark = f"{COLOR_GREEN}[PASS]{COLOR_RESET}" if passed else f"{COLOR_RED}[FAIL]{COLOR_RESET}"
        print(f"%-25s %s" % (name + ":", mark))

    print_result("Python Environment", stages["env"])
    print_result("Dependencies", stages["deps"])
    print_result("Configuration", stages["config"])
    print_result("Database Connection", stages["db_conn"])
    print_result("Database Schema", stages["db_schema"])

    all_passed = all(stages.values())
    if all_passed:
        print(f"\n{COLOR_GREEN}{COLOR_BOLD}PMLA-SCWE is ready to run.{COLOR_RESET}")
    else:
        print(f"\n{COLOR_RED}{COLOR_BOLD}Please fix errors listed above before running the app.{COLOR_RESET}")

    print(f"\n{COLOR_CYAN}{COLOR_BOLD}=================================================={COLOR_RESET}\n")

    print("Next commands:\n")
    print(f"  python seed_data.py")
    print(f"  python main.py")
    print(f"  python main.py --web\n")


if __name__ == "__main__":
    run_diagnostics()
