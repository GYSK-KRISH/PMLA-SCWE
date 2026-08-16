# PMLA-SCWE Version 2.0 — Migration Guide (Phase 1)
## Safe Multi-School Tenancy & Schema Upgrade Runbook

---

## 1. Overview & Safety Principles

Version 2.0 Phase 1 upgrades existing single-school databases into multi-school multi-tenant structures without data loss, downtime, or account disruption.

### Safety Guarantees
- **Atomic Snapshots**: Automated SQLite snapshot backup to `database/backups/` before any DDL operations.
- **Idempotency**: Execution tracked in `Schema_Migrations` table (`version = 'v2_0_phase_1'`).
- **Zero Account Resets**: All PBKDF2 and legacy SHA-256 password hashes are preserved.
- **Row Count Assertions**: Before and after row count equality is verified automatically.

---

## 2. Automated Migration Execution

### Option A: Via Python Module (Recommended)
```powershell
.venv\Scripts\python.exe -m database.migrations.v2_0_phase_1
```

### Option B: Programmatic Execution
```python
from core.migration_service import run_v2_phase1_migration

report = run_v2_phase1_migration(create_backup=True)
if report["success"]:
    print("Migration successful! Steps:", report["steps_completed"])
else:
    print("Migration failed:", report["errors"])
```

---

## 3. Step-by-Step Migration Pipeline

```
 [1] Backup
     │── Creates timestamped SQLite snapshot: database/backups/pmla_scwe_fallback_pre_v2_0_phase1_*.db
     ▼
 [2] Pre-Migration Metric Baseline
     │── Counts rows in Students, Attendance, Diagnostic_Logs, Cyber_Audit, Users, etc.
     ▼
 [3] Version Check
     │── Queries Schema_Migrations. If v2_0_phase_1 is applied, skips and exits cleanly.
     ▼
 [4] DDL Schema Execution
     │── Creates Schema_Migrations, Organizations, Schools tables (IF NOT EXISTS).
     ▼
 [5] Dynamic Default Tenant Provisioning
     │── PMLA-SCWE Default Organization (code: DEFAULT_ORG)
     │── Default School (code: DEFAULT_SCHOOL)
     ▼
 [6] Safe Column Additions
     │── Adds school_id to Students
     │── Adds organization_id, school_id, is_active, updated_at to Users
     ▼
 [7] Data Backfilling
     │── Associates existing 99 Students with Default School ID
     │── Maps Users status -> is_active (Active -> 1, Inactive -> 0)
     │── Associates existing Users with Default Org & School IDs
     │── Synchronizes legacy Admin_Login accounts into Users (one-time idempotent sync)
     ▼
 [8] Performance Indexes
     │── idx_students_school ON Students(school_id)
     │── idx_schools_org ON Schools(organization_id)
     │── idx_users_school ON Users(school_id)
     ▼
 [9] Row Count Integrity Verification
     │── Verifies critical table counts before == after (Zero Data Loss)
     ▼
[10] Commit Version
     └── Inserts v2_0_phase_1 record into Schema_Migrations
```

---

## 4. Verification Checklist

Run verification script or unit tests to confirm:
```powershell
.venv\Scripts\python.exe -m unittest tests.test_v2_phase1_migration tests.test_tenant_service tests.test_authorization
```

### Manual Verification Queries
```sql
-- 1. Verify Default Organization
SELECT * FROM Organizations WHERE code = 'DEFAULT_ORG';

-- 2. Verify Default School
SELECT * FROM Schools WHERE code = 'DEFAULT_SCHOOL';

-- 3. Verify Students Tenant Association
SELECT school_id, COUNT(*) FROM Students GROUP BY school_id;

-- 4. Verify Users Tenant and Role Association
SELECT user_id, username, role, status, is_active, organization_id, school_id FROM Users;

-- 5. Verify Applied Migration
SELECT * FROM Schema_Migrations WHERE version = 'v2_0_phase_1';
```

---

## 5. Rollback & Disaster Recovery Procedures

### SQLite Rollback
If a rollback is required, restore from the pre-migration snapshot:
```python
from core.backup_service import restore_sqlite, list_backups

# List all available snapshots
backups = list_backups()
latest_backup = backups[0]["path"]

# Restore database
restore_sqlite(latest_backup)
print(f"Restored database from {latest_backup}")
```

### MySQL Enterprise Backup & Rollback
To generate mysqldump scripts:
```python
from core.backup_service import generate_mysqldump_instructions

instructions = generate_mysqldump_instructions()
print("Backup Command:", instructions["dump_command"])
print("Restore Command:", instructions["restore_command"])
```
Operator command:
```bash
# Dump
mysqldump -h localhost -u root -p --single-transaction --routines --triggers --databases pmla_scwe > pre_v2_0_backup.sql

# Restore
mysql -h localhost -u root -p pmla_scwe < pre_v2_0_backup.sql
```
