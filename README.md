# PMLA-SCWE

Predictive Micro-Learning Analytics and Student Cyber-Wellbeing Engine.

PMLA-SCWE is a school analytics project package built for CBSE-style project work. It combines a MySQL-backed data model, a modular Python application, and supporting documentation for students, teachers, and evaluators.

If you want the full step-by-step version that explains how to run the project and how to present it in viva, open [RUN_AND_EXPLAIN.md](RUN_AND_EXPLAIN.md).

## What This Project Does

The project currently supports:
- **Student CRUD Operations**: Add, update, view, and delete student profiles.
- **Admin Login Hashing**: Secure hashed administrator access via console.
- **Attendance Registry**: Record present, absent, or leave details with percentage counters.
- **Diagnostic Assessments**: Track marks obtained vs max marks for academic quizzes.
- **Weekly Progress Logs**: Record weekly checkpoints to track improvement curves.
- **Predictive Analytics**: Runs mathematical linear regression trends and risk category mappings.
- **Visual Charting & Exporters**: Outputs matplotlib figures and CSV/text report documents.
- **Database Fallbacks**: Automatically falls back to SQLite if local MySQL service is inactive.
- **Explainable AI Assistant**: Type or speak voice questions to query context-rich student reports.

## Project Structure

- `PMLA_SCWE/` - Python package containing the application code
  - `database.py` - handles MySQL connection and SQLite fallback logic.
  - `analytics.py` - handles mathematical computations (LHS, linear regression, averages).
  - `recommendation.py` - flags rule-based teacher alerts and risk classifications.
  - `graphs.py` - renders academic trends, wellness stats, and class comparisons.
  - `reports.py` - builds formatted student/class txt documents and CSV files.
  - `ai_assistant.py` - manages OpenAI/Gemini clients and voice synthesis.
  - `main.py` - routes command-line loops and submenu layouts.
- `schema.sql` - MySQL database script for schema creation.
- `requirements.txt` - Python project package dependencies.
- `RUN_AND_EXPLAIN.md` - Comprehensive student run instructions and Viva Q&As.

## Requirements

- Python 3.14+ or compatible Python 3.x installation
- MySQL Server & Workbench (Optional - Fallback database included)
- Python packages listed in `requirements.txt`

### Python dependencies

The project uses:
- `matplotlib` (data visualization)
- `mysql-connector-python` (MySQL driver)
- `openai` & `google-genai` (AI Assistant APIs)
- `SpeechRecognition` & `pyttsx3` (voice command recording and voice synthesis)

## Database Overview

The database name used by the project is `pmla_scwe`.

Main tables include:

- `Admin_Login`
- `Students`
- `Learning_Objectives`
- `Diagnostic_Logs`
- `Cyber_Audit`
- `Weekly_Progress`
- `Achievements`
- `Attendance`
- `Activity_Log`
- `Reports_Metadata`

## MySQL Workbench Setup

Use these values when creating the connection in MySQL Workbench:

- Connection Name: `PMLA-SCWE Project Package`
- Hostname: `127.0.0.1` or `localhost`
- Port: `3306`
- Username: `root`
- Password: your local MySQL root password
- Default Schema: `pmla_scwe`

Important notes:

- Do not put `:3306` inside the Hostname field.
- If Workbench says the database is unknown, leave Default Schema blank for the first connection test.
- Run `schema.sql` first to create the database and tables.

## Setup Instructions

### 1. Clone or open the workspace

Open the project folder in VS Code or your preferred editor.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

If your Python installation blocks direct package changes, install into the project virtual environment instead.

### 5. Create the database schema

Open `schema.sql` in MySQL Workbench or run it from the SQL editor. The script creates the `pmla_scwe` database and all tables.

If you want to reset the database before rerunning the schema:

```sql
DROP DATABASE IF EXISTS pmla_scwe;
CREATE DATABASE pmla_scwe;
USE pmla_scwe;
```

### 6. Seed sample data

To load 100 sample students and related rows, run:

```powershell
python -m PMLA_SCWE.seed_data
```

This seeds:

- 100 students
- 100 diagnostic log rows
- 100 attendance rows
- 100 cyber audit rows
- 100 weekly progress rows
- report metadata rows
- activity log rows
- sample achievements

## Running the App

Start the menu application with:

```powershell
python -m PMLA_SCWE.main
```

When the app starts, it shows the main menu:

- Login
- Add Student
- List Students
- Attendance
- Assessment
- Predictive Analytics & Insights
- Exit

## Default App Login

The application creates a default admin account when no admin exists yet.

- Username: `admin`
- Password: `admin123`

## Main Menu Features

### Login

Logs into the application using the admin credentials stored in the database.

### Add Student

Adds a student record with:

- first name
- last name
- class or section
- date of birth
- gender
- email
- phone

### List Students

Displays the students currently stored in the database.

### Attendance

Provides options to:

- mark attendance
- calculate attendance percentage

### Assessment

Provides options to:

- add a diagnostic assessment
- view assessment history

### Predictive Analytics & Insights

Provides statistical predictive analytics and risk classification:
- **View Single Student Analytics**: Calculates a student's performance trend using simple linear regression, estimates next week's score, computes a weighted Learning Health Score, and classifies risk levels.
- **Class-wide Risk Report**: Aggregates high-risk students and active alerts (such as declining weekly trends, wellness concerns, or critical attendance) for proactive teacher intervention.

## SQLite Fallback

If MySQL is not available, the application falls back to a local SQLite database file named `pmla_scwe_fallback.db`.

This lets you run and test the app even when the MySQL connector or MySQL server is unavailable.

## Sample Data Helper

The file `PMLA_SCWE/seed_data.py` loads bulk sample data into the current database.

You can rerun it safely. It will fill missing sample rows and keep the app data usable for demonstrations.

## Documentation Folder

The `documentation/` folder contains extra notes, including MySQL Workbench connection instructions and project documentation content.

## Troubleshooting

### MySQL connection fails

- Check that MySQL Server is running.
- Confirm the host is `127.0.0.1`.
- Confirm the port is `3306`.
- Confirm the root password is correct.

### Unknown database error

If Workbench says `Unknown database 'pmla_scwe'`, connect first without setting a default schema, then run `schema.sql`.

### Login does not work

- Make sure the database contains an admin row.
- Use the default login `admin / admin123` if no admin has been created yet.

### App starts but MySQL is unavailable

The SQLite fallback should still allow the app to run. Check the generated file `pmla_scwe_fallback.db` in the project root.

## Current Status

The project is now fully functional with:
- Schema creation & MySQL Workbench setup
- SQLite fallback database support
- Administrator login authentication
- Student CRUD operations
- Attendance and diagnostic assessment tracking
- Matplotlib visualizations (academic trends, attendance, cyber-wellness, learning health)
- Data export features (text reports and CSV spreadsheets)
- Statistical predictive models (regression forecasting) & risk classification
- **AI Assistant Integration (Q&A, context-aware student analysis, suggestions)**
- **Voice Command Interface (Speech-to-Text & optional Text-to-Speech)**

---

## AI Assistant & Voice Command Integration

PMLA-SCWE features a built-in AI Assistant module (`ai_assistant.py`) which acts as an explainable decision-support engine. 

### What it Does
1. **General Q&A**: Answers conceptual questions about micro-learning and digital wellbeing.
2. **Contextual Student Analysis**: Reads current analytics data (academics, weekly trends, attendance, cyber-wellness score, risk levels) and explains the student's status.
3. **Actionable Suggestions**: Recommends practical educational interventions for the student.
4. **Voice Commands**: Captures speech from your microphone, converts it to text, processes it through the AI, and optional reads responses aloud using text-to-speech.

### How to Configure API Keys
To use the AI features, you must configure either OpenAI or Google Gemini. 
1. Create a `.env` file in the project root directory (copy `.env.example`).
2. Add your API key:
   - For OpenAI: `OPENAI_API_KEY=your_key_here`
   - For Gemini: `GEMINI_API_KEY=your_key_here`
3. The app will automatically read the keys from the environment. **Do not commit your `.env` file to git.**

### Running Voice Commands
Make sure you install the required voice libraries:
```powershell
pip install SpeechRecognition pyttsx3
```
*Note: Voice features will fall back gracefully to keyboard entry if a microphone is not connected or pyttsx3 is not installed.*

