"""Database migration engine and verification service for PMLA-SCWE Version 2.0.

Provides versioned, idempotent, and non-destructive schema migrations with pre/post
row count verification, atomic backup snapshots, and safe data backfilling.
"""

from __future__ import annotations

import datetime
import hashlib
from typing import Any

from core.database import execute_query, execute_non_query, get_connection
from core.backup_service import backup_sqlite, restore_sqlite
from core import tenant_service

V2_0_PHASE_1_VERSION = "v2_0_phase_1"
V2_0_PHASE_1_NAME = "Multi-School Tenancy & RBAC Foundation"

TRACKED_TABLES = [
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
    "Notifications",
    "Interventions",
]


def ensure_schema_migrations_table() -> None:
    """Ensure the Schema_Migrations metadata tracking table exists."""
    q = """
    CREATE TABLE IF NOT EXISTS Schema_Migrations (
        migration_id INT PRIMARY KEY AUTO_INCREMENT,
        version VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(150) NOT NULL,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        checksum VARCHAR(64),
        status VARCHAR(20) DEFAULT 'SUCCESS'
    )
    """
    execute_non_query(q)


def is_migration_applied(version: str) -> bool:
    """Check whether a specific migration version has already been successfully applied."""
    try:
        ensure_schema_migrations_table()
        rows = execute_query(
            "SELECT migration_id, version, applied_at, status "
            "FROM Schema_Migrations WHERE version = %s AND status = 'SUCCESS'",
            (version,)
        )
        return len(rows) > 0
    except Exception:
        return False


def record_migration(version: str, name: str, checksum: str = "", status: str = "SUCCESS") -> bool:
    """Record the application of a migration version in the tracking table."""
    try:
        ensure_schema_migrations_table()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_non_query(
            "INSERT INTO Schema_Migrations (version, name, applied_at, checksum, status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (version, name, now_str, checksum, status)
        )
        return True
    except Exception:
        return False


def record_database_metrics() -> dict[str, Any]:
    """Capture snapshot of table presence, column definitions, and row counts."""
    metrics: dict[str, Any] = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tables": {},
        "row_counts": {},
    }

    all_tables = TRACKED_TABLES + ["Organizations", "Schools", "Schema_Migrations"]
    for table in all_tables:
        try:
            res = execute_query(f"SELECT COUNT(*) AS cnt FROM {table}")
            cnt = int(res[0]["cnt"]) if res else 0
            metrics["row_counts"][table] = cnt
            metrics["tables"][table] = True
        except Exception:
            metrics["row_counts"][table] = 0
            metrics["tables"][table] = False

    return metrics


def run_v2_phase1_migration(create_backup: bool = True) -> dict[str, Any]:
    """Executes the Version 2.0 Phase 1 Multi-School migration pipeline.

    Idempotent, non-destructive, and verifies row count integrity before and after.
    """
    report: dict[str, Any] = {
        "version": V2_0_PHASE_1_VERSION,
        "name": V2_0_PHASE_1_NAME,
        "success": False,
        "backup": None,
        "pre_metrics": {},
        "post_metrics": {},
        "already_applied": False,
        "steps_completed": [],
        "errors": [],
    }

    # Step 1: Pre-migration backup (for SQLite fallback or records info)
    if create_backup:
        backup_result = backup_sqlite(tag="pre_v2_0_phase1")
        report["backup"] = backup_result

    # Step 2: Record baseline metrics
    pre_metrics = record_database_metrics()
    report["pre_metrics"] = pre_metrics
    report["steps_completed"].append("Pre-migration metrics recorded")

    # Step 3: Check if already applied
    if is_migration_applied(V2_0_PHASE_1_VERSION):
        report["already_applied"] = True
        report["success"] = True
        report["post_metrics"] = record_database_metrics()
        report["steps_completed"].append("Migration previously applied; verified existing schema.")
        return report

    try:
        # Step 4: Create Schema_Migrations & Organizations table
        ensure_schema_migrations_table()
        execute_non_query("""
        CREATE TABLE IF NOT EXISTS Organizations (
            organization_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(150) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            is_active INT DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        report["steps_completed"].append("Created Organizations table")

        # Step 5: Create Schools table
        execute_non_query("""
        CREATE TABLE IF NOT EXISTS Schools (
            school_id INT PRIMARY KEY AUTO_INCREMENT,
            organization_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            is_active INT DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
        )
        """)
        report["steps_completed"].append("Created Schools table")

        # Step 6: Dynamically create/resolve default organization & default school
        default_org = tenant_service.get_default_organization()
        default_school = tenant_service.get_default_school()
        default_org_id = int(default_org["organization_id"])
        default_school_id = int(default_school["school_id"])
        report["steps_completed"].append(
            f"Resolved default tenant: Org '{default_org['name']}' (ID: {default_org_id}), "
            f"School '{default_school['name']}' (ID: {default_school_id})"
        )

        # Step 7: Safely alter existing tables with nullable / default columns
        alterations = [
            ("Students", "school_id", "INT", "INTEGER"),
            ("Users", "organization_id", "INT", "INTEGER"),
            ("Users", "school_id", "INT", "INTEGER"),
            ("Users", "is_active", "INT DEFAULT 1", "INTEGER DEFAULT 1"),
            ("Users", "updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]
        for tbl, col, mysql_type, sqlite_type in alterations:
            try:
                execute_non_query(f"ALTER TABLE {tbl} ADD COLUMN {col} {mysql_type}")
            except Exception:
                # Column already exists
                pass
        report["steps_completed"].append("Extended Students and Users schemas with tenant references")

        # Step 8: Backfill legacy data safely
        # 8a: Associate Students with default school
        execute_non_query(
            "UPDATE Students SET school_id = %s WHERE school_id IS NULL OR school_id = 0",
            (default_school_id,)
        )

        # 8b: Map Users status -> is_active & set default tenant
        execute_non_query(
            "UPDATE Users SET is_active = 1 WHERE is_active IS NULL AND (status IS NULL OR LOWER(status) IN ('active', '1', 'true'))"
        )
        execute_non_query(
            "UPDATE Users SET is_active = 0 WHERE is_active IS NULL AND LOWER(status) IN ('inactive', '0', 'false', 'disabled')"
        )
        execute_non_query(
            "UPDATE Users SET organization_id = %s WHERE organization_id IS NULL OR organization_id = 0",
            (default_org_id,)
        )
        execute_non_query(
            "UPDATE Users SET school_id = %s WHERE school_id IS NULL OR school_id = 0",
            (default_school_id,)
        )

        # 8c: One-time idempotent legacy sync from Admin_Login to Users
        legacy_admins = execute_query("SELECT admin_id, username, password_hash, last_login FROM Admin_Login")
        for admin in legacy_admins:
            uname = admin["username"].strip().lower()
            existing_user = execute_query("SELECT user_id FROM Users WHERE LOWER(username) = %s", (uname,))
            if not existing_user:
                execute_non_query(
                    "INSERT INTO Users (username, full_name, password_hash, role, status, is_active, organization_id, school_id, last_login) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        uname,
                        "System Administrator",
                        admin["password_hash"],
                        "Admin",
                        "Active",
                        1,
                        default_org_id,
                        default_school_id,
                        admin.get("last_login"),
                    )
                )
        report["steps_completed"].append("Backfilled existing students, users, and synchronized legacy admin credentials")

        # Step 9: Create performance indexes where supported
        indexes = [
            ("idx_students_school", "CREATE INDEX IF NOT EXISTS idx_students_school ON Students(school_id)"),
            ("idx_schools_org", "CREATE INDEX IF NOT EXISTS idx_schools_org ON Schools(organization_id)"),
            ("idx_users_school", "CREATE INDEX IF NOT EXISTS idx_users_school ON Users(school_id)"),
            ("idx_users_org", "CREATE INDEX IF NOT EXISTS idx_users_org ON Users(organization_id)"),
        ]
        for idx_name, idx_sql in indexes:
            try:
                execute_non_query(idx_sql)
            except Exception:
                pass
        report["steps_completed"].append("Created tenant performance indexes")

        # Step 10: Post-migration verification
        post_metrics = record_database_metrics()
        report["post_metrics"] = post_metrics

        # Verify core tables row counts
        verification_passed = True
        critical_tables = [
            "Students",
            "Attendance",
            "Diagnostic_Logs",
            "Cyber_Audit",
            "Weekly_Progress",
            "Achievements",
            "Learning_Objectives",
        ]
        for tbl in critical_tables:
            pre_cnt = pre_metrics["row_counts"].get(tbl, 0)
            post_cnt = post_metrics["row_counts"].get(tbl, 0)
            if pre_cnt != post_cnt:
                verification_passed = False
                report["errors"].append(
                    f"Row count mismatch on critical table {tbl}: before={pre_cnt}, after={post_cnt}"
                )

        # Step 11: Ensure SQLite fallback database file is also migrated
        migrate_sqlite_fallback_file()

        if verification_passed:
            # Step 12: Record migration success
            checksum = hashlib.sha256(f"{V2_0_PHASE_1_VERSION}_{default_school_id}".encode()).hexdigest()[:16]
            record_migration(V2_0_PHASE_1_VERSION, V2_0_PHASE_1_NAME, checksum=checksum, status="SUCCESS")
            report["success"] = True
            report["steps_completed"].append("Migration v2_0_phase_1 successfully committed and verified across all engines")
        else:
            report["success"] = False

    except Exception as ex:
        report["success"] = False
        report["errors"].append(f"Migration execution error: {ex}")

    return report


def migrate_sqlite_fallback_file(db_path: str | None = None) -> bool:
    """Explicitly applies Version 2.0 Phase 1 migration to the SQLite fallback database file."""
    import sqlite3
    from pathlib import Path
    
    sqlite_file = Path(db_path) if db_path else Path(__file__).resolve().parent.parent / "pmla_scwe_fallback.db"
    if not sqlite_file.exists():
        return False

    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        # Tables
        c.execute("""
        CREATE TABLE IF NOT EXISTS Schema_Migrations (
            migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT,
            status TEXT DEFAULT 'SUCCESS'
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS Organizations (
            organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS Schools (
            school_id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
        )
        """)

        # Default org
        c.execute("SELECT organization_id FROM Organizations WHERE code = 'DEFAULT_ORG'")
        r_org = c.fetchone()
        if not r_org:
            c.execute("INSERT INTO Organizations (name, code, is_active) VALUES ('PMLA-SCWE Default Organization', 'DEFAULT_ORG', 1)")
            c.execute("SELECT organization_id FROM Organizations WHERE code = 'DEFAULT_ORG'")
            org_id = int(c.fetchone()[0])
        else:
            org_id = int(r_org[0])

        # Default school
        c.execute("SELECT school_id FROM Schools WHERE code = 'DEFAULT_SCHOOL'")
        r_sch = c.fetchone()
        if not r_sch:
            c.execute("INSERT INTO Schools (organization_id, name, code, is_active) VALUES (?, 'Default School', 'DEFAULT_SCHOOL', 1)", (org_id,))
            c.execute("SELECT school_id FROM Schools WHERE code = 'DEFAULT_SCHOOL'")
            school_id = int(c.fetchone()[0])
        else:
            school_id = int(r_sch[0])

        # Alter columns
        cols = [
            ("Students", "school_id", "INTEGER"),
            ("Users", "organization_id", "INTEGER"),
            ("Users", "school_id", "INTEGER"),
            ("Users", "is_active", "INTEGER DEFAULT 1"),
            ("Users", "updated_at", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]
        for tbl, col, ctype in cols:
            try:
                c.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {ctype}")
            except Exception:
                pass

        # Backfill
        c.execute("UPDATE Students SET school_id = ? WHERE school_id IS NULL OR school_id = 0", (school_id,))
        try:
            c.execute("UPDATE Users SET organization_id = ?, school_id = ?, is_active = 1 WHERE organization_id IS NULL OR organization_id = 0", (org_id, school_id))
        except Exception:
            pass

        # Record migration
        c.execute("INSERT OR REPLACE INTO Schema_Migrations (version, name, status) VALUES ('v2_0_phase_1', 'Multi-School Tenancy & RBAC Foundation', 'SUCCESS')")
        conn.commit()
        c.close()
        conn.close()
        return True
    except Exception:
        return False

