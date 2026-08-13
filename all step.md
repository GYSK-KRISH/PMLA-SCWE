# PMLA-SCWE: Live Demonstration & Step-by-Step Guide

This document provides a detailed step-by-step guide to demonstrate the **Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine (PMLA-SCWE)** during your practical assessment or project presentation.

---

## 🌟 Live Project Demonstration Flow

### Step 1: Pre-populate the Database (Seeding Mock Data)
Before starting the interface, populate the database with realistic mock data to demonstrate regression trends and dashboards.
- **Action**: Run this command in your VS Code terminal:
  ```powershell
  python seed_data.py
  ```
- **Under the Hood**:
  - The script executes the schema script to reset and construct all 12 tables.
  - Generates exactly 100 students.
  - Generates 10 days of attendance logs per student (simulating realistic present/absent rates).
  - Logs 4 weeks of progress test scores per student (creating declining, improving, or stable linear trends).
  - Adds cyber wellness audits, learning health records, and initial system notifications.
- **Output**: Logs the initialization status and outputs a clear summary of seeded table counts.

---

### Step 2: Run setup diagnostics
Verify that all dependencies and databases are correctly connected.
- **Action**: Run the diagnostics utility:
  ```powershell
  python diagnose_setup.py
  ```
- **Under the Hood**:
  - Validates python and virtual environment activation.
  - Checks if required libraries are installed.
  - Tests local MySQL connection on port 3306 and the SQLite fallback file.
  - Checks if all 12 tables exist.

---

### Step 3: Launch the Application
Start either the graphical desktop application or the Flask web console.
- **Action**: 
  - To launch the **Desktop GUI**:
    ```powershell
    python main.py
    ```
  - To launch the **Flask Web Server**:
    ```powershell
    python main.py --web
    ```
- **Under the Hood**:
  - If a connection to local MySQL on port 3306 fails, the app prints a status notification and launches in fallback mode using the local SQLite file `pmla_scwe_fallback.db`.
  - Ensures a default administrator exists (`admin` / `admin123`).

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
If the target computer has no Internet to run pip install:
1. **On a machine with internet**:
   ```powershell
   pip download -r requirements.txt -d ./wheels
   ```
2. **Copy the wheels folder** to the offline machine.
3. **On the offline machine**:
   ```powershell
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```
