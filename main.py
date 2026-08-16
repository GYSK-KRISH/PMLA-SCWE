"""Main entry point for PMLA-SCWE.

Launches the CustomTkinter desktop app by default.
Run with '--web' option to start the Flask web application instead.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file in the workspace root
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def parse_args():
    parser = argparse.ArgumentParser(
        description="PMLA-SCWE: Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start the Flask web presentation server instead of the desktop interface"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Core database initialization
    from core.database import initialize_database, get_db_status, execute_query
    from core import auth_service

    print("=== Initializing PMLA-SCWE Database ===")
    initialized = initialize_database()
    status = get_db_status()
    print(f"Database setup complete. Status: {status['display']}")

    # Guarantee that at least one admin exists in the system
    try:
        admins = execute_query("SELECT COUNT(*) AS cnt FROM Users")
        if not admins or int(admins[0].get("cnt", 0)) == 0:
            auth_service.create_admin("admin", "admin123")
            print("Default administrator created successfully:")
            print("  Username: admin")
            print("  Password: admin123")
            
        # Compile notification alerts at boot
        from core.notification_service import generate_system_alerts
        generate_system_alerts()
    except Exception as e:
        print(f"Warning: Could not verify or seed default administrator: {e}")

    if args.web:
        print("\n=== Launching Flask Web Server ===")
        # Dynamic import of web app module to prevent GUI environments requiring web imports unnecessarily
        from web.app import run_web_server
        run_web_server()
    else:
        print("\n=== Launching PySide6 Desktop Client ===")
        # Dynamic import of desktop app
        from desktop.app import run
        run()


if __name__ == "__main__":
    main()
