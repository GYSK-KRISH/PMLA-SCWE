# PMLA-SCWE: Comprehensive Presentation & Running Guide

This guide is designed to help you run the **PMLA-SCWE** application on any computer and explain every line of code, math formula, and database concept to your evaluator to secure full marks.

---

## 1. Project Meaning & Objectives

**What is PMLA-SCWE?**
It is a student performance analysis and wellness prediction engine. It monitors two major facets of student life:
1. **Academic Progress**: Tracked via diagnostic assessments and weekly progress scores.
2. **Cyber-Wellbeing**: Tracked via digital habits (daily screen time, sleep duration, distraction level, and safety awareness).

**Project Objectives (What to tell your teacher):**
- **Data Integration**: Standardize student academic and cyber-wellbeing logs into a single database.
- **Explainable Analytics**: Calculate a composite **Learning Health Score (LHS)** to assess overall performance.
- **Academic Forecasting**: Apply **Simple Linear Regression** on weekly progress trend data to forecast the student's next score.
- **Risk Identification**: Automatically flag students as **Low, Medium, or High Risk** and list diagnostic reasons (e.g. low attendance, wellness concern, declining trend).
- **Interactive AI Assistant**: Ask questions about students or system concepts using typed or voice commands, with automated TTS (Text-to-Speech) feedback.
- **Robustness (Graceful Fallbacks)**: Designed to run anywhere. If MySQL is unavailable, it runs on SQLite. If voice libraries are missing, it falls back to text.

---

## 2. System Architecture & File Structure

The project has a clean, modular structure. Explain how files interact:

```text
                             USER INTERFACE
                   (main.py / main.py --web / desktop/)
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
DATABASE PATHWAYS (core/database.py)  ANALYTICS (core/analytics.py)  AI & VOICE (core/ai_assistant.py)
   ├─ MySQL (Default Port 3306)       ├─ Regression Trend            ├─ OpenAI & Gemini Clients
   └─ SQLite (Fallback File)          ├─ Learning Health Score       ├─ Speech-to-Text (Voice)
                                      └─ Risk Classifications        └─ Text-to-Speech (Audio)
```

### Module Breakdown
1. **[main.py](file:///d:/PMLA-SCWE/main.py)**: Router entry point. Parses CLI args and starts the desktop GUI or Flask web app.
2. **[seed_data.py](file:///d:/PMLA-SCWE/seed_data.py)**: Clears existing data, resets ID counters, and seeds 100 mock student profiles.
3. **[diagnose_setup.py](file:///d:/PMLA-SCWE/diagnose_setup.py)**: 5-stage setup verification tool.
4. **[core/database.py](file:///d:/PMLA-SCWE/core/database.py)**: Manages database connections and SQLite fallback mode.
5. **[core/analytics.py](file:///d:/PMLA-SCWE/core/analytics.py)**: Computes regression line slopes, future score predictions, and composite Learning Health Scores.
6. **[core/recommendation.py](file:///d:/PMLA-SCWE/core/recommendation.py)**: Generates explainable risk classifications and teacher alerts.
7. **[core/graphs.py](file:///d:/PMLA-SCWE/core/graphs.py)**: Renders Matplotlib plots and outputs them as PNGs.
8. **[core/reports.py](file:///d:/PMLA-SCWE/core/reports.py)**: Compiles structured CSV/TXT reports.

---

## 3. Explaining the Database Design (Schema)

Your database contains **12 tables** structured to minimize redundancy:

- **`Students`**: Basic personal details (ID, Name, Section, DOB, Email).
- **`Admin_Login`**: Administrator username and hashed password credentials (legacy support).
- **`Users`**: Multi-user accounts (Teacher, Admin, Student) with roles and statuses.
- **`Learning_Objectives`**: Academic subject descriptions and learning targets.
- **`Diagnostic_Logs`**: Assessment scores (obtained score vs max score) linked to objectives.
- **`Attendance`**: Daily present (`P`) or absent (`A`) logs.
- **`Cyber_Audit`**: Sleep duration, screen hours (daily, study, recreational), safety levels.
- **`Weekly_Progress`**: Weekly progress scores for regression analysis.
- **`Achievements`**: Student badges and awards.
- **`Notifications`**: System alerts and messages.
- **`Reports_Metadata`**: Metadata logs for exported reports.
- **`Activity_Log`**: Logs of system activities.

### Database Keys & Constraints
- **Primary Key (PK)**: Uniquely identifies a row in a table (e.g., `student_id` in `Students`).
- **Foreign Key (FK)**: References the primary key of another table to maintain relationships (e.g., `student_id` in `Attendance` references `student_id` in `Students`).
- **`ON DELETE CASCADE`**: A constraint ensuring that if a student is deleted from the `Students` table, all of their attendance records, assessment scores, and cyber audits are automatically deleted to prevent orphaned records.

---

## 4. Mathematics & Logic

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

### B. Learning Health Score (LHS)
A composite index reflecting student performance across four categories:
$$\text{LHS} = 40\% \cdot \text{Academic Avg} + 25\% \cdot \text{Weekly Progress} + 20\% \cdot \text{Attendance Rate} + 15\% \cdot \text{Cyber-Wellness Score}$$

### C. Student Risk Classification
Students are dynamically grouped based on LHS, Attendance, and Progress:
- **HIGH RISK**: If LHS $< 50$, OR if Attendance Rate $< 75\%$, OR if the academic trend is **Declining** while LHS $< 65$.
- **MEDIUM RISK**: If LHS is between $50$ and $75$, or if there are active cyber-wellness concerns.
- **LOW RISK**: If LHS $\ge 75$ and Attendance Rate $\ge 85\%$ with a stable or improving trend.

---

## 5. Sample Viva Questions & Answers

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
