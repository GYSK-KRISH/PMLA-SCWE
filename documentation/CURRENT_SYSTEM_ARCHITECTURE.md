# PMLA-SCWE: Current System Architecture Specifications
## Version 2.0 (Phase 1 Checkpoint) Architectural Blueprint

---

## 1. High-Level Service-Oriented Architecture (SOA)

PMLA-SCWE employs a **Shared-Core Service-Oriented Architecture (SOA)** where presentation frontends are strictly decoupled from business logic and analytical algorithms:

```mermaid
flowchart TD
    subgraph Presentation_Layer [Presentation Frontends]
        DESK["PySide6 Desktop Client (Qt 6)"]
        WEB["Flask Web Console (Jinja2)"]
    end

    subgraph Security_Layer [Authentication & Authorization]
        AUTH["auth_service.py (PBKDF2 Hashing)"]
        RBAC["authorization_service.py (AuthenticatedUser Context)"]
        USER["user_service.py (Tenant Accounts)"]
    end

    subgraph Shared_Core_Services [Shared Core Services (core/)]
        P360["student_profile_service.py (Student 360° SSoT)"]
        RISK["risk_engine.py (0-100 Risk Engine)"]
        EXP["explainability.py (Evidence Factors)"]
        ANLY["analytics.py (OLS Linear Regression & LHS)"]
        CMD["command_center_service.py (Executive KPIs)"]
        NOTIF["notification_service.py (Smart Deduplication)"]
        IVS["intervention_service.py (Baseline Snapshots)"]
        IVA["intervention_analytics.py (Deltas & Scoring)"]
        REP["report_service.py (ReportLab Vector PDF & CSV)"]
        AI["ai_assistant.py (Gemini / OpenAI / Offline Engine)"]
        TEN["tenant_service.py (Organizations & Schools)"]
        MIG["migration_service.py (Schema Migrations Engine)"]
        BAK["backup_service.py (SQLite Snapshots & Dumps)"]
    end

    subgraph Data_Routing_Layer [Database Abstraction Layer (core/database.py)]
        ROUTER{"Connection Router & Active Backend Detector"}
        MYSQL[("MySQL 8.0+ Primary (Port 3306)")]
        SQLITE[("SQLite3 Fallback (pmla_scwe_fallback.db)")]
    end

    DESK --> AUTH
    DESK --> RBAC
    DESK --> Shared_Core_Services

    WEB --> AUTH
    WEB --> RBAC
    WEB --> Shared_Core_Services

    Security_Layer --> ROUTER
    Shared_Core_Services --> ROUTER

    ROUTER -->|Primary Reachable| MYSQL
    ROUTER -->|MySQL Offline / Failover| SQLITE
```

---

## 2. Multi-School Tenancy Hierarchy

Version 2.0 establishes hierarchical tenant boundaries:

```text
                     ORGANIZATIONS (Root Tenant Boundary)
                               │
                               │ 1 : N
                               ▼
                        SCHOOLS (Operational Tenant Unit)
                               │
           ┌───────────────────┴───────────────────┐
           ▼                                       ▼
         USERS                                  STUDENTS
  (Faculty & Administrators)               (Enrolled Learners)
           │                                       │
           ├── user_id                             ├── student_id
           ├── username                            ├── school_id (FK)
           ├── role (Admin/Teacher/Viewer)         ├── first_name, last_name
           ├── organization_id (FK)                ├── class_section
           └── school_id (FK)                      │
                                                   ├── Attendance (via student_id)
                                                   ├── Diagnostic_Logs (via student_id)
                                                   ├── Cyber_Audit (via student_id)
                                                   ├── Weekly_Progress (via student_id)
                                                   ├── Achievements (via student_id)
                                                   └── Interventions (via student_id)
```

---

## 3. Authentication & Server-Side Revalidation Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Faculty Member
    participant Client as Presentation (PySide6 / Flask)
    participant Auth as core/auth_service.py
    participant RBAC as core/authorization_service.py
    participant DB as core/database.py (MySQL / SQLite)

    User->>Client: Enters Credentials (Username, Password)
    Client->>Auth: login_user(username, password)
    Auth->>DB: Query Users row by username
    DB-->>Auth: Users row (with password_hash, role, organization_id, school_id, is_active)
    Auth->>Auth: verify_password(entered_pass, stored_hash)
    
    alt Invalid Password or Inactive User
        Auth-->>Client: Return None (Authentication Failed)
        Client-->>User: Display Error Message
    else Valid Credentials & Active Account
        Auth-->>Client: Return user session dictionary
        Client->>Client: Construct AuthenticatedUser Context
    end

    Note over Client,RBAC: Subsequent Protected Operations (e.g. Modify Student, Log Test)...

    Client->>RBAC: can_modify_students(user_context)
    RBAC->>RBAC: Verify role in ('Admin', 'Teacher') & is_active == True
    RBAC->>DB: get_authenticated_user_context(user_id) (Server Revalidation)
    DB-->>RBAC: Fresh Database State
    RBAC-->>Client: Permission GRANTED / DENIED
```

---

## 4. RBAC Capability & Boundary Scoping Matrix

```text
┌──────────────────────────────┬───────────────────┬───────────────────┬───────────────────┐
│ System Capability            │ Admin Role        │ Teacher Role      │ Viewer Role       │
├──────────────────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ Manage Users                 │ ALLOW             │ DENY              │ DENY              │
│ Manage Organizations/Schools │ ALLOW             │ DENY              │ DENY              │
│ School Access Scope          │ ALL Schools       │ Assigned School   │ Assigned School   │
│ Create/Edit Students         │ ALLOW             │ ALLOW             │ DENY (Read-Only)  │
│ Record Daily Attendance      │ ALLOW             │ ALLOW             │ DENY (Read-Only)  │
│ Log Diagnostic Tests         │ ALLOW             │ ALLOW             │ DENY (Read-Only)  │
│ Log Cyber-Wellness Audits    │ ALLOW             │ ALLOW             │ DENY (Read-Only)  │
│ Create/Manage Interventions  │ ALLOW             │ ALLOW             │ DENY (Read-Only)  │
│ View Analytics & Dashboards  │ ALLOW             │ ALLOW             │ ALLOW             │
│ Export PDF & CSV Reports     │ ALLOW             │ ALLOW             │ ALLOW             │
└──────────────────────────────┴───────────────────┴───────────────────┴───────────────────┘
```

---

## 5. Database Connection Routing & Abstraction Architecture

`core/database.py` handles database communication dynamically:

```text
                        get_connection()
                               │
            Is mysql-connector-python available?
                     ├── No ──► Connect to SQLite (pmla_scwe_fallback.db)
                     │
                    Yes
                     │
            Attempt connection to MySQL (Port 3306)
                     ├── Success ──► Return MySQL Connection (Primary Mode)
                     └── Failure ──► Fall back to SQLite (pmla_scwe_fallback.db)
```

- **Parameterized Queries**: All SQL execution uses parameterized placeholders (`%s` for MySQL, `?` for SQLite) via query normalization in `_normalize_query()`.
- **Foreign Key Constraints**: Foreign keys are enabled on both MySQL (`ENGINE=InnoDB`) and SQLite (`PRAGMA foreign_keys = ON`).

---

## 6. Migration Pipeline Architecture

```mermaid
flowchart TD
    A[Start Migration: run_v2_phase1_migration] --> B[Create Atomic SQLite Snapshot Backup in database/backups/]
    B --> C[Capture Pre-Migration Row Count Baseline across All Tables]
    C --> D{Is v2_0_phase_1 recorded in Schema_Migrations?}
    D -- Yes --> E[Skip DDL & Return already_applied = True]
    D -- No --> F[Execute DDL: Create Schema_Migrations, Organizations, Schools IF NOT EXISTS]
    F --> G[Dynamically Provision DEFAULT_ORG and DEFAULT_SCHOOL if missing]
    G --> H[Alter Students: Add school_id INT DEFAULT 1]
    H --> I[Alter Users: Add organization_id, school_id, is_active, updated_at]
    I --> J[Backfill Data: Associate existing Students & Users with Default Tenant IDs]
    J --> K[Create Performance Indexes on school_id and organization_id]
    K --> L[Verify Post-Migration Row Count Equality: Before == After]
    L --> M[Commit Version v2_0_phase_1 to Schema_Migrations Table]
    M --> N[Return Success Report]
```
