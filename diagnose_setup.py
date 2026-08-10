"""Diagnostics and Setup Verification Script for PMLA-SCWE.

This script runs a complete diagnostic check of your Python environment,
virtual environment (VENV), package dependencies, and database settings (MySQL and SQLite).
Run this script to locate and fix setup errors.
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
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}======================================================================{COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}                  PMLA-SCWE ENVIRONMENT DIAGNOSTICS                   {COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}======================================================================{COLOR_RESET}\n")

    has_failures = False
    has_warnings = False

    # ----------------------------------------------------
    # 1. Python Environment Check
    # ----------------------------------------------------
    print(f"{COLOR_BOLD}Checking Python Installation...{COLOR_RESET}")
    python_ver = sys.version.split()[0]
    print_status("INFO", f"Python version: {python_ver} (Executable: {sys.executable})", COLOR_CYAN)

    # ----------------------------------------------------
    # 2. Virtual Environment (VENV) Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}Checking Virtual Environment (VENV)...{COLOR_RESET}")
    in_venv = (sys.prefix != sys.base_prefix) or ("VIRTUAL_ENV" in os.environ)
    if in_venv:
        print_status("PASS", "Virtual environment is active.", COLOR_GREEN)
    else:
        print_status("FAIL", "Virtual environment (VENV) is NOT active!", COLOR_RED)
        print("\n   --> ACTION REQUIRED to activate VENV on Windows VS Code:")
        print("      1. Open the command palette in VS Code (Ctrl + Shift + P).")
        print("      2. Type and select: 'Python: Select Interpreter'.")
        print("      3. Choose the option pointing to '.venv\\Scripts\\python.exe'.")
        print("      4. Open a NEW terminal (Ctrl + Shift + `) to trigger auto-activation.")
        print("      Alternatively, activate manually in PowerShell:")
        print("         .\\.venv\\Scripts\\Activate.ps1")
        print("      Or in Command Prompt (cmd.exe):")
        print("         .venv\\Scripts\\activate.bat\n")
        has_failures = True

    # ----------------------------------------------------
    # 3. Dependencies check (requirements.txt)
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}Checking Installed Python Dependencies...{COLOR_RESET}")
    req_file_path = Path(__file__).resolve().parent / "requirements.txt"
    
    # Mapping requirements library names to actual importable modules
    libraries_map = {
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "mysql-connector-python": "mysql.connector",
        "openai": "openai",
        "google-genai": "google.genai",
        "SpeechRecognition": "speech_recognition",
        "pyttsx3": "pyttsx3"
    }

    if not req_file_path.exists():
        print_status("WARNING", f"Could not find requirements.txt at {req_file_path}. Skipping checks.", COLOR_YELLOW)
        has_warnings = True
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
                    # google-genai is imported as `from google import genai`
                    from google import genai
                else:
                    __import__(import_name)
                print_status("PASS", f"Module '{lib_name}' is installed.", COLOR_GREEN)
            except ImportError:
                print_status("FAIL", f"Module '{lib_name}' is MISSING!", COLOR_RED)
                missing_libs.append(lib_name)
                has_failures = True

        if missing_libs:
            print("\n   --> ACTION REQUIRED to install missing packages:")
            print("      Ensure your internet is active and run:")
            print("         pip install -r requirements.txt")
            print("      If your school computer is OFFLINE, run this in the terminal with your USB drive wheels:")
            print("         pip install --no-index --find-links=./wheels -r requirements.txt\n")

    # ----------------------------------------------------
    # 4. MySQL Service Connectivity Check (Port 3306)
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}Checking MySQL Local Port (3306)...{COLOR_RESET}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    mysql_port_open = s.connect_ex(("127.0.0.1", 3306)) == 0
    s.close()

    if mysql_port_open:
        print_status("PASS", "MySQL server is listening on port 3306.", COLOR_GREEN)
    else:
        print_status("WARNING", "MySQL server is NOT listening on port 3306!", COLOR_YELLOW)
        print("   * Note: The application will automatically fall back to SQLite.")
        print("   --> ACTION REQUIRED to set up MySQL (if you want to use MySQL instead of SQLite fallback):")
        print("      1. Verify MySQL Community Server is installed on your school PC.")
        print("      2. Verify MySQL service is started (open Services in Windows, find 'MySQL80', and click Start).")
        has_warnings = True

    # ----------------------------------------------------
    # 5. Database Config and Schema Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}Checking Database Connection...{COLOR_RESET}")
    sys.path.append(str(Path(__file__).resolve().parent))
    
    try:
        from PMLA_SCWE import config, database
        cfg = config.DATABASE_CONFIG
        print_status("INFO", f"Config parameters -> host={cfg['host']}, user={cfg['user']}, database={cfg['database']}, port={cfg['port']}", COLOR_CYAN)
        
        # Test MySQL connection if port is open
        if mysql_port_open:
            try:
                import mysql.connector
                conn = mysql.connector.connect(
                    host=cfg["host"],
                    user=cfg["user"],
                    password=cfg["password"],
                    port=cfg["port"]
                )
                print_status("PASS", "Successfully authenticated with MySQL server.", COLOR_GREEN)
                
                # Check if database schema exists
                cursor = conn.cursor()
                cursor.execute(f"SHOW DATABASES LIKE '{cfg['database']}'")
                db_exists = cursor.fetchone() is not None
                
                if db_exists:
                    print_status("PASS", f"Database '{cfg['database']}' exists in MySQL.", COLOR_GREEN)
                    cursor.execute(f"USE {cfg['database']}")
                    
                    # Verify tables
                    cursor.execute("SHOW TABLES")
                    tables = [t[0].lower() for t in cursor.fetchall()]
                    required_tables = ["students", "attendance", "cyber_audit", "admin_login"]
                    missing_tables = [t for t in required_tables if t not in tables]
                    
                    if not missing_tables:
                        print_status("PASS", "All required database tables exist in MySQL.", COLOR_GREEN)
                        # Check seeding
                        cursor.execute("SELECT COUNT(*) FROM Students")
                        students_cnt = cursor.fetchone()[0]
                        print_status("INFO", f"Seeded student records in MySQL: {students_cnt}", COLOR_CYAN)
                        if students_cnt == 0:
                            print_status("WARNING", "MySQL database is empty! Please run 'python -m PMLA_SCWE.seed_data' to seed.", COLOR_YELLOW)
                            has_warnings = True
                    else:
                        print_status("FAIL", f"Missing tables in MySQL: {', '.join(missing_tables)}", COLOR_RED)
                        print("   --> ACTION REQUIRED: Run the SQL schema to initialize tables:")
                        print("      Open schema.sql in MySQL Workbench and execute all statements.")
                        has_failures = True
                else:
                    print_status("FAIL", f"Database '{cfg['database']}' does not exist in MySQL.", COLOR_RED)
                    print("   --> ACTION REQUIRED: Initialize database:")
                    print("      Run MySQL schema.sql inside MySQL Workbench or run Python seeder: python -m PMLA_SCWE.seed_data")
                    has_failures = True
                    
                cursor.close()
                conn.close()
            except mysql.connector.Error as err:
                print_status("FAIL", f"Failed to connect to MySQL database: {err}", COLOR_RED)
                print("   --> ACTION REQUIRED: Update your configuration:")
                print("      Open 'PMLA_SCWE/config.py' and change DATABASE_CONFIG settings (user, password) to match your local setup.")
                has_failures = True
        else:
            print_status("INFO", "Skipping MySQL connectivity checks because port 3306 is closed.", COLOR_CYAN)
            
    except ImportError as e:
        print_status("FAIL", f"Could not load package modules to perform database checks: {e}", COLOR_RED)
        has_failures = True

    # ----------------------------------------------------
    # 6. SQLite Fallback Database Check
    # ----------------------------------------------------
    print(f"\n{COLOR_BOLD}Checking SQLite Fallback Database...{COLOR_RESET}")
    sqlite_db_path = Path(__file__).resolve().parent / "pmla_scwe_fallback.db"
    if sqlite_db_path.exists():
        print_status("INFO", f"SQLite fallback database file found: {sqlite_db_path}", COLOR_CYAN)
        try:
            import sqlite3
            s_conn = sqlite3.connect(sqlite_db_path)
            s_curr = s_conn.cursor()
            s_curr.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0].lower() for t in s_curr.fetchall()]
            required_tables = ["students", "attendance", "cyber_audit", "admin_login"]
            missing_tables = [t for t in required_tables if t not in tables]
            
            if not missing_tables:
                print_status("PASS", "SQLite fallback tables are fully initialized.", COLOR_GREEN)
                s_curr.execute("SELECT COUNT(*) FROM Students")
                cnt = s_curr.fetchone()[0]
                print_status("INFO", f"Student records in SQLite: {cnt}", COLOR_CYAN)
            else:
                print_status("WARNING", f"SQLite schema is missing tables: {', '.join(missing_tables)}", COLOR_YELLOW)
                print("   * Note: The app will auto-create these schema tables when run.")
                has_warnings = True
                
            s_curr.close()
            s_conn.close()
        except Exception as e:
            print_status("WARNING", f"Failed to read SQLite fallback database: {e}", COLOR_YELLOW)
            has_warnings = True
    else:
        print_status("WARNING", "SQLite fallback database file 'pmla_scwe_fallback.db' is missing.", COLOR_YELLOW)
        print("   * Note: The file will be created automatically when you run the seeder or start the main app.")
        has_warnings = True

    # ----------------------------------------------------
    # Final Diagnostic Summary
    # ----------------------------------------------------
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}======================================================================{COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}                          DIAGNOSTIC REPORT                           {COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}======================================================================{COLOR_RESET}")
    
    if has_failures:
        print(f"\n{COLOR_RED}{COLOR_BOLD}STATUS: CRITICAL PROBLEMS DETECTED!{COLOR_RESET}")
        print("   Please scroll up and check all the [FAIL] steps.")
        print("   Follow the listed '--> ACTION REQUIRED' steps to fix the issues.")
        sys.exit(1)
    elif has_warnings:
        print(f"\n{COLOR_YELLOW}{COLOR_BOLD}STATUS: SYSTEM READY WITH WARNINGS{COLOR_RESET}")
        print("   MySQL server is offline, but SQLite fallback mode is fully functional.")
        print("   You can run the application, which will save all records locally.")
    else:
        print(f"\n{COLOR_GREEN}{COLOR_BOLD}STATUS: ALL CHECKS PASSED SUCCESSFULLY!{COLOR_RESET}")
        print("   Your system, dependencies, and database connections are perfectly set up.")
        print("   You can start the app with: python -m PMLA_SCWE.main")
        
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}======================================================================{COLOR_RESET}\n")


if __name__ == "__main__":
    run_diagnostics()
