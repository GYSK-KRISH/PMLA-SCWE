# PMLA-SCWE: Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine

**Version 1.8 — Final Release & Submission Edition**

PMLA-SCWE is an **explainable, AI-assisted educational analytics and teacher decision-support platform** built in Python with dual presentation interfaces (**PySide6 Desktop Application** and **Flask Web Console**). It implements a closed-loop intelligence cycle:
$$\textbf{Detect} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Recommend} \longrightarrow \textbf{Teacher Review} \longrightarrow \textbf{Intervene} \longrightarrow \textbf{Monitor} \longrightarrow \textbf{Evaluate Outcomes} \longrightarrow \textbf{Command Center}$$

### 📚 Official Submission Documentation Dossier
- 📄 [Comprehensive Academic Project Report](file:///d:/PMLA-SCWE/documentation/FINAL_PROJECT_REPORT.md)
- 📊 [12-Slide Presentation Deck & Defense Script](file:///d:/PMLA-SCWE/documentation/PRESENTATION_SLIDES_OUTLINE.md)
- 📐 [System Architecture, Flowcharts & ER Diagrams](file:///d:/PMLA-SCWE/documentation/SYSTEM_ARCHITECTURE_AND_ERD.md)
- 🛠️ [Installation, Setup & Live Demo Guide](file:///d:/PMLA-SCWE/documentation/INSTALLATION_AND_DEMO_GUIDE.md)
- 🎓 [CBSE Viva Voce Preparation Guide](file:///d:/PMLA-SCWE/documentation/VIVA_PREPARATION_GUIDE.md)


---

## 🚀 Quick Start Guide

### 1. Configure Python Environment & Dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify System & Database Connectivity
```powershell
python diagnose_setup.py
```

### 3. Seed Mock Institutional Dataset
```powershell
python seed_data.py
```

### 4. Launch the Applications
* **PySide6 Desktop Application**:
  ```powershell
  python main.py
  ```
* **Flask Web Console**:
  ```powershell
  python main.py --web
  ```
  *Default Administrator Credentials: `admin` / `admin123`*

### 5. Run Automated Test Suite
```powershell
python -m unittest discover tests/ -v
```
*(63/63 tests passing with 100% OK across 8 test suites)*

---

## 📋 Comprehensive System Capabilities (v1.0 – v1.7)

### 1. Student 360° Intelligence Profile (`core/student_profile_service.py`)
- Centralized Single Source of Truth aggregating academic performance, daily attendance records, weekly score trajectory, cyber-wellness indices, and chronological event timelines.
- **Dynamic Learning Health Score (LHS)**:
  $$\text{LHS} = (\text{Academic Average} \times 0.40) + (\text{Attendance Rate} \times 0.40) + (\text{Cyber-Wellness Score} \times 0.20)$$

### 2. Explainable Learning Risk Engine (`core/risk_engine.py`)
- Transparent **0–100 Multi-Factor Risk Score** with explicit factor contribution evidence:
  - Academic Deficit ($35\%$)
  - Attendance Deficit ($30\%$)
  - Cyber Distraction & Wellness Deficit ($20\%$)
  - Weekly Trajectory Slope ($15\%$)

### 3. AI Teacher Copilot & Pedagogical Assistant (`core/ai/`)
- 8 grounded decision-support actions: Explain Risk, Create Study Plan, Identify Weak Topics, Generate Intervention Plan, Summarize Class Performance, Compare Two Students, Draft Parent Letter, and Suggest Teacher Actions.
- Resilient multi-provider failover: Google Gemini $\rightarrow$ OpenAI $\rightarrow$ Deterministic Offline Engine (`core/ai/offline_engine.py`).
- Human-in-the-loop safety: non-autonomous design ensuring all high-stakes actions require teacher review.

### 4. Professional Report Generation Engine (`core/report_service.py`)
- Centralized exporter for 6 standardized report types.
- High-resolution vector PDF generation via ReportLab with embedded charts, statistics tables, and educational safety notices.
- Clean CSV spreadsheet export and live Markdown preview dialogs.

### 5. Closed-Loop Intervention Tracking (`core/intervention_service.py`)
- Automated baseline snapshots (`pre_*`) captured at creation time.
- **Before vs. After Delta Analytics**: $\Delta_{\text{Risk}}$, $\Delta_{\text{Acad}}$, $\Delta_{\text{Att}}$, $\Delta_{\text{LHS}}$.
- Transparent **0–100 Intervention Effectiveness Scoring**:
  $$\text{Effectiveness Score} = \min\Big(100.0, \max\big(0.0, (\Delta_{\text{Risk}}\times 0.35 + \Delta_{\text{Acad}}\times 0.30 + \Delta_{\text{Att}}\times 0.20 + \Delta_{\text{LHS}}\times 0.15)\times 2.5\big)\Big)$$
- Standardized outcome tiers: `Highly Effective` ($\ge 75$), `Effective` ($50-74$), `Moderate Improvement` ($25-49$), `Needs Review / Escalated` ($<25$).

### 6. Smart Notification & Decision-Support Engine (`core/notification_service.py`)
- `dedup_key` indexing with 7-day cooldown windows preventing alert floods.
- In-place severity escalation (`MEDIUM` $\rightarrow$ `HIGH`) without database clutter.
- Grounded positive learning milestone detection for rapid growth trajectories.

### 7. Academic Intelligence Command Center (`core/command_center_service.py`)
- Unified executive overview for Desktop (`desktop/dashboard.py`) and Web (`web/templates/dashboard.html`).
- Automated Smart Recommended Teacher Actions banner.

---

## 📂 Project Architecture

```text
PMLA-SCWE/
├── main.py                          # Dual-interface CLI launch router
├── seed_data.py                     # Mock institutional database seeder
├── diagnose_setup.py                # 5-stage setup verification tool
├── requirements.txt                 # Project dependencies
├── schema.sql                       # Master database schema
│
├── core/                            # Shared Business Logic & Single Source of Truth
│   ├── database.py                  # MySQL / SQLite query engine with auto-fallback
│   ├── auth_service.py              # PBKDF2-HMAC-SHA256 authentication
│   ├── student_service.py           # Student record transactions
│   ├── attendance_service.py        # Attendance registry and analytics
│   ├── assessment_service.py        # Diagnostic assessment scoring
│   ├── wellness_service.py          # Cyber-wellness audit computations
│   ├── analytics.py                 # Linear regression & trend analytics
│   ├── risk_engine.py               # Explainable 0-100 risk scoring
│   ├── explainability.py            # Natural language evidence synthesis
│   ├── student_profile_service.py   # Student 360° Profile aggregator
│   ├── report_service.py            # Centralized vector PDF & CSV report engine
│   ├── intervention_service.py      # Baseline snapshots & intervention CRUD
│   ├── intervention_analytics.py    # Before vs After delta & effectiveness math
│   ├── notification_service.py      # Smart deduplication & alert engine
│   ├── command_center_service.py    # Executive command center aggregator
│   └── ai/                          # AI Teacher Copilot package
│       ├── provider_manager.py      # Gemini / OpenAI / Offline router
│       ├── prompt_templates.py      # Grounded pedagogical prompt templates
│       ├── context_builder.py       # Grounded student context synthesis
│       ├── response_parser.py       # Structured JSON & Markdown parser
│       └── offline_engine.py        # Deterministic offline rule engine
│
├── desktop/                         # PySide6 Desktop GUI (Premium Dark UI)
│   ├── app.py                       # Application controller & window stack
│   ├── theme.py                     # Centralized design tokens & stylesheet
│   ├── dashboard.py                 # Academic Intelligence Command Center
│   ├── student_profile_dialog.py    # Interactive Student 360° modal
│   ├── interventions_view.py        # Intervention pipeline & delta evaluation
│   ├── reports_view.py              # PDF/CSV report generation center
│   ├── ai_assistant_view.py         # AI Teacher Copilot chat view
│   └── widgets/                     # Reusable PySide6 UI component library
│
├── web/                             # Flask Web Console
│   ├── app.py                       # Flask server factory & blueprint registration
│   ├── routes/                      # Modular endpoint controllers
│   ├── static/css/style.css         # Dark glassmorphism stylesheet
│   └── templates/                   # Jinja2 presentation templates
│
├── tests/                           # Comprehensive Unit & Integration Test Suites
│   ├── test_core.py                 # Core CRUD, auth, wellness, token parity
│   ├── test_profile_service.py      # Student 360° Single Source of Truth
│   ├── test_risk_engine.py          # Explainable 0-100 risk calculations
│   ├── test_copilot.py              # AI actions & offline fallback failover
│   ├── test_reports.py              # Vector PDF and CSV generation
│   ├── test_intervention_service.py # Intervention baselines, deltas, effectiveness
│   ├── test_notifications.py        # Deduplication, escalation, milestones
│   └── test_command_center.py       # Executive aggregation & smart actions
│
└── documentation/                   # CBSE Project Defense & Guides
    └── VIVA_PREPARATION_GUIDE.md    # Complete viva voce defense questions & answers
```

---

## 🔒 Security & Data Integrity
- Passwords are encrypted using **PBKDF2-HMAC-SHA256** with unique salts and 100,000 hash iterations.
- Non-autonomous AI guardrails enforce teacher confirmation for all intervention recommendations.
- Automatic database migrations ensure non-destructive schema evolution for MySQL and SQLite.
