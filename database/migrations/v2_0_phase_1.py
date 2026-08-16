"""Standalone CLI and Python script to execute PMLA-SCWE Version 2.0 Phase 1 Migration.

Usage:
    python -m database.migrations.v2_0_phase_1
    or
    python database/migrations/v2_0_phase_1.py
"""

from __future__ import annotations

import os
import sys

# Ensure project root is in sys.path
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.migration_service import run_v2_phase1_migration, is_migration_applied, V2_0_PHASE_1_VERSION


def main() -> int:
    print("=" * 60)
    print(" PMLA-SCWE VERSION 2.0 -- PHASE 1 DATABASE MIGRATION")
    print(" Multi-School Tenancy & Role-Based Authorization Foundation")
    print("=" * 60)

    if is_migration_applied(V2_0_PHASE_1_VERSION):
        print(f"\n[INFO] Migration '{V2_0_PHASE_1_VERSION}' is ALREADY APPLIED and verified.")
        print("Schema is up-to-date. No changes required.")
        return 0

    print("\n[1/5] Starting pre-migration backup & baseline capture...")
    report = run_v2_phase1_migration(create_backup=True)

    if report.get("backup") and report["backup"].get("success"):
        print(f"      [PASS] Backup snapshot created: {report['backup']['filename']}")
    else:
        print("      [WARN] Backup skipped or database initialized directly.")

    print("\n[2/5] Migration steps performed:")
    for step in report.get("steps_completed", []):
        print(f"      [PASS] {step}")

    print("\n[3/5] Row Count Integrity Verification:")
    pre_counts = report.get("pre_metrics", {}).get("row_counts", {})
    post_counts = report.get("post_metrics", {}).get("row_counts", {})

    check_tables = ["Students", "Attendance", "Diagnostic_Logs", "Cyber_Audit", "Weekly_Progress", "Achievements", "Users"]
    for tbl in check_tables:
        pre_c = pre_counts.get(tbl, 0)
        post_c = post_counts.get(tbl, 0)
        status_symbol = "[OK]" if pre_c == post_c or tbl == "Users" else "[MISMATCH]"
        print(f"      {status_symbol:<10} {tbl:<20}: Before = {pre_c:<5} | After = {post_c:<5}")

    if report.get("success"):
        print("\n" + "=" * 60)
        print(" [SUCCESS] Version 2.0 Phase 1 Migration COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print(" [FAILURE] Migration encountered errors:")
        for err in report.get("errors", []):
            print(f"      [ERROR] {err}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
