# Changelog

All notable changes to the **PMLA-SCWE** (*Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine*) platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned (Next Development Checkpoint)
#### Version 2.0 Phase 2A — Desktop AuthenticatedUser Context & Desktop RBAC Integration
> **STATUS: NOT IMPLEMENTED YET (Scheduled Next)**
- **Desktop Login Integration**: Connect `desktop/login.py` to centralized `AuthenticatedUser` context.
- **Context Propagation**: Pass `current_user: AuthenticatedUser` state to `desktop/app.py` and child view panels.
- **Role-Aware Sidebar Navigation**: Dynamically filter sidebar items based on role (`Admin`, `Teacher`, `Viewer`).
- **UI Operational Enforcement**: Disable/hide mutation controls (*Add Student*, *Mark Attendance*, *Log Test*, *Create Intervention*) for Viewers.
- **Desktop RBAC Tests**: Automated GUI session tests in `tests/test_desktop_rbac.py`.

---

## [2.0.0] - 2026-08-16

### Version 2.0 Phase 1: Multi-School Tenancy & Role-Based Authorization Foundation

#### Added
- **Multi-School Tenancy Relational Schema**: Added `Organizations` (root tenant boundary) and `Schools` (operational tenant unit) tables with foreign keys and performance indexes.
- **Tenant Scoping for Core Entities**: Extended `Students` table with `school_id` and `Users` table with `organization_id`, `school_id`, and `is_active`.
- **Dynamic Default Tenant Provisioning**: Automatically seeds `DEFAULT_ORG` (*PMLA-SCWE Default Organization*) and `DEFAULT_SCHOOL` (*Default School*) for transparent single-school backward compatibility.
- **Centralized `AuthenticatedUser` Context (`core/authorization_service.py`)**: Immutable session dataclass encapsulating user ID, username, full name, role, organization ID, school ID, and active status.
- **Server-Side Identity Revalidation**: Active state re-verification (`get_authenticated_user_context`) protecting against client-side tampering.
- **Role Capability Matrix**: Granular permission predicates for `Admin`, `Teacher`, and `Viewer` roles (`can_manage_users`, `can_modify_students`, `can_record_attendance`, `can_create_interventions`).
- **Tenant Boundary Scoping Functions**: Enforced school access validation via `has_school_access(user, school_id)` and `has_org_access(user, org_id)`.
- **Versioned Migration Engine (`core/migration_service.py`)**: Idempotent DDL upgrade pipeline tracking applied versions in `Schema_Migrations` with pre/post row-count verification.
- **Automated Backup Service (`core/backup_service.py`)**: Online SQLite snapshot generation in `database/backups/` and enterprise `mysqldump` instruction generator.
- **Phase 1 End-to-End Smoke Test (`tests/smoke_test_v2.py`)**: 5-stage automated integration test validating tenant resolution, admin login, student CRUD, attendance, and analytics.
- **New Unit Test Suites**: Added `tests/test_tenant_service.py`, `tests/test_authorization.py`, and `tests/test_v2_phase1_migration.py`.
- **Setup & Verification Utility (`scripts/setup_project.py`)**: Cross-platform interactive setup and diagnostic utility.

#### Changed
- **Modern Password Hashing (`core/auth_service.py`)**: Standardized on PBKDF2-HMAC-SHA256 (100,000 iterations) while preserving backward-compatible verification for legacy SHA-256 and MD5 hashes.
- **Database Abstraction (`core/database.py`)**: Enhanced connection routing and query parameter normalization for multi-tenant schema DDL.
- **Modernized Diagnostics (`diagnose_setup.py`)**: Updated package mapping to verify `PySide6` and `reportlab`.
- **Authoritative Schema (`database/schema.sql`)**: Established canonical master DDL definition in `database/schema.sql` with root mirror documentation.
- **Test Isolation**: Implemented `setUp()` and `tearDown()` data cleanup across tenant and authorization test suites for 100% idempotent test execution.

#### Verified Baseline
- **78 Unit Tests Passing (100% OK in ~92s)** across 11 test modules.
- **5/5 Smoke Test Checkpoints Passing**.
- **5/5 Diagnostic Stages Passing**.

---

## [1.8.0] - 2026-08-16
### Added
- **Final Submission & Examination Package**: Complete CBSE Class XII project dossier including final project reports, 12-slide presentation decks, and viva voce preparation guides.
- **Feature Freeze & Final Verification**: 63 automated tests passing with 100% OK across 8 test suites.

---

## [1.7.0] - 2026-08-16
### Added
- **Academic Intelligence Command Center (`core/command_center_service.py`)**: Unified institutional data aggregator powering executive dashboards on Desktop and Web.
- **Smart Teacher Action Recommendations**: Grounded decision-support generating prioritized next steps for at-risk learners.
- **Smart Notification & Deduplication Engine (`core/notification_service.py`)**: `dedup_key` indexing with 7-day cooldowns, priority escalation, and positive learning milestone alerts.

---

## [1.6.0] - 2026-08-16
### Added
- **Closed-Loop Intervention Tracking (`core/intervention_service.py`)**: Automatic baseline snapshot capture (`pre_risk`, `pre_academic`, `pre_attendance`, `pre_lhs`).
- **Before vs. After Delta Analytics (`core/intervention_analytics.py`)**: Multi-dimensional recovery tracking and transparent 0–100 Effectiveness Scoring.
- **PySide6 & Flask Intervention Consoles**: Desktop pipeline table with outcome evaluation dialogs and web `/interventions` console.

---

## [1.5.0] - 2026-08-16
### Added
- **Professional Report Generation Engine (`core/report_service.py`)**: Centralized report builder for 6 report types (Individual Student, Class Performance, At-Risk, Attendance, Monthly Progress, Intervention Tracking).
- **Vector PDF Exporter**: High-resolution vector PDF generation via ReportLab with embedded charts and KPI summary tables.

---

## [1.4.0] - 2026-08-16
### Added
- **AI Teacher Copilot (`core/ai_assistant.py`)**: Grounded pedagogical actions (Explain Risk, Study Plan, Weak Topics, Parent Letter).
- **Multi-Provider Fallback Chain**: Google Gemini $\rightarrow$ OpenAI $\rightarrow$ Deterministic Offline Engine.

---

## [1.3.0] - 2026-08-16
### Added
- **Explainable Predictive Analytics & Risk Engine (`core/risk_engine.py`, `core/explainability.py`)**: Transparent 0–100 multi-factor risk formula with explicit factor contributions.
- **Ordinary Least Squares (OLS) Regression (`core/analytics.py`)**: Trajectory slope calculation ($y = mx + c$) over longitudinal weekly scores.

---

## [1.2.0] - 2026-08-14
### Added
- **Student 360° Intelligence Profile (`core/student_profile_service.py`)**: Centralized Single Source of Truth aggregating attendance, assessments, and wellness audits.
- **Learning Health Score (LHS)**: Multi-dimensional index combining Academic (40%), Attendance (40%), and Cyber-Wellness (20%).

---

## [1.1.0] - 2026-08-14
### Added
- **Premium Modern UI Design System**: Dark theme palette (`#080A12` base), reusable PySide6 widgets (`desktop/widgets/`), and responsive Flask glassmorphism CSS.

---

## [1.0.0] - 2026-08-10
### Added
- **Core Platform Architecture**: MySQL database schema with SQLite automatic fallback (`pmla_scwe_fallback.db`), student CRUD, daily attendance registry, and cyber-wellbeing audits.
