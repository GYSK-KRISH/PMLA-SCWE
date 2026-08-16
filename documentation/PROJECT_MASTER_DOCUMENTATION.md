# PMLA-SCWE: Project Master Technical Documentation
## Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine
### Authoritative Comprehensive System Reference — Version 2.0 (Phase 1 Checkpoint)

---

## 1. Executive Summary

**PMLA-SCWE** (*Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine*) is an explainable educational intelligence, academic analytics, and teacher decision-support platform. Designed to bridge the gap between static school management ledgers and actionable pedagogical intervention, PMLA-SCWE synthesizes student academic assessment data, daily attendance patterns, and digital cyber-wellbeing metrics into a unified, multi-dimensional **Learning Health Score (LHS)**.

The system utilizes **Ordinary Least Squares (OLS) Linear Regression** for academic trajectory forecasting, a deterministic **Explainable Risk Engine** for early dropout/deficit warning, and a **Closed-Loop Intervention Pipeline** that snapshots baseline performance and tracks before-and-after recovery deltas over time.

Following the completion of **Version 2.0 Phase 1**, the platform features a **hierarchical multi-school multi-tenant architecture**, a centralized **Role-Based Access Control (RBAC)** security model supporting **Admin**, **Teacher**, and **Viewer** roles, an automated **Database Migration Engine** with atomic backups, and a dual-backend database abstraction layer supporting **MySQL 8.0+** primary mode and **SQLite3** zero-configuration automatic fallback.

---

## 2. Project Purpose & Educational Problem Statement

### 2.1 The Traditional School Software Problem
Traditional Educational Management Information Systems (EMIS) suffer from three structural shortcomings:
1. **Passive Electronic Ledgers**: Existing tools record absent marks and exam scores as isolated historical facts, offering zero predictive foresight or trend detection.
2. **Opaque "Black-Box" Alerts**: Modern machine-learning alert tools often output opaque probability scores (e.g., *"Student Risk: 82%"*) without explaining the root contributing deficits, confusing educators and preventing targeted remediation.
3. **Open-Loop Disconnect**: When a struggling student is identified, traditional systems provide no mechanism to log pedagogical interventions, capture baseline metrics, or quantitatively measure intervention effectiveness over time.

### 2.2 The PMLA-SCWE Solution: Closed-Loop Educational Intelligence
PMLA-SCWE implements a continuous, closed-loop educational lifecycle:

```text
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                 CLOSED-LOOP EDUCATIONAL INTELLIGENCE CYCLE               │
  └──────────────────────────────────────────────────────────────────────────┘
                                      │
  1. COLLECT MULTI-FACET DATA (Attendance, Assessments, Cyber-Wellbeing)
                                      ▼
  2. SYNTHESIZE STUDENT 360° PROFILE (Single Source of Truth)
                                      ▼
  3. COMPUTE LEARNING HEALTH SCORE (Academic 40%, Attendance 40%, Wellness 20%)
                                      ▼
  4. EXPLAINABLE RISK ENGINE (Deterministic 0-100 Score + Evidence Factors)
                                      ▼
  5. SMART NOTIFICATION ENGINE (Cooldowns, Deduplication, Priority Escalation)
                                      ▼
  6. AI TEACHER COPILOT ADVISORY (Grounded Remedial Strategies)
                                      ▼
  7. TEACHER-APPROVED INTERVENTION (Baseline Metrics Snapshot: Pre-Risk, Pre-LHS)
                                      ▼
  8. OUTCOME EVALUATION & DELTA TRACKING (Post-Intervention Deltas & 0-100 Score)
                                      ▼
  9. EXECUTIVE COMMAND CENTER (Institutional Risk Stratification & Governance)
```

---

## 3. System Objectives

- **Multi-Tenant Foundation**: Support multi-organization and multi-school tenancy with strict boundary scoping.
- **Explainable Analytics**: Provide deterministic, human-understandable risk scores with explicit evidence bullets.
- **Academic Forecasting**: Calculate linear regression trends across longitudinal progress scores to predict future outcomes.
- **Cyber-Wellbeing Integration**: Factor screen time, sleep duration, digital distraction, and cyber-safety awareness into overall student health.
- **Role-Based Access Control**: Enforce granular role capabilities across Administrators, Teachers, and Viewers.
- **Dual-Backend Resilience**: Deliver high-performance MySQL enterprise storage with automated SQLite fallback for offline evaluations.
- **Professional Reporting**: Generate high-resolution vector PDF reports, CSV tabular exports, and markdown previews.

---

## 4. Current Version Status

| Attribute | Current Checkpoint Specification |
| :--- | :--- |
| **System Version** | **Version 2.0.0** |
| **Active Milestone** | **Phase 1 COMPLETE & VERIFIED** |
| **Next Milestone** | **Phase 2A PENDING (Desktop AuthenticatedUser Context & Desktop RBAC Integration)** |
| **Database Architecture** | Hierarchical Multi-School Multi-Tenant (Organizations $\rightarrow$ Schools $\rightarrow$ Users/Students) |
| **Primary Database** | MySQL 8.0+ (Port 3306) via `mysql-connector-python` |
| **Fallback Database** | SQLite3 Embedded (`pmla_scwe_fallback.db`) |
| **Desktop Technology** | PySide6 (Qt 6 for Python) with Dark Modern CSS Design System |
| **Web Technology** | Flask 3.0+ with Jinja2 Glassmorphism Templates |
| **Test Baseline** | **78 Unit Tests Passing (100% OK) + 5/5 Smoke Test Checkpoints Passing** |

---

## 5. High-Level System Architecture

PMLA-SCWE follows a **Shared-Core Service-Oriented Architecture (SOA)**. The presentation layer (PySide6 Desktop and Flask Web) contains no business or analytical logic; all domain rules, analytical models, authorization checks, and database operations reside exclusively in the `core/` package.

```text
                           PMLA-SCWE SYSTEM ARCHITECTURE
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
┌───────────────────────────────┐                 ┌───────────────────────────────┐
│     PySide6 Desktop Client    │                 │       Flask Web Server        │
│   • Command Center Dashboard  │                 │   • Web Executive Dashboard   │
│   • Student 360° Profile Modal│                 │   • /students & /profile Views│
│   • Attendance & Assessments  │                 │   • /interventions Console    │
│   • Cyber-Wellness Audit View │                 │   • /reports Download Hub     │
│   • Predictive Analytics View │                 │   • /assistant Web Copilot    │
│   • Intervention Pipeline     │                 │   • /settings User Management │
│   • AI Assistant Chat & Voice │                 │   • Session Authentication    │
│   • ReportLab PDF Exporter GUI│                 │   • Responsive Glassmorphism  │
└───────────────────────────────┘                 └───────────────────────────────┘
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SHARED CORE SERVICES (core/)                          │
├───────────────────────────────┬─────────────────────────────────────────────────┤
│ Tenant & Security Services    │ • tenant_service.py (Organizations & Schools)   │
│                               │ • auth_service.py (Authentication & Hashing)    │
│                               │ • authorization_service.py (RBAC & Context)     │
│                               │ • user_service.py (Tenant-Aware Accounts)       │
├───────────────────────────────┼─────────────────────────────────────────────────┤
│ Student & Operational Services│ • student_service.py (Tenant-Scoped CRUD)       │
│                               │ • student_profile_service.py (Student 360° SSoT)│
│                               │ • attendance_service.py (Attendance & Streaks)  │
│                               │ • assessment_service.py (Diagnostic Scores)     │
│                               │ • wellness_service.py (Cyber-Audit & Wellness)  │
├───────────────────────────────┼─────────────────────────────────────────────────┤
│ Analytics & Decision Support  │ • analytics.py (Regression & Predictions)       │
│                               │ • risk_engine.py (0-100 Multi-Factor Risk)      │
│                               │ • explainability.py (Evidence Factors)          │
│                               │ • command_center_service.py (Institutional KPIs)│
│                               │ • recommendation.py (Teacher Decision Support)  │
│                               │ • notification_service.py (Smart Deduplication) │
├───────────────────────────────┼─────────────────────────────────────────────────┤
│ Interventions & Reporting     │ • intervention_service.py (Baseline Snapshots)  │
│                               │ • intervention_analytics.py (Deltas & Scoring)  │
│                               │ • report_service.py (Vector PDF & CSV Engine)   │
│                               │ • reports.py (Text/CSV Export Utilities)        │
├───────────────────────────────┼─────────────────────────────────────────────────┤
│ AI & Migration Infrastructure │ • ai_assistant.py (Gemini / OpenAI / Offline)   │
│                               │ • voice_service.py (pyttsx3 TTS & Voice Q&A)    │
│                               │ • migration_service.py (Schema_Migrations Engine│
│                               │ • backup_service.py (SQLite Snapshots & Dumps)  │
│                               │ • database.py (Connection Routing & Fallback)   │
└───────────────────────────────┴─────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE ROUTING LAYER                             │
│                           (core/database.py Abstraction)                        │
├────────────────────────────────────────┬────────────────────────────────────────┤
│          PRIMARY BACKEND: MySQL 8.0+   │        FALLBACK BACKEND: SQLite3       │
│          • Port 3306                   │        • Embedded zero-config file     │
│          • Connection Pooling & DDL    │        • pmla_scwe_fallback.db         │
│          • Multi-User Concurrency      │        • Automatic offline failover    │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 6. Complete Repository Structure

```text
PMLA-SCWE/
├── main.py                               # Application entry point (PySide6 or Flask)
├── requirements.txt                      # Project dependency specification
├── .env.example                          # Configuration template
├── .gitignore                            # Git exclusion rules
├── README.md                             # Authoritative project landing page
├── CHANGELOG.md                          # Release history & roadmap tracking
├── diagnose_setup.py                     # 5-stage setup verification diagnostic
├── seed_data.py                          # 100-student demonstration data seeder
├── seed_database.py                      # Idempotent DB initializer CLI wrapper
├── setup_and_run.bat                     # Windows automated launcher & installer
├── download_wheels.bat                   # Offline package downloader (Windows)
├── download_wheels.sh                    # Offline package downloader (Linux/macOS)
├── pmla_scwe_fallback.db                 # SQLite fallback database
├── schema.sql                            # Root compatibility mirror of schema
│
├── core/                                 # Shared Business Logic & Services
│   ├── config.py                         # App configuration & DB settings
│   ├── constants.py                      # System constants & enum definitions
│   ├── database.py                       # DB abstraction layer & routing
│   ├── auth_service.py                   # Authentication & PBKDF2 hashing
│   ├── authorization_service.py          # RBAC & AuthenticatedUser context
│   ├── tenant_service.py                 # Organizations & Schools management
│   ├── user_service.py                   # User account administration
│   ├── student_service.py                # Student CRUD & tenant scoping
│   ├── student_profile_service.py        # Student 360° intelligence SSoT
│   ├── attendance_service.py             # Attendance tracking & streak analytics
│   ├── assessment_service.py             # Diagnostic test logs & scoring
│   ├── wellness_service.py               # Cyber-safety & digital habit tracking
│   ├── analytics.py                      # OLS Linear Regression & LHS scoring
│   ├── risk_engine.py                    # Explainable 0-100 risk scoring
│   ├── explainability.py                 # Evidence synthesizer & SHAP-like factors
│   ├── recommendation.py                 # Teacher action recommendations
│   ├── notification_service.py           # Smart alerts & dedup cooldowns
│   ├── intervention_service.py           # Intervention lifecycles & baselines
│   ├── intervention_analytics.py         # Outcome evaluation & delta recovery
│   ├── report_service.py                 # ReportLab vector PDF & CSV builder
│   ├── reports.py                        # Tabular export utilities
│   ├── dashboard_service.py              # High-level KPI aggregations
│   ├── command_center_service.py         # Executive command center aggregator
│   ├── ai_assistant.py                   # Multi-provider AI copilot
│   ├── voice_service.py                  # Text-to-speech & audio recognition
│   ├── migration_service.py              # Versioned schema migration engine
│   ├── backup_service.py                 # Atomic SQLite snapshots & MySQL dumps
│   └── graphs.py                         # Matplotlib dark analytics renderers
│
├── desktop/                              # PySide6 Desktop Presentation Layer
│   ├── app.py                            # Main Qt application window & router
│   ├── theme.py                          # Modern dark CSS stylesheet & tokens
│   ├── login.py                          # Login dialog & credential handler
│   ├── dashboard.py                      # Executive Command Center view
│   ├── students.py                       # Student directory & management view
│   ├── student_profile_dialog.py         # Student 360° deep-dive modal
│   ├── attendance.py                     # Attendance tracking & registry view
│   ├── assessments.py                    # Diagnostic assessment logging view
│   ├── wellness.py                       # Cyber-wellness audit console
│   ├── analytics_view.py                 # Class analytics & predictive view
│   ├── interventions_view.py             # Closed-loop intervention pipeline
│   ├── reports_view.py                   # Report generation & PDF viewer
│   ├── ai_assistant_view.py              # AI conversational tutor & audio Q&A
│   ├── users_view.py                     # User management console (Admin)
│   └── widgets/                          # Reusable Qt custom components
│       ├── __init__.py
│       ├── animated_card.py              # Animated hover KPI card
│       ├── loading_indicator.py          # Smooth indeterminate spinner
│       └── reusable_ui_components.py     # Headers, badges, progress bars
│
├── web/                                  # Flask Web Presentation Layer
│   ├── __init__.py
│   ├── app.py                            # Flask application factory
│   ├── routes/                           # Blueprinted HTTP endpoints
│   │   ├── auth.py                       # Web authentication & session routes
│   │   ├── dashboard.py                  # Executive dashboard route
│   │   ├── students.py                   # Student directory & 360 profile
│   │   ├── attendance.py                 # Daily attendance registry routes
│   │   ├── assessments.py                # Assessment recording routes
│   │   ├── wellness.py                   # Cyber-wellness logging routes
│   │   ├── analytics.py                  # Class performance analytics
│   │   ├── interventions.py              # Intervention management console
│   │   ├── notifications.py              # Notification center & AJAX actions
│   │   ├── reports.py                    # PDF download & markdown preview
│   │   ├── assistant.py                  # AI assistant conversational web chat
│   │   └── settings.py                   # User settings & administration
│   ├── templates/                        # Jinja2 HTML templates
│   └── static/                           # CSS and JavaScript assets
│
├── database/                             # Database Assets & Migrations
│   ├── schema.sql                        # AUTHORITATIVE master DDL schema
│   ├── migrations/                       # Executable migration scripts
│   │   ├── __init__.py
│   │   └── v2_0_phase_1.py               # Phase 1 migration runner
│   └── backups/                          # Automated backup snapshot catalog
│       └── pmla_scwe_fallback_pre_v2_0_phase1_20260816_210017.db
│
├── tests/                                # Comprehensive Automated Test Suite
│   ├── smoke_test_v2.py                  # Phase 1 End-to-End Smoke Test
│   ├── test_authorization.py             # RBAC & AuthenticatedUser tests
│   ├── test_tenant_service.py            # Organizations & Schools tests
│   ├── test_v2_phase1_migration.py       # Migration pipeline & backup tests
│   ├── test_core.py                      # Core student & attendance tests
│   ├── test_command_center.py            # Command center aggregator tests
│   ├── test_intervention_service.py      # Intervention & delta scoring tests
│   ├── test_notifications.py             # Notification deduplication tests
│   ├── test_profile_service.py           # Student 360° profile tests
│   ├── test_reports.py                   # PDF & CSV reporting tests
│   ├── test_risk_engine.py               # Risk engine & LHS calculation tests
│   └── test_copilot.py                   # AI Copilot fallback tests
│
├── scripts/                              # Operations & Setup Utilities
│   └── setup_project.py                  # Safe cross-platform setup utility
│
└── documentation/                        # Authoritative Project Documentation
    ├── PROJECT_MASTER_DOCUMENTATION.md   # This comprehensive master reference
    ├── PROJECT_EVOLUTION.md              # Historical project evolution narrative
    ├── CURRENT_SYSTEM_ARCHITECTURE.md    # Active system architecture specifications
    ├── DATABASE_ARCHITECTURE.md          # MySQL/SQLite & multi-tenant schema
    ├── AUTHENTICATION_AND_RBAC.md        # Security, passwords & RBAC model
    ├── INSTALLATION_AND_SETUP.md         # Start-to-finish setup & launch guide
    ├── MIGRATION_AND_BACKUP_GUIDE.md     # Migration runbook & backup procedures
    ├── TESTING_AND_VERIFICATION.md       # Test suite specifications & results
    ├── DEVELOPMENT_ROADMAP.md            # Strategic product roadmap & Phase 2A
    └── REPOSITORY_CLEANUP_AND_CONSOLIDATION_REPORT.md # Checkpoint audit report
```

---

## 7. Multi-School Tenancy & Database Schema

### 7.1 Hierarchical Tenancy Model
Version 2.0 introduces structural multi-tenancy:

$$\text{Organizations (Root Tenant)} \xrightarrow{1:N} \text{Schools (Operational Tenant Unit)} \xrightarrow{1:N} \begin{cases} \text{Users (Staff / Faculty)} \\ \text{Students (Enrolled Learners)} \end{cases}$$

### 7.2 Core Relational Tables (13 Master Tables)

```text
Table 1: Schema_Migrations
├── migration_id (PK, INT AUTO_INCREMENT)
├── version (VARCHAR(50), UNIQUE)      -> e.g. 'v2_0_phase_1'
├── name (VARCHAR(150))                -> Descriptive migration title
├── applied_at (DATETIME)              -> Timestamp applied
├── checksum (VARCHAR(64))             -> SHA-256 validation hash
└── status (VARCHAR(20))               -> 'SUCCESS' / 'FAILED'

Table 2: Organizations
├── organization_id (PK, INT AUTO_INCREMENT)
├── name (VARCHAR(150))                -> Organization / Trust name
├── code (VARCHAR(50), UNIQUE)         -> Unique identifier (e.g. 'DEFAULT_ORG')
├── is_active (INT, DEFAULT 1)         -> Active state flag
└── created_at (DATETIME)

Table 3: Schools
├── school_id (PK, INT AUTO_INCREMENT)
├── organization_id (FK -> Organizations.organization_id)
├── name (VARCHAR(150))                -> School / Campus name
├── code (VARCHAR(50), UNIQUE)         -> Unique campus code (e.g. 'DEFAULT_SCHOOL')
├── is_active (INT, DEFAULT 1)
└── created_at (DATETIME)

Table 4: Users
├── user_id (PK, INT AUTO_INCREMENT)
├── username (VARCHAR(50), UNIQUE)
├── full_name (VARCHAR(100))
├── password_hash (VARCHAR(255))       -> PBKDF2-HMAC-SHA256 hash
├── role (VARCHAR(20))                 -> 'Admin', 'Teacher', 'Viewer'
├── status (VARCHAR(20))               -> 'Active' / 'Inactive' (legacy compat)
├── is_active (INT, DEFAULT 1)         -> Authoritative active flag
├── organization_id (FK -> Organizations.organization_id)
├── school_id (FK -> Schools.school_id)
├── created_at (DATETIME)
├── updated_at (DATETIME)
└── last_login (DATETIME)

Table 5: Students
├── student_id (PK, INT AUTO_INCREMENT)
├── school_id (FK -> Schools.school_id)
├── first_name (VARCHAR(50))
├── last_name (VARCHAR(50))
├── class_section (VARCHAR(20))        -> e.g. 'XII-A'
├── dob (DATE)
├── gender (CHAR(1))                   -> 'M', 'F', 'O'
├── email (VARCHAR(100))
├── phone (VARCHAR(20))
└── created_at (DATETIME)

Table 6: Attendance
├── attendance_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── attendance_date (DATE)
├── status (CHAR(1))                   -> 'P' (Present) / 'A' (Absent)
└── UNIQUE(student_id, attendance_date)

Table 7: Learning_Objectives
├── objective_id (PK, INT AUTO_INCREMENT)
├── topic_name (VARCHAR(100), UNIQUE)
├── description (TEXT)
└── created_at (DATETIME)

Table 8: Diagnostic_Logs
├── log_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── objective_id (FK -> Learning_Objectives.objective_id)
├── score_obtained (DECIMAL(5,2))
├── max_score (DECIMAL(5,2), DEFAULT 100.00)
├── assessment_date (DATE)
└── remarks (VARCHAR(255))

Table 9: Cyber_Audit
├── audit_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── audit_date (DATE)
├── daily_screen_time_hours (DECIMAL(4,2))
├── study_screen_time_hours (DECIMAL(4,2))
├── recreational_screen_time_hours (DECIMAL(4,2))
├── sleep_duration_hours (DECIMAL(4,2))
├── digital_distraction_level (INT)    -> 1 (Low) to 5 (Severe)
└── cyber_safety_awareness_rating (INT)-> 1 (Poor) to 5 (Exemplary)

Table 10: Weekly_Progress
├── progress_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── week_number (INT)                  -> 1, 2, 3, 4...
├── score (DECIMAL(5,2))               -> Weekly assessment score
├── recorded_date (DATE)
└── UNIQUE(student_id, week_number)

Table 11: Achievements
├── achievement_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── badge_name (VARCHAR(100))
├── description (VARCHAR(255))
└── awarded_date (DATE)

Table 12: Notifications
├── notification_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE, NULLABLE)
├── priority (VARCHAR(20))             -> 'HIGH', 'MEDIUM', 'LOW'
├── category (VARCHAR(50))             -> 'ACADEMIC', 'ATTENDANCE', 'CYBER_WELLNESS', 'MILESTONE'
├── title (VARCHAR(150))
├── message (TEXT)
├── is_read (INT, DEFAULT 0)
├── dedup_key (VARCHAR(100))           -> Deduplication hash
├── created_at (DATETIME)
└── expires_at (DATETIME)

Table 13: Interventions
├── intervention_id (PK, INT AUTO_INCREMENT)
├── student_id (FK -> Students.student_id ON DELETE CASCADE)
├── assigned_by_user_id (FK -> Users.user_id)
├── title (VARCHAR(150))
├── description (TEXT)
├── status (VARCHAR(30))               -> 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'ESCALATED'
├── target_date (DATE)
├── pre_risk_score (DECIMAL(5,2))      -> Baseline Risk Snapshot
├── pre_academic_avg (DECIMAL(5,2))    -> Baseline Academic Snapshot
├── pre_attendance_rate (DECIMAL(5,2)) -> Baseline Attendance Snapshot
├── pre_lhs_score (DECIMAL(5,2))       -> Baseline LHS Snapshot
├── post_risk_score (DECIMAL(5,2))     -> Evaluated Risk
├── post_academic_avg (DECIMAL(5,2))   -> Evaluated Academic
├── post_attendance_rate (DECIMAL(5,2))-> Evaluated Attendance
├── post_lhs_score (DECIMAL(5,2))      -> Evaluated LHS
├── effectiveness_score (DECIMAL(5,2)) -> 0 to 100 Recovery Score
├── outcome_notes (TEXT)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

---

## 8. Authentication, Password Security & RBAC Foundation

### 8.1 Password Hashing Architecture
Passwords are secure against offline dictionary attacks using **PBKDF2-HMAC-SHA256**:
- **Algorithm**: `pbkdf2:sha256:100000` (100,000 iterations with 16-byte cryptographically secure salt).
- **Format**: `pbkdf2:sha256:100000$<salt_hex>$<hash_hex>`.
- **Legacy Compatibility**: The authentication engine transparently verifies legacy raw SHA-256 and MD5 hashes from earlier project phases without locking out legacy users.

### 8.2 Centralized `AuthenticatedUser` Context
User sessions are encapsulated in an immutable Python dataclass (`core/authorization_service.py`):

```python
@dataclass(slots=True)
class AuthenticatedUser:
    user_id: int
    username: str
    full_name: str
    role: str                       # "Admin", "Teacher", "Viewer"
    organization_id: int | None = None
    school_id: int | None = None
    is_active: bool = True
```

### 8.3 Server-Side Identity Revalidation
To protect against client-side tampering, the service layer reloads the fresh database state via `get_authenticated_user_context(user_id)` prior to high-stakes mutations:
- Deactivated accounts (`is_active = 0` or `status = 'Inactive'`) are immediately rejected.
- Modified roles take effect on the very next service call.

### 8.4 Role Capability Matrix (Phase 1 Baseline)

| Capability / Action | Service Enforcement Function | Admin | Teacher | Viewer |
| :--- | :--- | :---: | :---: | :---: |
| **System User Administration** | `can_manage_users(user)` | **ALLOW** | DENY | DENY |
| **Organizations & Schools CRUD** | `can_manage_organizations(user)`| **ALLOW** | DENY | DENY |
| **Cross-School Scope Access** | `has_school_access(user, school_id)`| **ALL SCHOOLS**| Assigned School Only | Assigned School Only |
| **Register / Edit Students** | `can_modify_students(user)` | **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **Log Attendance Records** | `can_record_attendance(user)` | **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **Log Diagnostic Tests** | `can_modify_students(user)` | **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **Create / Update Interventions**| `can_create_interventions(user)`| **ALLOW** | **ALLOW** | DENY (Read-Only) |
| **View Analytics & Dashboards** | `can_view_analytics(user)` | **ALLOW** | **ALLOW** | **ALLOW** |
| **Generate & Export PDF Reports**| `can_generate_reports(user)` | **ALLOW** | **ALLOW** | **ALLOW** |

> [!IMPORTANT]
> **Phase 2A Boundary Notice**: Version 2.0 Phase 1 implements and unit-tests all authorization functions in `core/authorization_service.py`. The visual UI enforcement (hiding navigation items and locking input controls in the desktop client) is scheduled for **Version 2.0 Phase 2A**.

---

## 9. Mathematical Formulations & Analytical Logic

### 9.1 Simple Linear Regression (Academic Trajectory Forecasting)
To forecast future performance without introducing opaque black-box deep learning models, PMLA-SCWE applies **Ordinary Least Squares (OLS) Linear Regression** over longitudinal weekly scores $(x_i, y_i)$ where $x_i = [1, 2, \dots, N]$:

$$\text{Slope } m = \frac{N \sum_{i=1}^N (x_i y_i) - \left(\sum_{i=1}^N x_i\right) \left(\sum_{i=1}^N y_i\right)}{N \sum_{i=1}^N (x_i^2) - \left(\sum_{i=1}^N x_i\right)^2}$$

$$\text{Intercept } c = \frac{\sum_{i=1}^N y_i - m \sum_{i=1}^N x_i}{N}$$

$$\text{Predicted Next Score } \hat{y}_{N+1} = \text{clamp}\Big(m \cdot (N + 1) + c, \; 0, \; 100\Big)$$

**Trajectory Classification**:
- **Improving**: $m > +0.10$ pts/week
- **Declining**: $m < -0.10$ pts/week
- **Stable**: $-0.10 \le m \le +0.10$ pts/week

---

### 9.2 Learning Health Score (LHS) Formulation
The composite Learning Health Score ($0 \le \text{LHS} \le 100$) integrates academic, attendance, and cyber-wellness dimensions:

$$\text{LHS} = 0.40 \cdot \bar{A}_{\text{academic}} + 0.40 \cdot R_{\text{attendance}} + 0.20 \cdot W_{\text{cyber}}$$

Where:
- $\bar{A}_{\text{academic}} = \frac{1}{K} \sum_{k=1}^K \left(\frac{\text{score}_k}{\text{max\_score}_k} \cdot 100\right)$ (Mean Diagnostic Score)
- $R_{\text{attendance}} = \frac{\text{Days Present}}{\text{Total Enrolled Days}} \cdot 100$
- $W_{\text{cyber}} = \text{Cyber-Wellness Score } (0 \text{ to } 100)$ computed from sleep duration, screen-time balance, and safety ratings:

$$W_{\text{cyber}} = \text{clamp}\Big(100 - (\text{Excess Screen Time} \cdot 10) - (\text{Sleep Deficit} \cdot 15) - (\text{Distraction Level} \cdot 8) + (\text{Safety Rating} \cdot 5), \; 0, \; 100\Big)$$

---

### 9.3 Explainable Risk Engine Formulation
Risk Score ($0 \le \text{Risk} \le 100$) is computed deterministically from 4 weighted deficits:

$$\text{Risk Score} = 0.40 \cdot D_{\text{acad}} + 0.30 \cdot D_{\text{att}} + 0.20 \cdot D_{\text{cyber}} + 0.10 \cdot D_{\text{trend}}$$

Where:
- $D_{\text{acad}} = \text{clamp}(100 - \bar{A}_{\text{academic}}, \; 0, \; 100)$
- $D_{\text{att}} = \text{clamp}\left(\frac{75 - R_{\text{attendance}}}{75} \cdot 100, \; 0, \; 100\right)$ (Deficit relative to CBSE 75% target)
- $D_{\text{cyber}} = \text{clamp}(100 - W_{\text{cyber}}, \; 0, \; 100)$
- $D_{\text{trend}} = \begin{cases} 100 & \text{if } m < -0.50 \\ 50 & \text{if } -0.50 \le m < -0.10 \\ 0 & \text{if } m \ge -0.10 \end{cases}$

**Risk Tiers**:
- **HIGH RISK** ($\text{Risk} \ge 60$ or $R_{\text{attendance}} < 75\%$ or $\text{LHS} < 50$): Requires immediate intervention.
- **MEDIUM RISK** ($35 \le \text{Risk} < 60$): Targeted advisory monitoring.
- **LOW RISK** ($\text{Risk} < 35$): Healthy baseline progress.

---

### 9.4 Closed-Loop Intervention Effectiveness Scoring
When an intervention is evaluated, recovery effectiveness is measured against the pre-intervention snapshot:

$$\Delta_{\text{Risk}} = \text{Pre\_Risk} - \text{Post\_Risk} \quad (\text{Positive is good})$$
$$\Delta_{\text{LHS}} = \text{Post\_LHS} - \text{Pre\_LHS} \quad (\text{Positive is good})$$
$$\Delta_{\text{Att}} = \text{Post\_Attendance} - \text{Pre\_Attendance}$$

$$\text{Effectiveness Score} = \text{clamp}\Big(50 + (\Delta_{\text{Risk}} \cdot 0.5) + (\Delta_{\text{LHS}} \cdot 0.5) + (\Delta_{\text{Att}} \cdot 0.2), \; 0, \; 100\Big)$$

**Outcome Categories**:
- **Highly Effective**: Score $\ge 75$
- **Effective**: $50 \le \text{Score} < 75$
- **Moderate Improvement**: $25 \le \text{Score} < 50$
- **Needs Review / Escalated**: Score $< 25$

---

## 10. Database Migration Engine & Backup Infrastructure

### 10.1 Versioned Migration Tracking
Applied database migrations are tracked in the `Schema_Migrations` table:
- Checked idempotently via `core/migration_service.py:is_migration_applied(version)`.
- Verified pre- and post-migration row counts to guarantee zero data loss.

### 10.2 Version 2.0 Phase 1 Migration Runbook
To execute the multi-school tenancy migration on active database backends:
```powershell
.venv\Scripts\python.exe -m database.migrations.v2_0_phase_1
```

**Automated Migration Pipeline Steps**:
1. **Atomic Backup**: Online SQLite snapshot created in `database/backups/pmla_scwe_fallback_pre_v2_0_phase1_<timestamp>.db`.
2. **Pre-Migration Baseline**: Counts rows in `Students`, `Attendance`, `Diagnostic_Logs`, `Cyber_Audit`, etc.
3. **DDL Execution**: Creates `Schema_Migrations`, `Organizations`, and `Schools` tables (`IF NOT EXISTS`).
4. **Dynamic Tenant Provisioning**: Seeds `DEFAULT_ORG` and `DEFAULT_SCHOOL` if missing.
5. **Safe Column Alterations**: Non-destructively adds `school_id` to `Students`, and `organization_id`, `school_id`, `is_active`, `updated_at` to `Users`.
6. **Data Backfilling**: Links all existing students and users to `DEFAULT_SCHOOL` and `DEFAULT_ORG`.
7. **Indexes**: Creates performance indexes on `Students(school_id)`, `Schools(organization_id)`, and `Users(school_id)`.
8. **Row-Count Assertions**: Asserts pre-count $==$ post-count across all operational tables.
9. **Commit Version**: Records `v2_0_phase_1` in `Schema_Migrations`.

---

## 11. Verification & Testing

### 11.1 Full Automated Unit Test Suite
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```
**Actual Verification Baseline**:
```text
Ran 78 tests in 92.201s — OK (0 Failures, 0 Errors, 0 Regressions)
```

### 11.2 End-to-End Smoke Test
```powershell
.venv\Scripts\python.exe tests\smoke_test_v2.py
```
**Actual Verification Baseline**:
```text
============================================================
 PMLA-SCWE VERSION 2.0 PHASE 1 -- END-TO-END SMOKE TEST
============================================================
[1/5] Testing Tenant Resolution & Admin Login...       [PASS]
[2/5] Testing Student Registration & Lookup...         [PASS]
[3/5] Testing Attendance Logging...                    [PASS]
[4/5] Testing Dashboard & Student 360 Analytics...     [PASS]
[5/5] Testing RBAC Roles & School Scoping...           [PASS]
============================================================
 [SUCCESS] ALL 5 SMOKE TEST CHECKPOINTS PASSED!
============================================================
```

### 11.3 Environment Diagnostics
```powershell
.venv\Scripts\python.exe diagnose_setup.py
```
**Diagnostics Summary**:
- Python Environment: `[PASS]` (Python 3.10+)
- Package Dependencies: `[PASS]` (All 11 required packages installed)
- Configuration: `[PASS]` (`.env` present)
- Database Connectivity: `[PASS]` (MySQL Primary reachable, SQLite fallback ready)
- Database Schema: `[PASS]` (All tables verified)

---

## 12. Security Considerations

- **Secrets Isolation**: `.env` and sensitive API keys are strictly excluded via `.gitignore` and must never be committed to source control.
- **Authoritative Service Enforcement**: Client-side UI controls are for usability only. Authoritative authorization is strictly enforced on the server/service side.
- **SQL Injection Prevention**: All queries in `core/database.py` utilize parameterized SQL queries (`%s` in MySQL, `?` in SQLite) rather than string interpolation.
- **Cascade Deletions**: Deleting a student cascades safely to related attendance and assessment logs, preventing orphaned relational records.

---

## 13. Development Resume Marker

```text
================================================================================
                    PMLA-SCWE DEVELOPMENT RESUME POINT
================================================================================

CURRENT CHECKPOINT:
  Version 2.0 Phase 1 COMPLETE

NEXT CHECKPOINT TO RESUME:
  Version 2.0 Phase 2A — Desktop AuthenticatedUser Context & Desktop RBAC Integration

EXACT SCOPE FOR PHASE 2A:
  1. Inspect Desktop Login Flow (desktop/login.py).
  2. Connect login result to centralized AuthenticatedUser context.
  3. Propagate AuthenticatedUser into Desktop MainWindow (desktop/app.py).
  4. Implement role-aware sidebar navigation (hide/show views based on role).
  5. Enforce Admin-only access to Users management (desktop/users_view.py).
  6. Enforce Teacher/Admin operational controls (disable edit/delete for Viewer).
  7. Verify Admin, Teacher, and Viewer user flows in Desktop UI.

DO NOT IMPLEMENT PHASE 2A DURING THIS MAINTENANCE TASK.
================================================================================
```
