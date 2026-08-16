# PMLA-SCWE: Installation, Setup & Live Demonstration Guide

**Version 1.8 — Final Release & Submission Edition**

---

## 1. Prerequisites & Environment Setup

### System Requirements
- Python 3.10, 3.11, 3.12, or 3.13 installed and added to your system `PATH`.
- MySQL Server (optional; if offline or uninstalled, the built-in SQLite auto-fallback engages automatically).

### Step-by-Step Installation

1. **Clone or Open the Project Directory**:
   ```powershell
   cd d:\PMLA-SCWE
   ```

2. **Create and Activate a Virtual Environment**:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Project Dependencies**:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify Environment Diagnostics**:
   ```powershell
   python diagnose_setup.py
   ```

---

## 2. Database Initialization & Seeding

1. **Seed Institutional Dataset**:
   ```powershell
   python seed_data.py
   ```
   *This command creates all 12 tables, resets auto-increment IDs, generates 100 students, 1,000 attendance entries, 100 diagnostic logs, 400 weekly progress points, 100 cyber audits, and sample notifications & interventions.*

---

## 3. Launching Dual Frontends

### Option A: PySide6 Desktop Application (Primary Examiner Demo)
```powershell
python main.py
```
- **Login Credentials**: Username `admin` | Password `admin123`
- Features dark theme (`#080A12` base), interactive progress bars, student 360° modals, intervention pipeline, and live PDF exports.

### Option B: Flask Web Console (Browser Experience)
```powershell
python main.py --web
```
- Open your browser to: `http://127.0.0.1:5000`
- **Login Credentials**: Username `admin` | Password `admin123`
- Features responsive glassmorphism, AJAX notification updates, live markdown previews, and interactive charts.

---

## 4. Running the Complete Automated Test Suite

To verify system integrity across all 8 test suites:
```powershell
python -m unittest discover tests/ -v
```

Expected output:
```text
Ran 63 tests in ~75s — OK
```

---

## 5. 5-Minute Live Examiner Demonstration Script

Follow this script to demonstrate all major platform features during practical defense:

| Step | Action | What to Explain to the Examiner |
| :---: | :--- | :--- |
| **1** | **Dashboard & Command Center** | Point to the **Smart Recommended Teacher Actions** banner. Show how the system prioritizes high-risk students and flags attendance drops below CBSE targets. |
| **2** | **Student 360° Intelligence Profile** | Click on any student (e.g. `Rohan Gupta`) ➔ Click `👤 Profile`. Point out the **Learning Health Score (LHS)**, the 4-component breakdown, and the chronological activity timeline. |
| **3** | **Explainable Risk Engine** | Point out the Risk Score (e.g. `82/100 - HIGH RISK`) and read the **Evidence Bullets** aloud (*"Attendance is 62% — 13% below target"*). Highlight that it is explainable and deterministic. |
| **4** | **AI Teacher Copilot** | Click `🤖 Ask Copilot` ➔ Select `Explain Student Risk` or `Create Study Plan (14 Days)`. Point out the structured sections and the safety disclaimer (*"Human-in-the-loop review required"*). Mention the offline fallback engine. |
| **5** | **Intervention Tracking & Outcomes** | Navigate to `Interventions` tab. Show how baseline metrics were snapshotted. Click `Evaluate Outcome` on a completed case to show Before vs. After Deltas and the 0–100 Effectiveness Score. |
| **6** | **Professional Vector PDF Report** | Navigate to `Reports` tab ➔ Select `Individual Student Intelligence Report` ➔ Click `Generate PDF`. Open the resulting PDF to showcase high-res vector charts, LHS donuts, and risk tables. |
| **7** | **Smart Notifications Hub** | Click the notification bell. Point out `dedup_key` deduplication, severity escalation chips, and positive milestone celebrations for improving students. |
