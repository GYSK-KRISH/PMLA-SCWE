# PMLA-SCWE: CBSE Class XII Final Viva Voce & Defense Guide

## 1. Project Identity & Executive Pitch
> **Question: What is PMLA-SCWE, and why is it not just another school management system?**

**Answer:**
PMLA-SCWE (**Predictive Machine Learning & Learning Analytics for Student Cyber-Wellbeing Engine**) is an **explainable educational intelligence and teacher decision-support platform**.

While typical school projects are purely CRUD (Create, Read, Update, Delete) forms, PMLA-SCWE implements a **closed-loop educational intelligence lifecycle**:
$$\textbf{Detect (v1.3)} \longrightarrow \textbf{Explain (v1.3)} \longrightarrow \textbf{Recommend (v1.4)} \longrightarrow \textbf{Review \& Intervene (v1.6)} \longrightarrow \textbf{Monitor (v1.6)} \longrightarrow \textbf{Evaluate Outcomes (v1.6)} \longrightarrow \textbf{Command Center (v1.7)}$$

---

## 2. Version Evolution Breakdown (v1.1 – v1.7)

| Version | Milestone Name | Key Architectural Innovation |
| :--- | :--- | :--- |
| **v1.1** | **Premium Modern UI System** | Centralized design tokens, PySide6 desktop dark palette, Flask glassmorphism, animated progress bars, responsive web layout. |
| **v1.2** | **Student 360° Intelligence Profile** | Centralized aggregation service as the Single Source of Truth; dynamic Learning Health Score (LHS) normalization and chronological timeline. |
| **v1.3** | **Explainable Risk Engine** | Transparent 0–100 multi-factor risk formula with explicit factor contribution evidence, removing "black-box" predictions. |
| **v1.4** | **AI Teacher Copilot** | 8 grounded pedagogical actions; resilient provider failover (Google Gemini $\rightarrow$ OpenAI) with offline deterministic engine fallback. |
| **v1.5** | **Professional Report Generation** | Centralized report engine for 6 report types, ReportLab vector PDF generation with embedded charts, and CSV spreadsheet exports. |
| **v1.6** | **Intervention Outcome Intelligence** | Automatic baseline snapshots (`pre_*`), Before vs. After delta analysis ($\Delta_{\text{Risk}}, \Delta_{\text{Acad}}, \Delta_{\text{Att}}, \Delta_{\text{LHS}}$), and 0–100 effectiveness scoring. |
| **v1.7** | **Academic Intelligence Command Center** | Smart notification engine with `dedup_key` cooldowns, severity escalation, positive milestone detection, and executive teacher command center. |

---

## 3. Key Technical Viva Questions & Exemplary Answers

### Architecture & Database
**Q1: How does your project share logic between Desktop (PySide6) and Web (Flask)?**
> **A:** We use a **Shared-Core Architecture** located in the `core/` package. The desktop GUI (`desktop/`) and Flask web controllers (`web/`) contain **presentation logic only**. Neither interface performs calculations or direct raw database queries; both call centralized services such as `core.student_profile_service`, `core.command_center_service`, and `core.intervention_service`.

**Q2: How does the system handle database connectivity if MySQL is unavailable?**
> **A:** The system implements an automatic **SQLite Fallback Engine** (`core/database.py`). If the MySQL connection fails or is unconfigured, the application gracefully switches to `pmla_scwe_fallback.db` without crashing, while notifying the teacher via a database warning banner.

**Q3: How are passwords stored securely?**
> **A:** Passwords are never stored in plaintext. We implement **PBKDF2-HMAC-SHA256** key derivation with individual 16-byte random salts and 100,000 iterations in `core/auth_service.py`.

---

### Machine Learning, Analytics & Explainability
**Q4: Why did you choose an Explainable Risk Engine over a black-box Deep Learning model?**
> **A:** In educational decision-support, high-stakes decisions should never be based on opaque probabilities. An opaque model might state "High Risk: 85%" without explanation. Our **Explainable Risk Engine** decomposes the score into weighted mathematical factors:
> - **Academic Deficit (35%)**: $\max(0, 100 - \text{average\_score})$
> - **Attendance Deficit (30%)**: $\max(0, 100 - \text{attendance\_percentage})$
> - **Cyber Distraction / Wellness Deficit (20%)**: $\max(0, 100 - \text{wellness\_score})$
> - **Declining Trajectory Deficit (15%)**: Slope of weekly assessment progress
> Each alert provides human-readable evidence (e.g. *"Attendance is 64% — 11% below CBSE 75% threshold"*).

**Q5: What is the Learning Health Score (LHS)?**
> **A:** LHS is a composite 0–100 index representing the holistic health of a student:
> $$\text{LHS} = (\text{Academic Average} \times 0.40) + (\text{Attendance Rate} \times 0.40) + (\text{Cyber-Wellness Score} \times 0.20)$$
> If a student has only enrolled and lacks wellness audits, the weights dynamically re-normalize ($50\% / 50\%$) rather than distorting the score with false zeros.

---

### Decision Support, AI & Interventions
**Q6: What happens if the AI API keys are missing or the internet is disconnected?**
> **A:** The system implements a 3-tier fallback chain:
> 1. **Primary**: Google Gemini API
> 2. **Secondary**: OpenAI API
> 3. **Offline Fallback**: Deterministic Pedagogical Rule Engine in `core/ai/offline_engine.py` that generates grounded study plans, weak topic breakdowns, and intervention drafts entirely offline.

**Q7: How do you measure whether an intervention was successful?**
> **A:** When a teacher creates an intervention in v1.6, the system snapshots baseline metrics (`pre_risk`, `pre_academic`, `pre_attendance`, `pre_lhs`). Upon review, post-metrics are compared to calculate **Before vs. After Deltas**:
> $$\text{Effectiveness Score} = \min\Big(100.0, \max\big(0.0, (\Delta_{\text{Risk}}\times 0.35 + \Delta_{\text{Acad}}\times 0.30 + \Delta_{\text{Att}}\times 0.20 + \Delta_{\text{LHS}}\times 0.15)\times 2.5\big)\Big)$$
> - $\ge 75$: `Highly Effective`
> - $50 - 74$: `Effective`
> - $25 - 49$: `Moderate Improvement`
> - $< 25$: `Needs Review / Escalated`

**Q8: How do you prevent notification spam in Version 1.7?**
> **A:** Alerts are keyed with a unique `dedup_key` (e.g. `att_crit_{student_id}`). If an alert already exists within a 7-day cooldown window, duplicate creation is skipped. However, if the student's risk **escalates** (e.g. `MEDIUM` $\rightarrow$ `HIGH`), the existing alert is upgraded in-place and re-flagged as unread without cluttering the database.

---

## 4. Test Suite Summary

All **63 unit and integration tests** pass with 100% OK across 8 comprehensive test suites:
- `tests/test_command_center.py`
- `tests/test_notifications.py`
- `tests/test_intervention_service.py`
- `tests/test_reports.py`
- `tests/test_copilot.py`
- `tests/test_risk_engine.py`
- `tests/test_profile_service.py`
- `tests/test_core.py`
