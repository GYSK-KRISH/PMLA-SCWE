# PMLA-SCWE: Chronological Project Evolution
## From Single-School Prototype to Multi-Tenant Educational Intelligence Platform

---

## 1. Evolution Overview & Milestones

The **PMLA-SCWE** (*Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine*) platform has evolved through multiple major architectural phases:

```text
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                           PROJECT EVOLUTION ROADMAP                      │
  └──────────────────────────────────────────────────────────────────────────┘

  [Phase 0: Conceptual Foundation]
    • Early academic concept for CBSE Class XII Informatics Practices.
    • Basic student records, diagnostic score logging, and SQLite storage.
            │
            ▼
  [Version 1.0 – 1.2: Core Domain & Student 360°]
    • MySQL relational schema + SQLite zero-configuration fallback.
    • Composite Learning Health Score (LHS) mathematical formulation.
    • Centralized Student 360° Profile Single Source of Truth (SSoT).
            │
            ▼
  [Version 1.3 – 1.4: Explainable Intelligence & AI Copilot]
    • OLS Linear Regression trajectory forecasting.
    • Transparent 0–100 Explainable Risk Engine with evidence factors.
    • AI Teacher Copilot (Gemini / OpenAI / Offline Deterministic Engine).
            │
            ▼
  [Version 1.5 – 1.6: Closed-Loop Remediation & Vector Reporting]
    • Closed-Loop Intervention Tracking with baseline metrics snapshots.
    • Before vs. After Delta Analytics ($\Delta_{\text{Risk}}$, $\Delta_{\text{LHS}}$) and Effectiveness Scoring.
    • ReportLab Vector PDF generation engine with high-res charts.
            │
            ▼
  [Version 1.7 – 1.8: Executive Command Center & Final CBSE Package]
    • Unified Academic Command Center dashboard aggregator.
    • Smart notification engine with deduplication keys and cooldowns.
    • Complete academic project package freeze (63 unit tests).
            │
            ▼
  [Shared-Core SOA Refactoring]
    • Complete decoupling of presentation layers (PySide6 & Flask).
    • Centralized shared domain logic residing entirely in `core/`.
            │
            ▼
  [Version 2.0 Phase 1: Multi-School Tenancy & RBAC Foundation] ───► [CURRENT CHECKPOINT]
    • Hierarchical Multi-Tenancy (`Organizations` ──► `Schools` ──► `Users`/`Students`).
    • Centralized `AuthenticatedUser` immutable context & server-side revalidation.
    • Role-Based Access Control matrix (`Admin`, `Teacher`, `Viewer`).
    • Idempotent Migration Engine (`Schema_Migrations`) & atomic SQLite online backups.
    • Expanded test suite: **78 Unit Tests Passing (100% OK)** + 5/5 Smoke Test.
            │
            ▼
  [Version 2.0 Phase 2A: Desktop Context & UI RBAC Integration] ───► [NEXT DEVELOPMENT]
    • Desktop login context connection, role-aware navigation, UI permissions.
```

---

## 2. Detailed Chronological Phase History

### Phase 0: Conceptual Foundation (Inception)
- **Goal**: Develop a student monitoring tool for Informatics Practices addressing academic and cyber-distraction habits.
- **Initial Capabilities**: Basic CRUD for student demographics, simple grade logging, early Tkinter/CustomTkinter GUI experimentation.
- **Data Storage**: Local SQLite file storage.

---

### Version 1.0.0 – 1.2.0: Core Domain, Database Abstraction & Student 360°
- **Database Abstraction Layer (`core/database.py`)**: Implemented dual-backend architecture with MySQL 8.0+ as the primary multi-user database and SQLite3 (`pmla_scwe_fallback.db`) as an automatic zero-configuration fallback if MySQL is offline.
- **Learning Health Score (LHS)**: Formulated the composite index combining Academic Performance (40%), Daily Attendance Rate (40%), and Digital Cyber-Wellbeing (20%).
- **Student 360° Intelligence Profile (`core/student_profile_service.py`)**: Created a centralized service aggregating personal records, attendance streaks, diagnostic logs, weekly progress, cyber audits, and achievements into a unified profile.

---

### Version 1.3.0 – 1.4.0: Predictive Analytics & AI Teacher Copilot
- **Ordinary Least Squares (OLS) Regression (`core/analytics.py`)**: Implemented linear regression modeling over longitudinal weekly progress scores $y = mx + c$ to compute trend slopes and forecast next-week exam performance without black-box opacity.
- **Explainable Multi-Factor Risk Engine (`core/risk_engine.py`, `core/explainability.py`)**: Designed a transparent 0–100 risk algorithm evaluating academic deficits, attendance shortfalls against the CBSE 75% threshold, digital distraction levels, and trend decay, generating human-readable evidence bullets.
- **AI Teacher Copilot (`core/ai_assistant.py`)**: Built a multi-provider pedagogical advisory assistant supporting Google Gemini, OpenAI, and a rule-based offline deterministic fallback for offline evaluation environments.

---

### Version 1.5.0 – 1.6.0: Closed-Loop Interventions & Vector Reporting
- **Closed-Loop Intervention Pipeline (`core/intervention_service.py`)**: Established pedagogical intervention tracking. Upon creating a remedial action, the system automatically captures a baseline snapshot (`pre_risk`, `pre_academic`, `pre_attendance`, `pre_lhs`).
- **Outcome Recovery & Delta Analytics (`core/intervention_analytics.py`)**: Created evaluation algorithms calculating before-vs-after deltas and assigning a transparent 0–100 Effectiveness Score (`Highly Effective`, `Effective`, `Moderate Improvement`, `Needs Review`).
- **Professional PDF Engine (`core/report_service.py`)**: Integrated ReportLab to compile publication-grade vector PDF reports with embedded charts, statistics grids, and safety disclaimers.

---

### Version 1.7.0 – 1.8.0: Executive Command Center & Final CBSE Freeze
- **Academic Command Center (`core/command_center_service.py`)**: Integrated institutional KPIs, stratified risk distributions, and smart teacher action recommendations into high-level dashboard feeds.
- **Smart Notification Engine (`core/notification_service.py`)**: Added `dedup_key` hashing, 7-day alert cooldowns, priority escalation, and milestone celebrations.
- **Final Submission Package**: Completed CBSE Class XII examination dossiers, slide decks, and verified 63 automated tests passing.

---

### Shared-Core SOA Architectural Refactoring
- **Presentation Decoupling**: Completely separated the PySide6 desktop GUI client (`desktop/`) and the Flask web console (`web/`) from domain logic.
- **Single Source of Truth**: All analytical algorithms, business validations, and data queries were centralized in `core/`, ensuring both interfaces display identical metrics.

---

### Version 2.0 Phase 1: Multi-School Tenancy & RBAC Foundation (Completed Checkpoint)
- **Hierarchical Multi-Tenancy**: Added `Organizations` (root tenant) and `Schools` (operational tenant) tables with dynamic default tenant provisioning (`DEFAULT_ORG`, `DEFAULT_SCHOOL`).
- **Tenant Scoping**: Extended `Students` with `school_id` and `Users` with `organization_id` and `school_id`.
- **RBAC Security Infrastructure (`core/authorization_service.py`)**: Implemented `AuthenticatedUser` dataclass, role checks (`Admin`, `Teacher`, `Viewer`), server-side identity revalidation, and school-scoped boundary enforcement (`has_school_access`).
- **Modern Password Security (`core/auth_service.py`)**: Upgraded authentication to PBKDF2-HMAC-SHA256 with full backward compatibility for legacy hashes.
- **Versioned Migration Engine (`core/migration_service.py`)**: Created `Schema_Migrations` table tracking with pre-migration SQLite snapshots in `database/backups/`, safe column additions, data backfilling, and row-count verification assertions (zero data loss).
- **Test Suite Expansion**: Added 15 new test cases across migrations, tenant management, and authorization, bringing the verified baseline to **78 Unit Tests Passing (100% OK)** and 5/5 Smoke Test checkpoints passing.

---

## 3. Version Comparison Matrix

| Capability / Dimension | Version 1.0 – 1.2 | Version 1.3 – 1.6 | Version 1.7 – 1.8 | Version 2.0 (Phase 1 Current) |
| :--- | :---: | :---: | :---: | :---: |
| **Tenancy Model** | Single School | Single School | Single School | **Hierarchical Multi-School Multi-Tenant** |
| **User Roles** | Admin only | Admin / User | Admin / User | **Admin, Teacher, Viewer (RBAC)** |
| **Session Context** | Dict / Username | Dict / Username | Dict / Username | **Immutable `AuthenticatedUser` Dataclass** |
| **Server Revalidation**| None | None | None | **`get_authenticated_user_context` Active** |
| **Password Security** | SHA-256 | SHA-256 | SHA-256 | **PBKDF2-HMAC-SHA256 + Legacy Compat** |
| **Migration Engine** | Ad-hoc SQL | Ad-hoc SQL | Ad-hoc SQL | **Versioned `Schema_Migrations` Engine** |
| **Backup Infrastructure**| Manual | Manual | Manual | **Automated Online SQLite Snapshots** |
| **Predictive Analytics** | Basic LHS | OLS Regression | OLS Regression | **OLS Regression + Student 360° SSoT** |
| **Risk Engine** | Threshold rules| 0-100 Explainable | 0-100 Explainable | **0-100 Explainable + Evidence Factors** |
| **Interventions** | None | Closed-Loop | Closed-Loop | **Closed-Loop + Tenant Scoping** |
| **Reporting** | Text / CSV | Vector PDF / CSV| Vector PDF / CSV| **Vector PDF / CSV / Tabular** |
| **Automated Tests** | 20 Tests | 45 Tests | 63 Tests | **78 Tests Passing (100% OK)** |

---

## 4. Current State & Immediate Next Milestone

The repository is frozen and verified at the completion of **Version 2.0 Phase 1**.

**Next Scheduled Milestone**:
**Version 2.0 Phase 2A — Desktop AuthenticatedUser Context and Desktop RBAC Integration**  
Development will resume by connecting the desktop login flow (`desktop/login.py`) to the centralized `AuthenticatedUser` context, passing user state to `desktop/app.py`, implementing role-aware sidebar navigation, and enforcing Admin/Teacher/Viewer UI permissions.
