# PMLA-SCWE: Database Architecture & Relational Schema
## Comprehensive Data Layer & Multi-Tenancy Specification — Version 2.0 (Phase 1)

---

## 1. Dual-Backend Architecture Strategy

PMLA-SCWE implements a resilient **Dual-Backend Data Layer** managed through the abstraction engine in `core/database.py`:

```text
┌────────────────────────────────────────┬────────────────────────────────────────┐
│            PRIMARY BACKEND             │            FALLBACK BACKEND            │
│               MySQL 8.0+               │                SQLite3                 │
├────────────────────────────────────────┼────────────────────────────────────────┤
│ • Production & multi-user concurrent   │ • Embedded zero-configuration runtime  │
│ • Listens on TCP port 3306             │ • File path: pmla_scwe_fallback.db     │
│ • Full relational integrity (InnoDB)   │ • Engaged automatically if MySQL fails │
│ • Configured via .env environment vars │ • Ideal for offline evaluator laptops  │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Data Independence Notice**: MySQL and SQLite are alternative runtime backends, not an active-active synchronized pair. Changes made when connected to MySQL reside in MySQL; changes made during offline SQLite fallback reside in `pmla_scwe_fallback.db`.

---

## 2. Authoritative Master Schema vs. Compatibility Mirror

The repository contains two schema files:
1. **`database/schema.sql` (AUTHORITATIVE MASTER SOURCE)**: The canonical, master DDL schema definition maintained for the project. Used by `core/database.py`, `seed_database.py`, and migration scripts.
2. **`schema.sql` (ROOT COMPATIBILITY MIRROR)**: Kept at the repository root as an exact convenience mirror for external tools and developers expecting a root-level DDL file.

Both files share identical table structures and SHA-256 integrity definitions.

---

## 3. Detailed Entity Schema Specifications (13 Master Tables)

### 3.1 `Schema_Migrations` (Version Tracking)
Tracks applied schema migrations idempotently.
```sql
CREATE TABLE IF NOT EXISTS Schema_Migrations (
    migration_id INT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'SUCCESS'
);
```

### 3.2 `Organizations` (Root Multi-Tenancy Boundary)
Represents the educational trust, district, or governing organization.
```sql
CREATE TABLE IF NOT EXISTS Organizations (
    organization_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 `Schools` (Operational Tenant Unit)
Represents an individual school, campus, or branch under an organization.
```sql
CREATE TABLE IF NOT EXISTS Schools (
    school_id INT PRIMARY KEY AUTO_INCREMENT,
    organization_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE RESTRICT
);
```

### 3.4 `Users` (Faculty, Staff & Administrators)
Accounts for system access with RBAC roles and tenant associations.
```sql
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Teacher',
    status VARCHAR(20) DEFAULT 'Active',
    is_active INT DEFAULT 1,
    organization_id INT DEFAULT 1,
    school_id INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE SET NULL,
    FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE SET NULL
);
```

### 3.5 `Students` (Enrolled Learners)
Core student demographic and enrollment registry scoped to a school.
```sql
CREATE TABLE IF NOT EXISTS Students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT DEFAULT 1,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    class_section VARCHAR(20) NOT NULL,
    dob DATE,
    gender CHAR(1),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE RESTRICT
);
```

### 3.6 `Attendance` (Daily Attendance Logs)
Daily attendance tracking with present (`P`) or absent (`A`) status.
```sql
CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status CHAR(1) NOT NULL,
    UNIQUE(student_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

### 3.7 `Learning_Objectives` (Curriculum Objectives)
Academic subject topics and descriptions.
```sql
CREATE TABLE IF NOT EXISTS Learning_Objectives (
    objective_id INT PRIMARY KEY AUTO_INCREMENT,
    topic_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.8 `Diagnostic_Logs` (Assessment Scores)
Granular assessment evaluations mapped to specific learning objectives.
```sql
CREATE TABLE IF NOT EXISTS Diagnostic_Logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    objective_id INT NOT NULL,
    score_obtained DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2) DEFAULT 100.00,
    assessment_date DATE NOT NULL,
    remarks VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (objective_id) REFERENCES Learning_Objectives(objective_id) ON DELETE CASCADE
);
```

### 3.9 `Cyber_Audit` (Digital Wellness Logs)
Student cyber-habits, screen time, sleep duration, and digital safety ratings.
```sql
CREATE TABLE IF NOT EXISTS Cyber_Audit (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    audit_date DATE NOT NULL,
    daily_screen_time_hours DECIMAL(4,2),
    study_screen_time_hours DECIMAL(4,2),
    recreational_screen_time_hours DECIMAL(4,2),
    sleep_duration_hours DECIMAL(4,2),
    digital_distraction_level INT,
    cyber_safety_awareness_rating INT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

### 3.10 `Weekly_Progress` (Longitudinal Trajectory Data)
Weekly performance data used by the regression engine for trend forecasting.
```sql
CREATE TABLE IF NOT EXISTS Weekly_Progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    week_number INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    recorded_date DATE NOT NULL,
    UNIQUE(student_id, week_number),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

### 3.11 `Achievements` (Gamification & Badges)
Student recognition badges and positive reinforcement awards.
```sql
CREATE TABLE IF NOT EXISTS Achievements (
    achievement_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    awarded_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

### 3.12 `Notifications` (Decision-Support Alerts)
System alerts with deduplication hashing (`dedup_key`) and expiration tracking.
```sql
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    category VARCHAR(50) DEFAULT 'ACADEMIC',
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read INT DEFAULT 0,
    dedup_key VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

### 3.13 `Interventions` (Closed-Loop Remedial Actions)
Pedagogical intervention cases with baseline metric snapshots and evaluated outcome deltas.
```sql
CREATE TABLE IF NOT EXISTS Interventions (
    intervention_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    assigned_by_user_id INT,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    status VARCHAR(30) DEFAULT 'PLANNED',
    target_date DATE,
    pre_risk_score DECIMAL(5,2),
    pre_academic_avg DECIMAL(5,2),
    pre_attendance_rate DECIMAL(5,2),
    pre_lhs_score DECIMAL(5,2),
    post_risk_score DECIMAL(5,2),
    post_academic_avg DECIMAL(5,2),
    post_attendance_rate DECIMAL(5,2),
    post_lhs_score DECIMAL(5,2),
    effectiveness_score DECIMAL(5,2),
    outcome_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);
```

---

## 4. Performance Indexes

The schema creates dedicated B-Tree indexes for tenant boundary queries and foreign key lookups:
- `idx_students_school ON Students(school_id)`
- `idx_schools_org ON Schools(organization_id)`
- `idx_users_school ON Users(school_id)`
- `idx_users_org ON Users(organization_id)`
- `idx_attendance_student_date ON Attendance(student_id, attendance_date)`
- `idx_notifications_dedup ON Notifications(dedup_key, is_read)`

---

## 5. Dynamic Default Tenant Provisioning

To guarantee seamless backward compatibility with existing single-school databases without breaking FK constraints, the system automatically provisions default tenant records on boot or migration:
- **Default Organization**: `PMLA-SCWE Default Organization` (Code: `DEFAULT_ORG`, ID: `1`)
- **Default School**: `Default School` (Code: `DEFAULT_SCHOOL`, ID: `1`, Org: `1`)
