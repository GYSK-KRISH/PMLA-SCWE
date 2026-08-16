# PMLA-SCWE: System Architecture, Database Schema & ER Diagram

**Version 1.8 — Submission Edition**

> [!NOTE]
> **STATUS: HISTORICAL / ARCHIVAL DOCUMENT (v1.8 System Architecture & ERD Archive)**  
> This file is preserved for historical reference. For the active Version 2.0 multi-school multi-tenant architecture and schema specifications, see:
> - Current Architecture: [CURRENT_SYSTEM_ARCHITECTURE.md](file:///d:/PMLA-SCWE/documentation/CURRENT_SYSTEM_ARCHITECTURE.md)
> - Database Architecture: [DATABASE_ARCHITECTURE.md](file:///d:/PMLA-SCWE/documentation/DATABASE_ARCHITECTURE.md)
> - Master Documentation: [PROJECT_MASTER_DOCUMENTATION.md](file:///d:/PMLA-SCWE/documentation/PROJECT_MASTER_DOCUMENTATION.md)

---

## 1. High-Level Closed-Loop Architecture

The PMLA-SCWE platform implements a **closed-loop educational intelligence lifecycle**:

```mermaid
flowchart TD
    subgraph Data Layer
        DB[(MySQL Database / SQLite Fallback)]
        S[Students] --> DB
        ATT[Daily Attendance] --> DB
        DIAG[Diagnostic Assessments] --> DB
        WP[Weekly Progress] --> DB
        CW[Cyber Wellness Audits] --> DB
        IV[Interventions & Baselines] --> DB
        NOTIF[Smart Notifications] --> DB
    end

    subgraph Intelligence & Analytics Layer (core/)
        P360[Student 360° Profile Service]
        LHS[Learning Health Score Engine]
        RISK[Explainable Risk Engine]
        EXP[Explainability Evidence Synthesizer]
        COP[AI Teacher Copilot with Offline Engine]
        IVA[Intervention Analytics & Deltas]
        NOTS[Smart Notification Engine]
        CMD[Executive Command Center Aggregator]
        REP[Report Generation Engine]

        DB --> P360
        P360 --> LHS
        P360 --> RISK
        RISK --> EXP
        EXP --> NOTS
        P360 --> COP
        DB --> IVA
        NOTS --> CMD
        IVA --> CMD
        LHS --> CMD
        RISK --> CMD
        P360 --> REP
        IVA --> REP
    end

    subgraph Dual Presentation Layer
        GUI[PySide6 Desktop Application]
        WEB[Flask Web Console]
        
        CMD --> GUI
        CMD --> WEB
        COP --> GUI
        COP --> WEB
        REP --> GUI
        REP --> WEB
    end
```

---

## 2. Intelligence Cycle Workflow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Teacher as Educator / School Admin
    participant UI as Presentation (PySide6 / Flask)
    participant CC as Command Center & Notifications
    participant Core as Core Analytics & Risk Engine
    participant Copilot as AI Teacher Copilot
    participant Interv as Intervention Service
    participant DB as Relational Database

    Teacher->>UI: Opens Dashboard / Command Center
    UI->>CC: Request Executive Intelligence Overview
    CC->>Core: Aggregate 360° Metrics, LHS & Risk Scores
    Core->>DB: Query Attendance, Tests, Audits, Progress
    DB-->>Core: Raw Student Records
    Core->>CC: Stratified Risk Levels & Smart Actions
    CC-->>UI: Render Executive KPIs & Action Cards

    Teacher->>UI: Selects High-Priority Student Case
    UI->>Copilot: Trigger Copilot ("Explain Risk" / "Create Intervention")
    Copilot->>Core: Fetch Student 360° Context
    Copilot-->>UI: Grounded Advisory Strategy (Human-in-the-Loop)

    Teacher->>UI: Confirms & Submits Intervention Plan
    UI->>Interv: Create Intervention(student_id, title, target_date)
    Interv->>Core: Snapshot Current Baseline Metrics (pre_risk, pre_academic, pre_attendance, pre_lhs)
    Interv->>DB: Insert Intervention Record with Baseline
    DB-->>UI: Status: IN_PROGRESS

    Note over Teacher,DB: Days / Weeks of Remedial Teaching & Ongoing Tests...

    Teacher->>UI: Clicks "Evaluate Outcome"
    UI->>Interv: Evaluate Outcome(intervention_id)
    Interv->>Core: Fetch Current Metrics vs Baseline
    Core->>Interv: Compute Before vs After Deltas & 0–100 Effectiveness Score
    Interv->>DB: Update Status (RESOLVED / NEEDS_REVIEW) + Post Metrics + Score
    Interv-->>UI: Display Multi-Dimensional Recovery Matrix
```

---

## 3. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    Students ||--o{ Attendance : "logs daily"
    Students ||--o{ Diagnostic_Logs : "records test marks"
    Students ||--o{ Weekly_Progress : "tracks weekly trend"
    Students ||--o{ Cyber_Audit : "audits wellness"
    Students ||--o{ Achievements : "earns badges"
    Students ||--o{ Activity_Log : "generates events"
    Students ||--o{ Reports_Metadata : "exports report"
    Students ||--o{ Notifications : "triggers alerts"
    Students ||--o{ Interventions : "receives remediation"
    Learning_Objectives ||--o{ Diagnostic_Logs : "evaluated in"

    Students {
        int student_id PK
        string first_name
        string last_name
        string class_section
        string roll_number
        string email
        string guardian_contact
        timestamp created_at
    }

    Learning_Objectives {
        int objective_id PK
        string topic_name
        string description
    }

    Attendance {
        int attendance_id PK
        int student_id FK
        date attendance_date
        string status "P or A"
    }

    Diagnostic_Logs {
        int log_id PK
        int student_id FK
        int objective_id FK
        float score_obtained
        float max_score
        date test_date
        string remarks
    }

    Weekly_Progress {
        int progress_id PK
        int student_id FK
        date week_start
        float score
    }

    Cyber_Audit {
        int audit_id PK
        int student_id FK
        float screen_time_hours
        float study_screen_time
        float recreational_screen_time
        float sleep_duration
        int digital_distraction_level
        int cyber_safety_awareness
        float wellness_score
        date audit_date
    }

    Interventions {
        int intervention_id PK
        int student_id FK
        string title
        string description
        string status "OPEN, IN_PROGRESS, RESOLVED, CANCELLED"
        date start_date
        date target_date
        date review_date
        float pre_risk_score
        float pre_academic_avg
        float pre_attendance_pct
        float pre_lhs_score
        float post_risk_score
        float post_academic_avg
        float post_attendance_pct
        float post_lhs_score
        float effectiveness_score
        string outcome_tier
    }

    Notifications {
        int notification_id PK
        int student_id FK
        string dedup_key
        string type
        string priority "HIGH, MEDIUM, INFO, SUCCESS"
        string title
        string message
        string status "OPEN, IN_PROGRESS, RESOLVED, DISMISSED"
        boolean is_read
        timestamp created_at
    }

    Users {
        int user_id PK
        string username
        string password_hash
        string full_name
        string role
    }
```

---

## 4. Key Mathematical Formulations

### 1. Learning Health Score (LHS)
Composite 0–100 index representing the holistic learning wellbeing:
$$\text{LHS} = (\text{Academic Average} \times 0.40) + (\text{Attendance Rate} \times 0.40) + (\text{Cyber-Wellness Score} \times 0.20)$$
*Dynamic Normalization: If wellness audit is pending, weights normalize to $50\% / 50\%$ across available components without false-zero penalties.*

### 2. Multi-Factor Explainable Risk Score
Transparent 0–100 risk formulation decomposing deficit contributions:
$$\text{Deficit}_{\text{Acad}} = \max(0, 100 - \text{Academic Average})$$
$$\text{Deficit}_{\text{Att}} = \max(0, 100 - \text{Attendance Rate})$$
$$\text{Deficit}_{\text{Well}} = \max(0, 100 - \text{Wellness Score})$$
$$\text{Deficit}_{\text{Slope}} = \text{Penalty derived from Simple Linear Regression slope } m$$

$$\text{Composite Risk} = \sum (\text{Deficit}_i \times w_i) \quad \text{where } \sum w_i = 1.0$$

### 3. Intervention Outcome Effectiveness Score
$$\Delta_{\text{Risk}} = \max(0, \text{Pre Risk} - \text{Post Risk})$$
$$\Delta_{\text{Acad}} = \max(0, \text{Post Acad} - \text{Pre Acad})$$
$$\Delta_{\text{Att}} = \max(0, \text{Post Att} - \text{Pre Att})$$
$$\Delta_{\text{LHS}} = \max(0, \text{Post LHS} - \text{Pre LHS})$$

$$\text{Effectiveness Score} = \min\Big(100.0, \max\big(0.0, (\Delta_{\text{Risk}}\times 0.35 + \Delta_{\text{Acad}}\times 0.30 + \Delta_{\text{Att}}\times 0.20 + \Delta_{\text{LHS}}\times 0.15)\times 2.5\big)\Big)$$
