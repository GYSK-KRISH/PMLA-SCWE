# PMLA-SCWE: Testing & Quality Assurance Verification Guide
## Test Suites, Smoke Tests & Isolation Strategy — Version 2.0 (Phase 1)

---

## 1. Test Architecture Overview

The PMLA-SCWE test framework validates security, analytical precision, database migrations, and domain services across 12 comprehensive test modules located in `tests/`:

```text
┌──────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Test Module                          │ Scope & Capabilities Validated                              │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_authorization.py          │ RBAC matrix, AuthenticatedUser dataclass, server-side       │
│                                      │ revalidation, and school-scoped boundary checks.            │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_tenant_service.py         │ Organizations & Schools CRUD, default tenant provisioning,  │
│                                      │ listing, updates, and isolation.                            │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_v2_phase1_migration.py    │ Migration pipeline idempotency, pre/post row count parity,  │
│                                      │ SQLite backup creation, and Schema_Migrations tracking.     │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_core.py                   │ Core student CRUD, attendance logging, wellness audits,     │
│                                      │ database abstraction routing, and UI widget imports.        │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_command_center.py         │ Executive command center aggregation, stratified risk KPIs, │
│                                      │ and recommended teacher actions.                            │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_intervention_service.py   │ Closed-loop intervention lifecycles, baseline snapshots,    │
│                                      │ delta recovery tracking, and 0-100 effectiveness scoring.   │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_notifications.py          │ Smart notification deduplication (dedup_key), 7-day alert   │
│                                      │ cooldowns, priority escalation, and milestone celebrations. │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_profile_service.py        │ Student 360° SSoT profile aggregation, Learning Health Score│
│                                      │ normalization, and chronological activity timeline feeds.   │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_reports.py                │ ReportLab vector PDF generation, CSV tabular exports, and   │
│                                      │ report metadata cataloging.                                 │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_risk_engine.py            │ Deterministic 0-100 risk scoring formula, deficit weighting,│
│                                      │ and SHAP-like explainability evidence bullets.              │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/test_copilot.py                │ Multi-provider AI assistant fallback chain (Gemini ->       │
│                                      │ OpenAI -> local deterministic offline engine).              │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ tests/smoke_test_v2.py               │ End-to-end integration smoke test across tenant resolution, │
│                                      │ admin auth, student CRUD, attendance, and analytics.        │
└──────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Execution & Verified Baseline

### 2.1 Full Automated Unit Test Suite
To execute all 11 unit test suites:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

**Actual Verified Execution Result**:
```text
Ran 78 tests in 92.201s

OK
```

---

### 2.2 End-to-End Smoke Test
To verify live platform operations from authentication through Student 360 analytics:
```powershell
.venv\Scripts\python.exe tests\smoke_test_v2.py
```

**Actual Verified Execution Result**:
```text
============================================================
 PMLA-SCWE VERSION 2.0 PHASE 1 -- END-TO-END SMOKE TEST
============================================================

[1/5] Testing Tenant Resolution & Admin Login...
      Default Org: 'PMLA-SCWE Default Organization' (ID: 1)
      Default School: 'Default School' (ID: 1)
      [PASS] Admin authenticated: @admin (Admin)

[2/5] Testing Student Registration & Lookup...
      [PASS] Registered and retrieved student #409 with school_id=1

[3/5] Testing Attendance Logging...
      [PASS] Attendance history logged (Records: 1)

[4/5] Testing Dashboard & Student 360 Analytics...
      [PASS] Dashboard summary loaded (Total students: 3)
      [PASS] Student 360 profile loaded for #409 (LHS: 100.0)
      [PASS] Cleaned up temporary test student

[5/5] Testing RBAC Roles & School Scoping...
      [PASS] Admin, Teacher (school-scoped), and Viewer (read-only) RBAC verified

============================================================
 [SUCCESS] ALL 5 SMOKE TEST CHECKPOINTS PASSED!
============================================================
```

---

### 2.3 Setup Diagnostics Verification
```powershell
.venv\Scripts\python.exe diagnose_setup.py
```

**Actual Verified Diagnostics Result**:
```text
==================================================
 SETUP DIAGNOSTIC RESULT
==================================================
Python Environment:       [PASS]
Dependencies:             [PASS]
Configuration:            [PASS]
Database Connection:      [PASS]
Database Schema:          [PASS]

PMLA-SCWE is ready to run.
==================================================
```

---

## 3. Test Isolation & Teardown Strategy

### 3.1 The Persistent Database Challenge
Because unit tests can execute against a persistent development MySQL database, tests that create unique records (e.g. `TEST_ORG_ALPHA`, `NORTH_CAMPUS`, `auth_test_teacher`) would previously fail on subsequent runs due to unique key collisions or residual inactive states.

### 3.2 Implemented Isolation Mechanism
In `tests/test_tenant_service.py` and `tests/test_authorization.py`, tests now implement symmetric `setUp()` and `tearDown()` cleanup hooks:
- **Pre-Test Cleanup**: Ensures that any residual artifacts from aborted previous runs are purged before test execution.
- **Post-Test Teardown**: Guarantees that newly created test accounts, organizations, and schools are deleted at test conclusion.
- **FK-Safe Cascades**: Child student records are removed prior to deleting parent entities.
- **Zero Pollution**: Production and default seed records (`DEFAULT_ORG`, `DEFAULT_SCHOOL`, `admin`) are strictly protected and never deleted during test teardowns.
