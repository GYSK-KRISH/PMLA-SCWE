# PMLA-SCWE: Live Demonstration & Step-by-Step Guide

This document provides a detailed step-by-step guide to demonstrate the **Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine (PMLA-SCWE)** during your practical assessment or project presentation.

---

## 🌟 Live Project Demonstration Flow

### Step 1: Automated Setup & Launch (One-Click)
Instead of running setup, dependency checks, database seeding, and application launching commands individually, you can do it all in a single command:
- **Action**: Run the automated launcher:
  - **Windows**: Double-click `setup_and_run.bat` (or run `./setup_and_run.bat` in terminal).
  - **macOS/Linux**: Run `./setup_and_run.sh` in terminal.
- **Under the Hood**:
  - Verifies Python installation.
  - Auto-creates the virtual environment `.venv` on the first run.
  - Verifies package requirements and installs them (either online, or offline from the `wheels` directory).
  - Runs the database schema verification and triggers the idempotent initialization.
  - Presents a timed menu to choose between the **Desktop CustomTkinter Client** and the **Flask Web Server** (defaulting to the Desktop client).

---

### Step 2: Populating Clean Mock Data (Optional)
If you want to demonstrate predictive regression trends and dashboards with a pre-seeded set of 100 sample student records:
- **Action**: Run the seeder with the reset flag:
  ```powershell
  python seed_database.py --reset
  ```
- **Under the Hood**:
  - Deletes any existing data and resets AUTO_INCREMENT ID counters.
  - Generates exactly 100 mock students.
  - Seeds 10 days of attendance logs per student.
  - Logs 4 weeks of progress test scores per student (declining, improving, or stable linear trends).
  - Adds cyber wellness audits, learning health records, and initial notifications.


---

### Step 4: Login and Basic Student Management
Demonstrate authentication and CRUD operations.
1. **Login**: Enter the username `admin` and password `admin123`.
2. **Add Student**: Navigate to the student register panel and enter details:
   - **First Name**: Aria
   - **Last Name**: Stark
   - **Class/Section**: 12-A
   - **DOB**: 2008-05-15
   - **Gender**: F
   - **Email**: aria@winterfell.com
   - **Phone**: 9999000101
3. **Save**: The student is added, auto-assigning student ID 101.

---

### Step 5: Mark Attendance & Add Assessments
1. **Attendance**: Mark Aria as present (`P`) for today's date.
2. **Assessment**: Add a diagnostic score for student 101:
   - **Score**: 95
   - **Max Score**: 100
   - **Topic**: Pandas Basics (from the objective list)

---

### Step 6: Perform Wellness Audit
Log digital habits to compute safety ratings:
- **Action**: Add cyber audit for student 101:
   - **Study Screen Time**: 2.5 hours
   - **Recreational Screen Time**: 1.5 hours
   - **Sleep Duration**: 8.0 hours
   - **Digital Distraction Level (1-5)**: 1
   - **Cyber Safety Awareness Rating (1-5)**: 5
- **Under the Hood**: Calculates a wellness rating from sleep hours, safety settings, and screen time balance.

---

### Step 7: View Predictive Analytics & Visual Reports
Analyze student performance trend forecasting:
1. Navigate to **Predictive Analytics & Insights** and select Student ID `101`.
2. **Mathematical Analysis**:
   - Compiles the composite **Learning Health Score (LHS)**.
   - Computes **Simple Linear Regression** over weekly scores to find the slope $m$ and intercept $c$, predicting next week's performance.
   - Categorizes risk level (Low, Medium, or High).
3. **Save Reports**: Generate and save diagnostic charts (PNG) and structured text/CSV reports inside the `reports/` folder.

---

### Step 8: Interact with the AI Assistant
Query the explainable analytics assistant:
1. Navigate to the **AI Assistant** tab.
2. Type or speak a voice question: *"Explain the wellness status of Student 1"* or *"Why is Student 6 flagged as high risk?"*
3. The assistant retrieves student metrics, sends them to the configured AI API (with local rule fallback), and prints the suggestion while reading it out loud.

---

## 💻 Technical Support Procedures

### Running Offline (Evaluator Machine)
If the examiner's machine has no Internet and no MySQL server:
1. Copy the project folder containing `pmla_scwe_fallback.db` via a USB drive.
2. Open terminal in the directory and run `python main.py`. The app will identify that MySQL is down and run directly on SQLite without crashing.

### Offline Package Setup
If the target computer has no internet connection:
1. **On a machine with internet**: Run `download_wheels.bat` (Windows) or `download_wheels.sh` (macOS/Linux) to download all required packages into the `wheels` directory.
2. **Copy the wheels folder** (which now contains all library files) to the offline machine inside your project folder.
3. **On the offline machine**: Simply run `setup_and_run.bat` or `setup_and_run.sh`. The script will detect the `wheels` folder and perform the installation automatically without requiring internet.

