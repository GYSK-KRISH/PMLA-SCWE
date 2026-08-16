# PMLA-SCWE: Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine
## Comprehensive Academic Project Report

**CBSE Class XII Informatics Practices / Computer Science Project**  
**Academic Year:** 2026–2027  
**Platform Version:** Version 1.8 (Submission Edition)

---

## 1. Certificate & Declaration

### Certificate of Authenticity
This is to certify that the project entitled **"PMLA-SCWE: Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine"** is a bonafide work carried out by the student under the guidance and supervision of the Department of Informatics Practices / Computer Science in partial fulfillment of the requirements for the **All India Senior School Certificate Examination (AISSCE) — CBSE Class XII**.

**Internal Examiner Signature:** ____________________  
**External Examiner Signature:** ____________________  
**Principal Signature & Seal:** ____________________  

---

### Student Declaration
I hereby declare that this project report titled **"PMLA-SCWE"** has been developed independently by me. The algorithms, data structures, shared-core services, relational database schemas, and dual user interfaces have been constructed in accordance with the CBSE Class XII syllabus guidelines.

---

## 2. Executive Summary & Aim

### Project Aim
To design, engineer, and deploy an **explainable educational analytics and teacher decision-support platform** that bridges the gap between raw student management records (grades, daily attendance, cyber-habits) and actionable educational remediation.

### The Problem with Traditional School Systems
1. **Purely Static & CRUD**: Most traditional school software acts solely as an electronic ledger. They record absent days and test marks but provide zero predictive foresight.
2. **Opaque "Black-Box" Alerts**: Modern AI systems often label students as "High Risk: 85%" without explaining the contributing deficits, confusing teachers.
3. **Open-Loop Disconnect**: After an educator identifies a student in difficulty, traditional software provides no mechanism to log pedagogical interventions, snapshot baselines, or evaluate outcome recovery over time.

### PMLA-SCWE Solution
PMLA-SCWE establishes a **Closed-Loop Educational Intelligence Cycle**:
$$\textbf{Collect Data} \longrightarrow \textbf{Synthesize 360° Profile} \longrightarrow \textbf{Explainable Risk Engine} \longrightarrow \textbf{Smart Alerts} \longrightarrow \textbf{AI Copilot Strategy} \longrightarrow \textbf{Teacher-Approved Intervention} \longrightarrow \textbf{Outcome Evaluation} \longrightarrow \textbf{Executive Command Center}$$

---

## 3. Hardware & Software Requirements

### Hardware Requirements
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Hard Disk Storage**: 500 MB free space
- **Display Resolution**: $1280 \times 720$ minimum ($1920 \times 1080$ recommended)

### Software Requirements
- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **Runtime Environment**: Python 3.10 to 3.13
- **Primary Database**: MySQL Server 8.0+ (via `mysql-connector-python`)
- **Fallback Database**: SQLite3 (Embedded zero-configuration fallback)
- **Desktop Presentation**: PySide6 (Qt 6 for Python)
- **Web Presentation**: Flask 3.0+ with Jinja2 Templating
- **Analytics & PDF Engine**: Matplotlib, ReportLab, NumPy

---

## 4. System Architecture & Core Modules

PMLA-SCWE employs a **Shared-Core Service-Oriented Architecture (SOA)** where the core business logic resides exclusively in the `core/` package, serving both the PySide6 desktop GUI and Flask web interface identically.

```text
                                 PMLA-SCWE PLATFORM
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[Desktop Application: PySide6]                                 [Web Console: Flask]
  • Command Center Dashboard                                     • Executive Command Hub
  • Student 360° Interactive Modal                               • Responsive Profile Views
  • Intervention Tracking Console                                • /interventions Center
  • ReportLab PDF Exporter GUI                                   • /reports Hub & Previews
  • AI Copilot Chat Interface                                    • /copilot Pedagogical Hub
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         │
                                         ▼
                            SHARED CORE SERVICES (core/)
  ├── student_profile_service.py     -> Single Source of Truth for Student 360°
  ├── risk_engine.py & explainability -> Transparent 0–100 Multi-Factor Risk
  ├── command_center_service.py      -> Executive Stratification & Smart Actions
  ├── notification_service.py        -> Deduplication, Cooldown & Escalation
  ├── intervention_service.py        -> Baselines & Lifecycle Tracking
  ├── intervention_analytics.py      -> Before vs. After Deltas & 0–100 Score
  ├── report_service.py              -> Vector PDF & CSV Report Engine
  ├── ai/                            -> Gemini / OpenAI / Offline Failover
  ├── auth_service.py                -> PBKDF2-HMAC-SHA256 Security
  └── database.py                    -> MySQL Engine with Automatic SQLite Fallback
                                         │
                                         ▼
                             RELATIONAL DATA LAYER
                               (12 Database Tables)
```

---

## 5. Mathematical Formulations & Analytical Logic

### 1. Learning Health Score (LHS)
The composite 0–100 health index assesses a student's holistic well-being:
$$\text{LHS} = (\text{Academic Average} \times 0.40) + (\text{Attendance Rate} \times 0.40) + (\text{Cyber-Wellness Score} \times 0.20)$$

### 2. Simple Linear Regression Progress Trajectory
To forecast next week's score from historical weekly progress points $(x_i, y_i)$:
$$m = \frac{n\sum (x_i y_i) - \sum x_i \sum y_i}{n\sum (x_i^2) - (\sum x_i)^2}$$
$$c = \frac{\sum y_i - m\sum x_i}{n}$$
$$\hat{y}_{\text{next}} = m(n+1) + c$$

### 3. Explainable Risk Score Formula
Rather than a probabilistic black box, the risk score is a deterministic linear combination of domain-specific deficits:
$$\text{Deficit}_{\text{Academic}} = \max(0, 100 - \text{Academic Average})$$
$$\text{Deficit}_{\text{Attendance}} = \max(0, 100 - \text{Attendance Rate})$$
$$\text{Deficit}_{\text{Cyber}} = \max(0, 100 - \text{Wellness Score})$$
$$\text{Deficit}_{\text{Trajectory}} = \text{Penalty for downward slope } (m < 0)$$

$$\text{Risk Score} = (0.35 \cdot \text{Def}_{\text{Acad}}) + (0.30 \cdot \text{Def}_{\text{Att}}) + (0.20 \cdot \text{Def}_{\text{Cyber}}) + (0.15 \cdot \text{Def}_{\text{Traj}})$$

### 4. Intervention Outcome Effectiveness Formula
Measures multi-dimensional recovery by comparing post-intervention metrics with the baseline snapshot:
$$\Delta_{\text{Risk}} = \max(0, \text{Pre Risk} - \text{Post Risk})$$
$$\Delta_{\text{Acad}} = \max(0, \text{Post Acad} - \text{Pre Acad})$$
$$\Delta_{\text{Att}} = \max(0, \text{Post Att} - \text{Pre Att})$$
$$\Delta_{\text{LHS}} = \max(0, \text{Post LHS} - \text{Pre LHS})$$

$$\text{Effectiveness Score} = \min\Big(100.0, \max\big(0.0, (0.35\Delta_{\text{Risk}} + 0.30\Delta_{\text{Acad}} + 0.20\Delta_{\text{Att}} + 0.15\Delta_{\text{LHS}})\times 2.5\big)\Big)$$

---

## 6. Software Quality Assurance & Testing

The platform is backed by an automated test suite of **63 tests across 8 test suites** executed via Python's standard `unittest` framework:

| Test Suite | Purpose | Test Cases | Status |
| :--- | :--- | :---: | :---: |
| `tests/test_command_center.py` | Executive aggregation, priority ranking & smart actions | 4 | ✅ Passed |
| `tests/test_notifications.py` | Alert deduplication, escalation, positive milestones | 7 | ✅ Passed |
| `tests/test_intervention_service.py` | Baseline snapshots, status lifecycle & delta scoring | 7 | ✅ Passed |
| `tests/test_reports.py` | Vector PDF generation, CSV exports & live previews | 8 | ✅ Passed |
| `tests/test_copilot.py` | Grounded actions, provider failover & offline engine | 14 | ✅ Passed |
| `tests/test_risk_engine.py` | 0-100 risk math, explainability & boundary conditions | 8 | ✅ Passed |
| `tests/test_profile_service.py` | Single Source of Truth, LHS normalization & timeline | 8 | ✅ Passed |
| `tests/test_core.py` | Core CRUD, attendance, PBKDF2 auth, token parity | 7 | ✅ Passed |
| **Total Automated Tests** | **Comprehensive System Verification** | **63** | **100% OK** |

---

## 7. Conclusion & Future Scope

### Conclusion
PMLA-SCWE successfully modernizes school educational management by uniting relational databases, transparent machine learning algorithms, non-autonomous AI pedagogical assistants, closed-loop intervention tracking, and executive command centers into a unified Python architecture.

### Future Scope
1. **LMS Integration**: Direct synchronization via LTI (Learning Tools Interoperability) with Google Classroom and Moodle.
2. **Automated SMS / WhatsApp Gateway**: Sending teacher-approved parent letters directly to verified guardian phone numbers.
3. **Biometric Attendance Hardware**: Real-time RFID / facial recognition integration at classroom entrance doors.

---

## 8. Bibliography & References

1. **CBSE Informatics Practices Class XII Syllabus**, Central Board of Secondary Education, New Delhi.
2. **Python Software Foundation**, Python 3.12 Documentation, https://docs.python.org/3/
3. **PySide6 / Qt for Python Documentation**, The Qt Company, https://doc.qt.io/qtforpython/
4. **Flask Web Development**, Miguel Grinberg, O'Reilly Media.
5. **ReportLab PDF Generation Library Documentation**, ReportLab Europe Ltd.
6. **National Education Policy (NEP) 2020 Guidelines on Digital Wellbeing and Holistic Progress Cards (HPC)**, Ministry of Education, Govt. of India.
