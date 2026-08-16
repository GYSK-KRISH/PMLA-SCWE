"""Unit tests for PMLA-SCWE Version 2.0 Phase 1 Migration Pipeline."""

from __future__ import annotations

import unittest
from pathlib import Path
from core.database import initialize_database, execute_query
from core.migration_service import (
    run_v2_phase1_migration,
    is_migration_applied,
    record_database_metrics,
    V2_0_PHASE_1_VERSION,
)
from core.backup_service import backup_sqlite, list_backups, generate_mysqldump_instructions


class TestV2Phase1Migration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_backup_service_sqlite(self):
        """Verify SQLite snapshot creation, file persistence, and metadata cataloging."""
        backup_res = backup_sqlite(tag="unit_test_backup")
        self.assertTrue(backup_res["success"])
        self.assertIsNotNone(backup_res["backup_path"])
        self.assertTrue(Path(backup_res["backup_path"]).exists())
        self.assertTrue(backup_res["size_bytes"] > 0)

        # Catalog listing
        backups = list_backups()
        self.assertTrue(len(backups) > 0)
        self.assertTrue(any(b["filename"] == backup_res["filename"] for b in backups))

    def test_mysqldump_instruction_generator(self):
        """Verify mysqldump command generator outputs valid command syntax."""
        instructions = generate_mysqldump_instructions()
        self.assertIn("mysqldump", instructions["dump_command"])
        self.assertIn("pmla_scwe", instructions["dump_command"])
        self.assertIn("mysql", instructions["restore_command"])

    def test_migration_pipeline_idempotency(self):
        """Verify running the migration returns success and marks version as applied."""
        report = run_v2_phase1_migration(create_backup=False)
        self.assertTrue(report["success"])
        self.assertTrue(is_migration_applied(V2_0_PHASE_1_VERSION))

        # Re-running must be idempotent and indicate already_applied
        second_run = run_v2_phase1_migration(create_backup=False)
        self.assertTrue(second_run["success"])
        self.assertTrue(second_run["already_applied"])

    def test_tenant_columns_and_data_integrity(self):
        """Verify all students and users have valid tenant IDs attached."""
        # Query students with NULL school_id (should be 0)
        null_students = execute_query("SELECT COUNT(*) AS cnt FROM Students WHERE school_id IS NULL OR school_id = 0")
        self.assertEqual(int(null_students[0]["cnt"]), 0)

        # Query users with NULL organization_id or school_id (should be 0)
        null_users = execute_query(
            "SELECT COUNT(*) AS cnt FROM Users WHERE organization_id IS NULL OR organization_id = 0 OR school_id IS NULL OR school_id = 0"
        )
        self.assertEqual(int(null_users[0]["cnt"]), 0)

        # Query organizations table
        orgs = execute_query("SELECT organization_id, code FROM Organizations WHERE code = 'DEFAULT_ORG'")
        self.assertTrue(len(orgs) >= 1)

        # Query schools table
        schools = execute_query("SELECT school_id, code FROM Schools WHERE code = 'DEFAULT_SCHOOL'")
        self.assertTrue(len(schools) >= 1)

    def test_schema_migrations_record(self):
        """Verify Schema_Migrations table stores applied version properly."""
        rows = execute_query(
            "SELECT version, name, status FROM Schema_Migrations WHERE version = %s",
            (V2_0_PHASE_1_VERSION,)
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
