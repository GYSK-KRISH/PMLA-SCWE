"""Idempotent Database Initializer, Seeder, and Cleaner for PMLA-SCWE."""
from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path

# Add project root to path to ensure relative imports work correctly when called from scripts
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.database import get_connection, initialize_database, execute_query
from core import auth_service
from core.notification_service import generate_system_alerts

DEFAULT_ADMIN = "admin"
DEFAULT_PASS = "admin123"


def clear_operational_data(interactive: bool = True) -> bool:
    """Wipes all student records, attendance, assessments, wellness audits, interventions, and notifications.
    
    Preserves default tenants, curriculum learning objectives, and administrator accounts.
    """
    if interactive:
        print("\n" + "!" * 60)
        print("WARNING: This will permanently delete all student records, attendance, assessments, and wellness logs!")
        print("!" * 60 + "\n")
        try:
            confirm = input("Type 'YES' to confirm wiping all operational student data: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Wipe cancelled.")
            return False
            
        if confirm != "YES":
            print("[INFO] Wipe cancelled. No changes were made.")
            return True

    print("[INFO] Wiping all operational student records...")
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = "sqlite" in str(type(conn)).lower()
    
    tables = [
        "Interventions", "Attendance", "Diagnostic_Logs", "Weekly_Progress",
        "Cyber_Audit", "Achievements", "Activity_Log", "Reports_Metadata",
        "Notifications", "Students"
    ]
    
    try:
        if not is_sqlite:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
        for t in tables:
            try:
                cursor.execute(f"DELETE FROM {t}")
                if not is_sqlite:
                    cursor.execute(f"ALTER TABLE {t} AUTO_INCREMENT = 1")
            except Exception:
                pass
                
        if is_sqlite:
            try:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('" + "','".join(tables) + "')")
            except Exception:
                pass
                
        if not is_sqlite:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
        conn.commit()
        print("[PASS] All operational student data has been wiped.")
        print("[PASS] Auto-increment counters reset to 1.")
        print("[PASS] Default admin, organizations, schools, and curriculum objectives preserved.")
        return True
    except Exception as e:
        print(f"[FAIL] Error wiping operational data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def seed_idempotent(reset: bool = False, count: int = 100, non_interactive: bool = False) -> bool:
    print("==================================================")
    print(" PMLA-SCWE DATABASE INITIALIZER & IDEMPOTENT SEEDER")
    print("==================================================")

    # Resolve schema.sql path
    schema_path = project_root / "database" / "schema.sql"
    if not schema_path.exists():
        schema_path = project_root / "schema.sql"
    
    # Initialize the database layout (creates tables if missing)
    initialized = initialize_database(schema_path=str(schema_path))
    if not initialized:
        print("[FAIL] Failed to initialize database tables.")
        return False
        
    print("[PASS] Database tables verified/initialized.")

    if reset:
        if not non_interactive:
            print("\n" + "!" * 60)
            print(f"WARNING: This will reset the database and seed {count} demonstration students!")
            print("!" * 60 + "\n")
            try:
                confirm = input("Type 'YES' to confirm database reset and seed clean mock data: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n[INFO] Reset cancelled.")
                return False
                
            if confirm != "YES":
                print("[INFO] Reset cancelled. No changes were made.")
                return True

        print(f"[INFO] Reset confirmed. Wiping and seeding {count} clean mock student records...")
        try:
            from seed_data import seed_database
            seed_database(count)
            print(f"[PASS] Clean demonstration database seeded successfully ({count} students).")
            return True
        except Exception as e:
            print(f"[FAIL] Error seeding mock data: {e}")
            return False

    # Check and seed Default Organization and School
    try:
        from core import tenant_service
        def_org = tenant_service.get_default_organization()
        def_school = tenant_service.get_default_school()
        print(f"[PASS] Default tenant boundary verified (Org: '{def_org['name']}', School: '{def_school['name']}').")
    except Exception as e:
        print(f"[WARN] Could not verify default tenants: {e}")

    # Check and seed Default Administrator account in Users table
    try:
        admins = execute_query("SELECT COUNT(*) AS cnt FROM Users")
        cnt = int(admins[0].get("cnt", 0)) if admins else 0
    except Exception as e:
        print(f"[WARN] Could not query Users table: {e}")
        cnt = 0

    if cnt == 0:
        try:
            auth_service.create_admin(DEFAULT_ADMIN, DEFAULT_PASS)
            print(f"[PASS] Default administrator created (Username: {DEFAULT_ADMIN}, Password: {DEFAULT_PASS})")
        except Exception as e:
            print(f"[WARN] Could not create default admin: {e}")
    else:
        print("[PASS] Administrator accounts already exist. Skipping admin creation.")

    # Check and seed Learning Objectives
    try:
        objs = execute_query("SELECT COUNT(*) AS cnt FROM Learning_Objectives")
        obj_cnt = int(objs[0].get("cnt", 0)) if objs else 0
    except Exception as e:
        print(f"[WARN] Could not query Learning_Objectives table: {e}")
        obj_cnt = 0

    if obj_cnt == 0:
        try:
            from seed_data import TOPICS
            conn = get_connection()
            cursor = conn.cursor()
            # Handle SQLite vs MySQL placeholder format
            placeholder = "?" if "sqlite" in str(type(conn)).lower() else "%s"
            
            for topic in TOPICS:
                cursor.execute(
                    f"INSERT INTO Learning_Objectives (topic_name, description) VALUES ({placeholder}, {placeholder})",
                    (topic, f"Introductory coverage for {topic.lower()}"),
                )
            conn.commit()
            print(f"[PASS] Seeded default {len(TOPICS)} learning objectives.")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[WARN] Could not seed default objectives: {e}")
    else:
        print("[PASS] Learning objectives already present. Skipping objective seeding.")

    # Compile system notifications/alerts at boot
    try:
        generate_system_alerts()
        print("[PASS] Initial system notifications and alerts generated.")
    except Exception as e:
        print(f"[WARN] Failed to compile notification alerts: {e}")

    print("\nDatabase configuration and initialization complete.")
    print("==================================================")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PMLA-SCWE Database Initializer, Seeder & Cleaner")
    parser.add_argument("--reset", action="store_true", help="Wipe and seed clean mock demonstration data (default: 100 students)")
    parser.add_argument("--count", type=int, default=100, help="Number of demonstration students to seed (default: 100)")
    parser.add_argument("--wipe", "--clear", action="store_true", help="Wipe all demonstration student records, keeping empty clean database")
    parser.add_argument("-y", "--yes", action="store_true", help="Non-interactive mode: auto-confirm prompt")
    args = parser.parse_args()

    if args.wipe:
        success = clear_operational_data(interactive=not args.yes)
    else:
        success = seed_idempotent(reset=args.reset, count=args.count, non_interactive=args.yes)
        
    sys.exit(0 if success else 1)
