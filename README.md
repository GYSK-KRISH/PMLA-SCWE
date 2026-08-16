# PMLA-SCWE
### Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine

[![Version](https://img.shields.io/badge/Version-2.0.0--Phase1-blue.svg)](file:///d:/PMLA-SCWE/CHANGELOG.md)
[![Status](https://img.shields.io/badge/Status-Phase_1_Complete_%7C_Phase_2A_Pending-success.svg)](file:///d:/PMLA-SCWE/documentation/DEVELOPMENT_ROADMAP.md)
[![Tests](https://img.shields.io/badge/Tests-78%20Passed%20(100%25)-brightgreen.svg)](file:///d:/PMLA-SCWE/documentation/TESTING_AND_VERIFICATION.md)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-MySQL%20Primary%20%2B%20SQLite%20Fallback-orange.svg)](file:///d:/PMLA-SCWE/documentation/DATABASE_ARCHITECTURE.md)

---

## Project Overview

**PMLA-SCWE** (*Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine*) is an explainable educational intelligence, academic analytics, and teacher decision-support platform. 

Designed to move beyond passive electronic school ledgers, PMLA-SCWE integrates **academic diagnostic assessments**, **daily attendance patterns**, and **digital cyber-wellness habits** (screen time, sleep duration, distraction level, safety awareness) into a unified, multi-dimensional **Learning Health Score (LHS)**.

The system applies **Ordinary Least Squares (OLS) Linear Regression** for transparent academic forecasting, a deterministic **Explainable Risk Engine** for early intervention, a **Closed-Loop Intervention Pipeline** to snapshot baselines and evaluate outcome recovery, and a **Multi-School Tenancy & RBAC Security Foundation** supporting multi-organization deployments.

---

## Current Version & Development Checkpoint

```text
================================================================================
CURRENT MILESTONE:
  PMLA-SCWE Version 2.0 — Phase 1 COMPLETE & VERIFIED

NEXT SCHEDULED MILESTONE:
  PMLA-SCWE Version 2.0 — Phase 2A PENDING
  (Desktop AuthenticatedUser Context and Desktop RBAC Integration)
================================================================================
```

---

## Key Features (Implemented & Active)

- **Hierarchical Multi-School Tenancy**: Root `Organizations` $\rightarrow$ operational `Schools` $\rightarrow$ scoped `Users` and `Students`.
- **Role-Based Access Control (RBAC)**: Centralized `AuthenticatedUser` context supporting `Admin`, `Teacher`, and `Viewer` roles with server-side identity revalidation and school boundary scoping.
- **Student 360° Intelligence Profile**: Single Source of Truth (SSoT) aggregating attendance, assessment trends, cyber audits, and interventions into an interactive profile.
- **Learning Health Score (LHS)**: Composite metric combining Academic Performance (40%), Daily Attendance (40%), and Digital Cyber-Wellbeing (20%).
- **Predictive Trajectory Forecasting**: OLS Linear Regression ($y = mx + c$) over longitudinal progress scores to forecast future exam performance.
- **Explainable Multi-Factor Risk Engine**: Transparent 0–100 risk scoring with deterministic evidence bullets (academic deficits, attendance below CBSE 75%, digital distraction).
- **Closed-Loop Intervention Tracking**: Automatically captures pre-intervention baseline snapshots (`pre_risk`, `pre_lhs`, `pre_academic`) and computes before-vs-after delta recovery metrics.
- **AI Teacher Copilot**: Pedagogical advisory assistant supporting Google Gemini, OpenAI, and a deterministic offline rule engine.
- **Professional Vector PDF Reporting**: Publication-grade ReportLab vector PDF generator with embedded charts, KPI summary tables, and safety notices.
- **Smart Decision-Support Notifications**: Priority alerts with `dedup_key` hashing, 7-day cooldowns, and milestone celebration chips.
- **Dual-Backend Database Layer**: MySQL 8.0+ primary backend with automated, zero-configuration SQLite3 fallback (`pmla_scwe_fallback.db`).
- **Versioned Migration Engine**: Idempotent migration runner (`core/migration_service.py`) with pre-migration SQLite snapshots and zero data loss assertions.

---

## Architecture Overview

```text
                           PMLA-SCWE ARCHITECTURE
                                     │
      ┌──────────────────────────────┴──────────────────────────────┐
      ▼                                                             ▼
┌───────────────────────────┐                         ┌───────────────────────────┐
│  PySide6 Desktop Client   │                         │     Flask Web Console     │
│  (Qt 6 Dark Modern Theme) │                         │  (Jinja2 Glassmorphism)   │
└───────────────────────────┘                         └───────────────────────────┘
      │                                                             │
      └──────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SHARED CORE SERVICES (core/)                           │
│  • tenant_service.py               • auth_service.py (PBKDF2)                   │
│  • authorization_service.py (RBAC) • user_service.py                            │
│  • student_profile_service.py      • student_service.py                         │
│  • risk_engine.py & explainability • analytics.py (OLS Regression & LHS)        │
│  • intervention_service.py         • intervention_analytics.py                  │
│  • command_center_service.py       • notification_service.py                    │
│  • report_service.py (ReportLab)   • ai_assistant.py (Gemini/OpenAI/Offline)    │
│  • migration_service.py            • backup_service.py (Snapshots)              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE ABSTRACTION LAYER                              │
│                                (database.py)                                    │
│          ├── MySQL 8.0+ Primary Backend (Port 3306)                             │
│          └── SQLite3 Automatic Offline Fallback (pmla_scwe_fallback.db)         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## User Roles & Capabilities

| Capability / Action | Service Enforcement Function | Admin | Teacher | Viewer |
| :--- | :--- | :---: | :---: | :---: |
| **System User Administration** | `can_manage_users(user)` | **ALLOW** | DENY | DENY |
| **Manage Organizations & Schools**| `can_manage_organizations(user)`| **ALLOW** | DENY | DENY |
| **School Access Scope** | `has_school_access(user, school_id)`| **ALL SCHOOLS**| Assigned School Only | Assigned School Only |
| **Register & Edit Students** | `can_modify_students(user)` | **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **Record Attendance Logs** | `can_record_attendance(user)` | **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **Create Remedial Interventions**| `can_create_interventions(user)`| **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **View Analytics & Dashboards** | `can_view_analytics(user)` | **ALLOW** | **ALLOW** | **ALLOW** |
| **Generate & Export PDF Reports**| `can_generate_reports(user)` | **ALLOW** | **ALLOW** | **ALLOW** |

---

## Quick Start & Installation

### 1. Automated Setup (Windows)
Double-click `setup_and_run.bat` or run:
```cmd
setup_and_run.bat
```

### 2. Cross-Platform Python Setup Utility
```powershell
.venv\Scripts\python.exe scripts\setup_project.py
```

### 3. Step-by-Step Manual Setup
```powershell
# 1. Open directory
cd d:\PMLA-SCWE

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy configuration template
Copy-Item .env.example .env

# 5. Run diagnostics
python diagnose_setup.py

# 6. Launch PySide6 Desktop GUI (Default Admin: admin / admin123)
python main.py

# 7. Launch Flask Web Console (http://127.0.0.1:5000)
python main.py --web
```

---

## Database Modes & Migration

### Dual Database Modes
- **MySQL Primary Mode**: Default when MySQL Server is listening on port 3306 with credentials configured in `.env`.
- **SQLite Fallback Mode**: Engaged automatically if MySQL is unavailable. Uses `pmla_scwe_fallback.db`.

### Running Database Migrations
To execute the Version 2.0 Phase 1 multi-school tenancy migration:
```powershell
.venv\Scripts\python.exe -m database.migrations.v2_0_phase_1
```

---

## Automated Verification & Test Suite

All 78 unit tests and the end-to-end smoke test have been verified:

```powershell
# Run full unit test suite
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
# Result: Ran 78 tests in 92.201s — OK

# Run Version 2.0 Phase 1 Smoke Test
.venv\Scripts\python.exe tests\smoke_test_v2.py
# Result: ALL 5 SMOKE TEST CHECKPOINTS PASSED!
```

---

## Authoritative Documentation Directory

Complete system documentation is available in the [`documentation/`](file:///d:/PMLA-SCWE/documentation/) directory:

- 📘 [PROJECT_MASTER_DOCUMENTATION.md](file:///d:/PMLA-SCWE/documentation/PROJECT_MASTER_DOCUMENTATION.md) — Comprehensive master technical reference (50 topics).
- 📜 [PROJECT_EVOLUTION.md](file:///d:/PMLA-SCWE/documentation/PROJECT_EVOLUTION.md) — Chronological history from early prototype to Version 2.0.
- 🏗️ [CURRENT_SYSTEM_ARCHITECTURE.md](file:///d:/PMLA-SCWE/documentation/CURRENT_SYSTEM_ARCHITECTURE.md) — Architectural blueprints, SOA layers, and flowcharts.
- 🗄️ [DATABASE_ARCHITECTURE.md](file:///d:/PMLA-SCWE/documentation/DATABASE_ARCHITECTURE.md) — Dual backend routing, 13-table schema, and indexes.
- 🔐 [AUTHENTICATION_AND_RBAC.md](file:///d:/PMLA-SCWE/documentation/AUTHENTICATION_AND_RBAC.md) — Security specifications, PBKDF2 hashing, and RBAC matrix.
- 🚀 [INSTALLATION_AND_SETUP.md](file:///d:/PMLA-SCWE/documentation/INSTALLATION_AND_SETUP.md) — Start-to-finish installation runbook and troubleshooting.
- 🔄 [MIGRATION_AND_BACKUP_GUIDE.md](file:///d:/PMLA-SCWE/documentation/MIGRATION_AND_BACKUP_GUIDE.md) — Migration runbooks, row-count parity, and backups.
- 🧪 [TESTING_AND_VERIFICATION.md](file:///d:/PMLA-SCWE/documentation/TESTING_AND_VERIFICATION.md) — Test suite documentation, smoke tests, and test isolation.
- 🗺️ [DEVELOPMENT_ROADMAP.md](file:///d:/PMLA-SCWE/documentation/DEVELOPMENT_ROADMAP.md) — Strategic roadmap and Version 2.0 Phase 2A resume marker.
- 📋 [REPOSITORY_CLEANUP_AND_CONSOLIDATION_REPORT.md](file:///d:/PMLA-SCWE/documentation/REPOSITORY_CLEANUP_AND_CONSOLIDATION_REPORT.md) — Maintenance audit and checkpoint report.

---

## Security Guidelines

- **Environment Secrets**: Never commit `.env` or API credentials to Git.
- **Authoritative Authorization**: Service-side permission checks in `core/authorization_service.py` are authoritative and re-verify database state.
- **SQL Sanitization**: All database interaction utilizes parameterized queries to prevent SQL injection.

---

## License

Developed for educational analytics, research, and institutional intelligence.
