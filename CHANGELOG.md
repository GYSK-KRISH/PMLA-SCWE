# Changelog

All notable changes to the **PMLA-SCWE** educational analytics platform are documented in this file.

---

## [Version 1.8.0] - 2026-08-16
### Added
- **Final Submission & Examination Package**: Complete CBSE Class XII project dossier including:
  - Comprehensive Academic Project Report (`documentation/FINAL_PROJECT_REPORT.md`).
  - 12-Slide Presentation Deck & Defense Script (`documentation/PRESENTATION_SLIDES_OUTLINE.md`).
  - System Architecture, Flowcharts & Entity-Relationship Diagrams (`documentation/SYSTEM_ARCHITECTURE_AND_ERD.md`).
  - Zero-to-Hero Installation, Setup & Live Demonstration Guide (`documentation/INSTALLATION_AND_DEMO_GUIDE.md`).
  - Comprehensive CBSE Viva Voce Preparation Guide (`documentation/VIVA_PREPARATION_GUIDE.md`).
- **Feature Freeze & Final Verification**: Verified all 63 automated tests passing with 100% OK across 8 test suites on dual backends (MySQL and SQLite).

---

## [Version 1.7.0] - 2026-08-16
### Added
- **Academic Intelligence Command Center (`core/command_center_service.py`)**: Unified institutional data aggregator powering the executive dashboard on Desktop and Web.
- **Smart Teacher Action Recommendations**: Grounded decision-support generating prioritized next steps (urgent alerts review, remedial interventions, pipeline monitoring).
- **Smart Notification & Deduplication Engine (`core/notification_service.py`)**: `dedup_key` indexing with 7-day cooldowns, severity escalation (`MEDIUM` $\rightarrow$ `HIGH`), and grounded positive learning milestone alerts ($\ge +2.0$ pts/wk growth slope).
- **Full Test Suite (`tests/test_command_center.py`)**: 63 automated tests passing with 100% OK across 8 test suites.


---

## [Version 1.6.0] - 2026-08-16
### Added
- **Closed-Loop Intervention Tracking (`core/intervention_service.py`)**: Automatic baseline snapshot capture (`pre_risk`, `pre_academic`, `pre_attendance`, `pre_lhs`) upon intervention creation.
- **Before vs. After Delta Analytics (`core/intervention_analytics.py`)**: Multi-dimensional recovery tracking ($\Delta_{\text{Risk}}$, $\Delta_{\text{Acad}}$, $\Delta_{\text{Att}}$, $\Delta_{\text{LHS}}$) and transparent 0–100 Effectiveness Scoring.
- **Standardized Outcome Tiers**: `Highly Effective` ($\ge 75$), `Effective` ($50-74$), `Moderate Improvement` ($25-49$), `Needs Review / Escalated` ($<25$).
- **PySide6 & Flask Intervention Consoles**: Desktop pipeline table with outcome evaluation dialogs and web `/interventions` console.

---

## [Version 1.5.0] - 2026-08-16
### Added
- **Professional Report Generation Engine (`core/report_service.py`)**: Centralized report builder for 6 report types (Individual Student, Class Performance, At-Risk, Attendance, Monthly Progress, Intervention Tracking).
- **Vector PDF Exporter**: High-resolution vector PDF generation via ReportLab with embedded charts, statistics grids, and safety disclaimers.
- **CSV Spreadsheet Export & Live Markdown Previews**: Instant tabular exports and live browser markdown preview dialogs.

---

## [Version 1.4.0] - 2026-08-16
### Added
- **AI Teacher Copilot (`core/ai/`)**: Modular package with 8 predefined grounded pedagogical actions (Explain Risk, Study Plan, Weak Topics, Intervention Plan, Class Summary, Compare Students, Parent Letter, Teacher Actions).
- **Multi-Provider Fallback Chain**: Google Gemini $\rightarrow$ OpenAI $\rightarrow$ Deterministic Offline Engine (`core/ai/offline_engine.py`).
- **Human-in-the-Loop Directives**: Non-autonomous decision advisory ensuring high-stakes actions require teacher review.

---

## [Version 1.3.0] - 2026-08-16
### Added
- **Explainable Predictive Analytics & Risk Engine (`core/risk_engine.py`, `core/explainability.py`)**: Transparent 0–100 multi-factor risk formula with explicit factor contributions (Academic, Attendance, Cyber Distraction, Trajectory Slope).
- **Early Warning Deduplication**: Cooldown mechanism preventing notification spam for the same student.

---

## [Version 1.2.0] - 2026-08-14
### Added
- **Student 360° Intelligence Profile (`core/student_profile_service.py`)**: Centralized aggregation service as the Single Source of Truth for student intelligence data.
- **Dynamic Learning Health Score (LHS) Normalization**: Safe normalization across academic (40%), attendance (40%), and wellness (20%) dimensions with data completeness tracking.
- **Chronological Activity Timeline**: Unified descending chronological feed of tests, attendance records, audits, and interventions.

---

## [Version 1.1.0] - 2026-08-14
### Added
- **Premium Modern UI Design System**: Unified design tokens (`#080A12` base), dark theme palette, standard reusable PySide6 widgets (`desktop/widgets/`), animated progress bars, responsive Flask glassmorphism CSS, and dark-themed matplotlib analytics.

---

## [Version 1.0.0] - 2026-08-10
### Added
- **Core Platform Architecture**: MySQL database schema with SQLite fallback (`pmla_scwe_fallback.db`), student CRUD, daily attendance registry, diagnostic assessment logging, and cyber-wellbeing audits.
