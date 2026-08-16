# PMLA-SCWE: Database Migration & Backup Guide
## Multi-Tenancy Upgrade Runbook & Disaster Recovery — Version 2.0 (Phase 1)

---

## 1. Migration Philosophy & Safety Guarantees

PMLA-SCWE Version 2.0 introduces an automated, idempotent migration framework (`core/migration_service.py`) built upon five safety principles:
1. **Pre-Migration Atomic Snapshot**: Automatically takes an online backup of SQLite databases before running any DDL statements.
2. **Idempotent Execution**: Version applied status is tracked in the `Schema_Migrations` table; repeated runs exit cleanly without re-executing DDL or duplicating records.
3. **Non-Destructive Column Additions**: Adds new tenant columns (`school_id`, `organization_id`, `is_active`) with safe defaults without dropping existing tables or truncating records.
4. **Automatic Tenant Backfilling**: Dynamically maps existing records to default tenant entities (`DEFAULT_ORG`, `DEFAULT_SCHOOL`).
5. **Row-Count Parity Assertions**: Asserts exact row-count equality before and after migration across all operational tables to guarantee zero data loss.

---

## 2. Executing Migrations

### 2.1 Standard CLI Execution (Recommended)
Run the migration module directly in PowerShell:
```powershell
.venv\Scripts\python.exe -m database.migrations.v2_0_phase_1
```

### 2.2 Programmatic Execution
```python
from core.migration_service import run_v2_phase1_migration

report = run_v2_phase1_migration(create_backup=True)
if report["success"]:
    print(f"Migration applied successfully! Version: {report['version']}")
else:
    print(f"Migration failed: {report['errors']}")
```

---

## 3. Step-by-Step Migration Pipeline

```text
 1. ATOMIC BACKUP
    └── Creates timestamped snapshot: database/backups/pmla_scwe_fallback_pre_v2_0_phase1_<timestamp>.db
    ▼
 2. CAPTURE BASELINE METRICS
    └── Queries table row counts: Students, Attendance, Diagnostic_Logs, Cyber_Audit, Users, etc.
    ▼
 3. CHECK VERSION IDEMPOTENCY
    └── Queries Schema_Migrations. If 'v2_0_phase_1' is already applied, skips DDL and returns success.
    ▼
 4. EXECUTE DDL SCHEMA
    └── Creates Schema_Migrations, Organizations, and Schools tables (IF NOT EXISTS).
    ▼
 5. PROVISION DEFAULT TENANTS
    ├── Seeds 'PMLA-SCWE Default Organization' (Code: DEFAULT_ORG) if missing.
    └── Seeds 'Default School' (Code: DEFAULT_SCHOOL) if missing.
    ▼
 6. SAFE COLUMN ALTERATIONS
    ├── Adds school_id to Students table (DEFAULT 1).
    └── Adds organization_id, school_id, is_active, updated_at to Users table.
    ▼
 7. DATA BACKFILLING
    ├── Maps Users status -> is_active ('Active' -> 1, 'Inactive' -> 0).
    ├── Links all existing Users to DEFAULT_ORG and DEFAULT_SCHOOL.
    └── Links all existing Students to DEFAULT_SCHOOL.
    ▼
 8. PERFORMANCE INDEXES
    ├── Creates idx_students_school ON Students(school_id).
    ├── Creates idx_schools_org ON Schools(organization_id).
    └── Creates idx_users_school ON Users(school_id).
    ▼
 9. VERIFY ROW-COUNT INTEGRITY
    └── Asserts Before_Count == After_Count across all tables (Zero Data Loss Assertion).
    ▼
10. COMMIT MIGRATION RECORD
    └── Inserts record for 'v2_0_phase_1' into Schema_Migrations.
```

---

## 4. Row-Count Parity Verification

During Version 2.0 Phase 1 migration, data integrity was verified with **zero data loss**:

```text
Table Name            Pre-Migration Count   Post-Migration Count  Integrity Status
──────────────────────────────────────────────────────────────────────────────────
Students              99                    99                    [OK] Preserved
Attendance            990                   990                   [OK] Preserved
Diagnostic_Logs       99                    99                    [OK] Preserved
Cyber_Audit           99                    99                    [OK] Preserved
Weekly_Progress       396                   396                   [OK] Preserved
Achievements          24                    24                    [OK] Preserved
Learning_Objectives   10                    10                    [OK] Preserved
Activity_Log          100                   100                   [OK] Preserved
Reports_Metadata      100                   100                   [OK] Preserved
Users                 1                     1                     [OK] Enriched with Tenant Scope
Organizations         0                     1                     [OK] Provisioned DEFAULT_ORG
Schools               0                     1                     [OK] Provisioned DEFAULT_SCHOOL
Schema_Migrations     0                     1                     [OK] Version Recorded
```

---

## 5. Backup & Disaster Recovery Procedures

### 5.1 SQLite Online Snapshots (`core/backup_service.py`)
To trigger an immediate backup of the fallback database:
```python
from core.backup_service import backup_sqlite, list_backups

# Create snapshot
res = backup_sqlite(tag="manual_backup")
print(f"Backup created at: {res['backup_path']} (Size: {res['size_bytes']} bytes)")

# List catalog
backups = list_backups()
for b in backups:
    print(f"Backup: {b['filename']} ({b['size_formatted']}) - {b['created_at']}")
```

### 5.2 SQLite Database Restoration
To restore a snapshot in the event of failure:
```python
from core.backup_service import restore_sqlite, list_backups

backups = list_backups()
latest_snapshot = backups[0]["path"]

restore_sqlite(latest_snapshot)
print(f"Restored database from {latest_snapshot}")
```

### 5.3 Enterprise MySQL Backup & Recovery
For MySQL primary mode, generate operator commands via `core/backup_service.py`:
```python
from core.backup_service import generate_mysqldump_instructions

info = generate_mysqldump_instructions()
print("Backup Command:", info["dump_command"])
print("Restore Command:", info["restore_command"])
```

**Operator Terminal Commands**:
```bash
# Export full database dump
mysqldump -h localhost -u root -p --single-transaction --routines --triggers --databases pmla_scwe > pmla_scwe_backup.sql

# Restore full database dump
mysql -h localhost -u root -p pmla_scwe < pmla_scwe_backup.sql
```
