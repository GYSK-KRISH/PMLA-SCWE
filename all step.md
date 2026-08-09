# PMLA-SCWE: Deep Step-by-Step Live Demonstration & Installation Guide

This document provides a highly detailed walkthrough of the entire project. Use this guide during your live project presentation to explain what the application does, what inputs to type, and exactly what happens inside the database and code at each step.

---

## Part A: Live Project Demonstration (Step-by-Step)

### Step 1: Pre-populate 100 Sample Records (Database Seeding)
Before running the main program, you should load mock data so that your analytics reports and graphs look full and realistic.
- **Action**: Run this command in your VS Code terminal:
  ```powershell
  python -m PMLA_SCWE.seed_data
  ```
- **Under the Hood**:
  - The script opens `schema.sql` and recreates all database tables cleanly.
  - It clears out any old records and resets the ID counter to `1`.
  - It inserts exactly `100` students, generating sequential student IDs from `1` to `100`.
  - It logs **10 days of attendance** per student (allowing actual percentages like 80% or 60% to be calculated).
  - It logs **4 weeks of progress test scores** per student (creating clear improving, declining, or stable trends for regression plotting).
  - It registers diagnostic logs and cyber-wellness habits matching each profile.
- **Expected Output**:
  `{'students': 100, 'learning_objectives': 10, 'admin_logins': 1, 'diagnostic_logs': 100, 'attendance': 1000, 'cyber_audit': 100, 'weekly_progress': 400, 'achievements': 25, 'activity_log': 100, 'reports_metadata': 100}`

---

### Step 2: Start the Main Program & Display Menu
- **Action**: Run the main module:
  ```powershell
  python -m PMLA_SCWE.main
  ```
- **Under the Hood**:
  - The code imports `database.py` and tries to open a connection to MySQL Server on port 3306.
  - If MySQL is down, it catches the error and initializes a local SQLite file `pmla_scwe_fallback.db` instead, guaranteeing the app never crashes.
  - It prints the ASCII title banner and lists the main options: `1. Login`, `2. Add Student`, `3. List Students`, `4. Attendance`, `5. Assessment`, `6. Predictive Analytics & Insights`, `7. Cyber Wellness Audit`, `8. AI Assistant`, `9. Exit`.

---

### Step 3: Admin Login Authentication (Option 1)
You must authenticate as an administrator to access student management and analytics features.
- **Action**: Choose option `1`, then enter:
  - **Username**: `admin`
  - **Password**: `admin123`
- **Under the Hood**:
  - The function reads the user input, retrieves the hashed password from the `Admin_Login` table, and verifies it using `sha256` hashing (implemented in `authentication.py`).
  - Sets the global session state `logged_in` to `True`.
- **Expected Output**: `Login successful.`

---

### Step 4: Register a Student Profile (Option 2)
Test adding a new student to see how data validation works.
- **Action**: Choose option `2`, then enter:
  - **First Name**: `Aria`
  - **Last Name**: `Stark`
  - **Class/Section**: `12-A`
  - **DOB**: `2008-05-15` (Validates YYYY-MM-DD format)
  - **Gender**: `F` (Validates M, F, or O)
  - **Email**: `aria@winterfell.com` (Checks for `@` symbol)
  - **Phone**: `1112223333` (Checks for a 10-digit number)
- **Under the Hood**:
  - `validation.py` checks all string inputs.
  - Executes an `INSERT INTO Students` statement.
  - The database auto-increment feature generates `student_id = 101` (since IDs 1–100 were occupied by the seeder).
- **Expected Output**: `Student added successfully with ID: 101`

---

### Step 5: Log Student Attendance (Option 4)
Log a daily presence registry for the student.
- **Action**: Choose option `4`, select sub-option `1` (Mark Attendance), then enter:
  - **Student ID**: `101` (Or any ID from 1 to 100)
  - **Date**: Press **Enter** (Defaults to today's date)
  - **Status**: `P` (Marks present)
- **Under the Hood**:
  - Checks if the student exists in the database.
  - Inserts a record into the `Attendance` table linking the student ID and date.
- **Expected Output**: `Attendance marked successfully.`

---

### Step 6: Log Quiz Assessment Score (Option 5)
Record academic grades to calculate diagnostics.
- **Action**: Choose option `5`, select sub-option `1` (Add Assessment), then enter:
  - **Student ID**: `101`
  - **Score Obtained**: `95`
  - **Max Score**: `100`
  - **Date**: Press **Enter**
- **Under the Hood**:
  - Saves the quiz marks into `Diagnostic_Logs`. The program automatically uses this to compute the student's academic percentage.
- **Expected Output**: `Assessment added successfully.`

---

### Step 7: Record Cyber Wellness Habits (Option 7)
Enter digital wellbeing details to compute safety ratings.
- **Action**: Choose option `7`, select sub-option `1` (Add Cyber Audit), then enter:
  - **Student ID**: `101`
  - **Daily Screen Time (Hours)**: `3.0`
  - **Study Screen Time (Hours)**: `1.0`
  - **Recreational Screen Time (Hours)**: `2.0`
  - **Daily Sleep Duration (Hours)**: `8.0`
  - **Digital Distraction Level (1-5)**: `1`
  - **Cyber Safety Awareness Rating (1-5)**: `5`
  - **Remarks**: `Balanced usage`
- **Under the Hood**:
  - Evaluates digital wellness criteria and computes a Cyber-Wellness score:
    $$\text{Wellness Score} = 25\% \cdot \text{Sleep} + 25\% \cdot \text{Screen Time} + 25\% \cdot \text{Distraction} + 25\% \cdot \text{Safety}$$
  - Saves the record in `Cyber_Audit`.
- **Expected Output**: `Cyber wellness audit record added successfully.`

---

### Step 8: View Predictive Analytics & Visual Graphs (Option 6)
Demonstrate forecasting and visual reporting.
- **Action**: Choose option `6`, select sub-option `1` (View Single Student Analytics), then enter:
  - **Student ID**: `101`
- **Under the Hood**:
  - Computes the student's **Learning Health Score (LHS)** using the formula:
    $$\text{LHS} = 40\% \cdot \text{Academic Avg} + 25\% \cdot \text{Weekly Progress} + 20\% \cdot \text{Attendance \%} + 15\% \cdot \text{Cyber-Wellness Score}$$
  - Runs **Simple Linear Regression** on the weekly progress scores to forecast next week's score (represented as slope $m$ and intercept $c$).
  - Displays risk levels (`LOW`, `MEDIUM`, or `HIGH`) and flags alerts.
- **Action inside Sub-Menu**:
  - Choose **`1` (Generate & Save Visual Charts)**: Matplotlib creates 4 distinct charts (Progress line plot, Attendance donut chart, Wellness dual-axis, and Health component breakdown) and writes them to the `reports/` folder.
  - Choose **`2` (Export Report to CSV & Text Formats)**: Saves structured text summaries and CSV spreadsheets under `reports/`.
  - Choose **`3` (Back to Analytics Menu)** to exit the student view.

---

### Step 9: Talk to the AI Assistant (Option 8)
Ask conceptual or data-specific questions.
- **Action**: Choose option `8` to load the AI Assistant menu:
  - **Option 1 (Type a Question)**: Enter *"What is the meaning of Learning Health Score?"*
  - **Option 3 (Ask About Student)**: Enter Student ID `1` and ask *"Why is this student at medium risk?"*
  - **Option 4 (Student Suggestions)**: Enter Student ID `1` to get intervention recommendations.
- **Under the Hood**:
  - The script extracts database stats for Student ID `1` (or whichever ID you choose) and compiles a context string.
  - It sends the context + question + system instructions to the configured AI API (OpenAI GPT or Google Gemini) and prints the explanation.
  - If PyAudio is missing, choosing voice prompts catches PyAudio errors gracefully and falls back to typing.

---

### Step 10: Exit the Application (Option 9)
- **Action**: Choose option `9`.
- **Expected Output**: `Exiting.`

---

## Part B: School Installation Procedures (Deep Instructions)

### Scenario A: Working with an Offline School PC (SQLite Fallback)
Many school computers lack active MySQL Server setups. Use this process to run the app with SQLite:
1. **Copy folder via USB**: Copy the entire extracted project folder (including `pmla_scwe_fallback.db`) to the Desktop of the school PC.
2. **Execute directly**:
   When you run `python -m PMLA_SCWE.main`, the system notices that MySQL connection fails, prints a message, and automatically connects to SQLite using `pmla_scwe_fallback.db` in your root folder. No server setup or Workbench config is required!

---

### Scenario B: Offline Dependency Installation
If the school computer has no internet access to download Python packages:
1. **At home (with internet)**:
   Create a folder called `wheels/` inside your project directory and run:
   ```powershell
   pip download -r requirements.txt -d ./wheels
   ```
   This downloads the pre-compiled `.whl` files for all dependencies (Matplotlib, MySQL connector, openai, speechrecognition, pyttsx3, etc.).
2. **At school (offline)**:
   Plug in your USB drive, open the terminal in the project folder, and run:
   ```powershell
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```
   This will install all required packages at once from the local files on your USB without using the internet!

---

### Scenario C: Opening in VS Code vs. Python IDLE
- **Why avoid Python IDLE F5?**:
  - If you open `main.py` directly in Python IDLE and press **F5**, it runs the script inside the package directory, which breaks the import statements. You will get a `ModuleNotFoundError: No module named 'PMLA_SCWE'` error.
- **Correct Procedure**:
  - Open the **entire root folder** (`PMLA-SCWE`) in **VS Code** (using *File -> Open Folder*).
  - Open the VS Code integrated terminal and run:
    ```powershell
    python -m PMLA_SCWE.main
    ```
    This sets the package path correctly and executes the application flawlessly.
- **If VS Code is not installed**:
  - Open the Windows Command Prompt (`cmd`) or PowerShell, navigate to the directory:
    ```cmd
    cd C:\Users\User\Desktop\PMLA-SCWE
    ```
  - Run the program command from there:
    ```cmd
    python -m PMLA_SCWE.main
    ```
