# PMLA-SCWE: Comprehensive School Presentation & Running Guide

This guide is designed to help you run the **PMLA-SCWE** (Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine) application on **any computer (including your school's computer)** and explain every line of code, math formula, and database concept to your teacher in a deep, impressive manner to secure full marks.

---

## 1. Deep Project Meaning & Objectives

**What is PMLA-SCWE?**
It is a student performance analysis and wellness prediction engine. It monitors two major facets of student life:
1. **Academic Progress**: Tracked via diagnostic assessments and weekly progress scores.
2. **Cyber-Wellbeing**: Tracked via digital habits (daily screen time, recreational screen time, sleep duration, distraction level, and safety awareness).

**Project Objectives (What to tell your teacher):**
- **Data Integration**: Standardize student academic and cyber-wellbeing logs into a single database.
- **Explainable Analytics**: Calculate a composite **Learning Health Score (LHS)** to assess overall performance.
- **Academic Forecasting**: Apply **Simple Linear Regression** on weekly progress trend data to forecast the student's next score.
- **Risk Identification**: Automatically flag students as **Low, Medium, or High Risk** and list diagnostic reasons (e.g. low attendance, wellness concern, declining trend).
- **Interactive AI Assistant**: Ask questions about students or system concepts using typed or voice commands, with automated TTS (Text-to-Speech) feedback.
- **Robustness (Graceful Fallbacks)**: Designed to run anywhere. If MySQL is unavailable, it runs on SQLite. If voice libraries are missing, it falls back to text.

---

## 2. Deep System Architecture & File Structure

The project has a clean, modular structure. Explain how files interact:

```text
                             USER MENU (main.py)
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
DATABASE PATHWAYS (database.py)  ANALYTICS ENGINE (analytics.py)  AI & VOICE (ai_assistant.py)
   ├─ MySQL (Default Port 3306)      ├─ Regression Trend             ├─ OpenAI Client
   └─ SQLite (Local Fallback File)   ├─ Learning Health Score        ├─ Gemini Client
                                     └─ Risk Classifications         ├─ Speech-to-Text (Voice)
                                                                     └─ Text-to-Speech (Audio)
```

### Module Breakdown
1. **[main.py](file:///d:/PMLA-SCWE/PMLA_SCWE/main.py)**: The main user interface. It renders menus, takes input, runs validations, and routes user actions.
2. **[database.py](file:///d:/PMLA-SCWE/PMLA_SCWE/database.py)**: Manages database connections. Contains the **SQLite Fallback Logic** that switches the app to SQLite if MySQL Server is offline.
3. **[analytics.py](file:///d:/PMLA-SCWE/PMLA_SCWE/analytics.py)**: The mathematical heart of the app. Computes averages, regression line slopes, future score predictions, and final Learning Health Scores.
4. **[recommendation.py](file:///d:/PMLA-SCWE/PMLA_SCWE/recommendation.py)**: The rule-based engine. Generates explainable alerts, intervention plans, and risk reasons for teachers.
5. **[ai_assistant.py](file:///d:/PMLA-SCWE/PMLA_SCWE/ai_assistant.py)**: Integrates OpenAI and Google Gemini APIs. Also manages microphone capturing (`SpeechRecognition`) and offline text-to-speech output (`pyttsx3`).
6. **[graphs.py](file:///d:/PMLA-SCWE/PMLA_SCWE/graphs.py)**: Generates visual charts (line graphs, donut charts, scatter plots) using Matplotlib and saves them under the `reports/` folder.
7. **[reports.py](file:///d:/PMLA-SCWE/PMLA_SCWE/reports.py)**: Assembles textual reports and exports student/class statistics to CSV spreadsheets.

---

## 3. Explaining the Database Design (Deep Schema)

Your database contains **10 tables** structured to minimize redundancy:

- **`Students`**: Stores basic personal details (ID, Name, Section, DOB, Email).
- **`Admin_Login`**: Stores administrator username and hashed password credentials.
- **`Learning_Objectives`**: Stores names of academic subjects and learning targets.
- **`Diagnostic_Logs`**: Stores diagnostic test results (Obtained Score vs Max Score).
- **`Attendance`**: Tracks presence (`P` for present, `A` for absent, `L` for leave) per date.
- **`Cyber_Audit`**: Stores daily screen hours, recreational screen hours, sleep hours, safety ratings (1-5), and distraction levels (1-5).
- **`Weekly_Progress`**: Tracks weekly test scores used to compute regression trends.
- **`Achievements`**: Stores student awards or badges.
- **`Reports_Metadata`**: Logs generated reports.
- **`Activity_Log`**: Logs system transactions for audit trails.

### Database Keys & Constraints
- **Primary Key (PK)**: Uniquely identifies a row in a table (e.g., `student_id` in `Students`).
- **Foreign Key (FK)**: References the primary key of another table to maintain relationships (e.g., `student_id` in `Attendance` references `student_id` in `Students`).
- **`ON DELETE CASCADE`**: A constraint ensuring that if a student is deleted from the `Students` table, all of their attendance records, assessment scores, and cyber audits are automatically deleted to prevent orphaned records.

---

## 4. Explaining the Mathematics & Logic (Super Deep)

Teachers love mathematical explanations. Memorize these formulas:

### A. Simple Linear Regression (Academic Score Forecasting)
Given a list of weekly progress scores over time $y$ at weeks $x = [1, 2, 3, 4, ...]$, the app fits a regression line:
$$y = mx + c$$
- **Slope ($m$)**: Represents the trend direction.
  $$m = \frac{N \sum(xy) - \sum x \sum y}{N \sum(x^2) - (\sum x)^2}$$
- **Intercept ($c$)**: The starting baseline value.
  $$c = \frac{\sum y - m \sum x}{N}$$
- **Forecasted Score**: Calculated for the next week ($N+1$):
  $$\text{Predicted Score} = m \cdot (N+1) + c \quad \text{(clamped between 0 and 100)}$$
- **Trend Classification**:
  - **Improving**: Slope $m > 0.1$
  - **Declining**: Slope $m < -0.1$
  - **Stable**: Slope $-0.1 \le m \le 0.1$
  - If a student has fewer than 2 weeks of progress records, the trend defaults to **Stable** and the prediction defaults to their latest score.

### B. Learning Health Score (LHS)
A composite index reflecting student performance across four categories:
$$\text{LHS} = 40\% \cdot \text{Academic Avg} + 25\% \cdot \text{Weekly Progress} + 20\% \cdot \text{Attendance Rate} + 15\% \cdot \text{Cyber-Wellness Score}$$
- **Academic Average**: Derived from Diagnostic Logs.
- **Weekly Progress**: Average of weekly test scores.
- **Attendance Rate**: Percentage of present status (`P`).
- **Cyber-Wellness Score**: Calculated as:
  $$\text{Wellness Score} = 25\% \cdot \text{Sleep} + 25\% \cdot \text{Screen Hours} + 25\% \cdot \text{Distraction Level} + 25\% \cdot \text{Safety Rating}$$

### C. Student Risk Classification
Students are dynamically grouped based on LHS, Attendance, and Progress:
- **HIGH RISK**: If LHS $< 50$, OR if Attendance Rate $< 75\%$, OR if the academic trend is **Declining** while LHS $< 65$.
- **MEDIUM RISK**: If LHS is between $50$ and $75$, or if there are active cyber-wellness concerns.
- **LOW RISK**: If LHS $\ge 75$ and Attendance Rate $\ge 85\%$ with a stable or improving trend.

---

## 5. Setting up & Running in a School Computer Environment

School computers are often **offline** or **restrictive** (no admin access, no MySQL server, and no internet to download pip libraries). The project is built to handle this seamlessly.

### Scenario A: Offline School Computer (Using SQLite Fallback)
If the school computer does not have MySQL Server installed or running:
1. **Copy the Entire Project Folder**: Copy the project folder (including `pmla_scwe_fallback.db`) to a flash drive and paste it onto the school computer.
2. **Execute Directly using SQLite**:
   The application detects that MySQL is offline and automatically loads/creates the database tables inside `pmla_scwe_fallback.db` in the project root.
3. **No Setup Required**: You do not need to install MySQL, configure Workbench, or type a database password! The SQLite engine is built directly into Python.

### Scenario B: Offline Package Installation
If the school computer does not have the required libraries (like `matplotlib` or `mysql-connector-python`) and has no internet connection:
1. **Download wheels on your home computer**:
   On your home computer (connected to the internet), create a folder `wheels/` and run:
   ```powershell
   pip download -r requirements.txt -d ./wheels
   ```
2. **Copy the wheels folder**: Transfer the `wheels/` directory to the school computer via a USB drive.
3. **Install Offline on the School Computer**:
   Open a terminal in the project folder and run:
   ```powershell
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```
   This will install Matplotlib, MySQL connectors, and helper libraries directly from the local files without requiring the internet.

### Scenario C: Standard MySQL Workbench Environment (Online/Connected)
If the school computer has a running MySQL instance:
1. **Configure Connection**: Edit the `PMLA_SCWE/config.py` file to match the school computer's MySQL password.
2. **Run Schema**: Open MySQL Workbench, open the file `schema.sql`, and execute it to create the database.
3. **Run Seeder**: Seed the database with 100 students:
   ```powershell
   python -m PMLA_SCWE.seed_data
   ```
4. **Run Application**:
   ```powershell
   python -m PMLA_SCWE.main
   ```

---

## 6. Explaining the AI & Voice Command Fallbacks

If your teacher asks how the AI Assistant works, explain these four levels of fallback design:

1. **AI Key Fallback**:
   - If `OPENAI_API_KEY` or `GEMINI_API_KEY` is not present in the environment variables, the program does not crash. It displays: *"AI is not configured. Please add the API key as an environment variable."*
2. **Voice Recognition Fallback (Stage 10)**:
   - If the `SpeechRecognition` library is missing, or if PyAudio fails to load (due to lack of compiler headers on Windows), selecting `2. Voice Command` displays: *"SpeechRecognition library is not installed..."* or *"Microphone or capture error..."* and returns the user to safety, allowing them to type their questions instead.
3. **Text-to-Speech (TTS) Fallback**:
   - The app uses `pyttsx3` to read responses. If the system audio driver is missing, it catches the error silently, bypasses the speech, and prints the text response clearly on the screen.
4. **Data Isolation (Security)**:
   - The AI only receives the raw statistical scores and counts for a specific student. It never receives sensitive database information or system keys.

---

## 7. Sample Viva Questions & Answers for Your Exam

Here are 10 questions the external examiner or your teacher might ask:

1. **Q: What is a Primary Key and Foreign Key in your schema?**
   - **A**: The primary key uniquely identifies a record (e.g. `student_id` in `Students` table). The foreign key links tables together (e.g. `student_id` in `Attendance` links back to the `Students` table).

2. **Q: Why does your project have a database fallback?**
   - **A**: It ensures portability. If MySQL Server is not running on the evaluator's system, the app automatically switches to an offline SQLite database (`pmla_scwe_fallback.db`) so the project can still be fully evaluated.

3. **Q: How are you predicting the student's next score?**
   - **A**: I implemented simple linear regression. By taking weekly progress scores as $y$ and weeks as $x$, the program calculates the slope ($m$) and intercept ($c$) to forecast $y$ for the next week ($x = N+1$).

4. **Q: What formulas did you use for the regression line?**
   - **A**: The slope is computed as $m = \frac{N \sum(xy) - \sum x \sum y}{N \sum(x^2) - (\sum x)^2}$, and the intercept is $c = \frac{\sum y - m \sum x}{N}$.

5. **Q: What is the purpose of `ON DELETE CASCADE`?**
   - **A**: It maintains referential integrity. If a student record is deleted from the `Students` table, all linked rows in the `Attendance`, `Diagnostic_Logs`, and `Cyber_Audit` tables are deleted automatically to prevent orphaned database rows.

6. **Q: Why did you use `matplotlib.use('Agg')` in your plotting script?**
   - **A**: The `Agg` backend is non-interactive. It allows the Python application to generate and save PNG charts directly to disk (`reports/`) without opening GUI windows, which prevents shell crashes during automated runs.

7. **Q: How does the AI Assistant obtain student information?**
   - **A**: It executes the local database queries first, builds a text-based summary of scores (attendance rate, academic average, risk level), and passes that text summary as context to the AI model. It does not allow the AI to directly query the database, ensuring safety and preventing data fabrication.

8. **Q: What happens if PyAudio is not installed?**
   - **A**: PyAudio requires C++ compilers on Windows. If it is missing, our code catches the `ImportError` or initialization failure gracefully and informs the user to use option 1 (Type a Question) instead of crashing.

9. **Q: How is the Cyber-Wellness score computed?**
   - **A**: It is a weighted average of sleep duration, screen time safety index, digital distraction frequency, and overall digital awareness, scaled from 0 to 100%.

10. **Q: What Python libraries are required to run this project?**
    - **A**: `mysql-connector-python` (for MySQL database connections), `matplotlib` (for chart plotting), `openai` / `google-genai` (for AI Assistant queries), `SpeechRecognition` (for voice recognition), and `pyttsx3` (for voice synthesis).
