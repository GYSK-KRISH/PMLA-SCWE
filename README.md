# PMLA-SCWE: Predictive Micro-Learning Analytics & Student Cyber-Wellbeing Engine

PMLA-SCWE is a student analytics and digital wellness engine built as a modular Python application with dual interfaces (desktop GUI and web console). It combines a MySQL/SQLite-backed data model, linear regression analytics, and an explainable AI assistant to monitor student academic progress and cyber-wellbeing.

---

## 🚀 Quick Start

1. **Verify your environment**:
   ```powershell
   python diagnose_setup.py
   ```
2. **Seed the database**:
   ```powershell
   python seed_data.py
   ```
3. **Launch the application**:
   - **Desktop GUI (CustomTkinter)**:
     ```powershell
     python main.py
     ```
   - **Web Interface (Flask Console)**:
     ```powershell
     python main.py --web
     ```

---

## 📋 What This Project Does

The engine integrates and monitors two major dimensions of student life:

1. **Academic Analytics**:
   - **CRUD Operations**: Manage student records (add, edit, list, delete).
   - **Attendance Tracker**: Daily registry (Present/Absent) with automatic percentage calculations.
   - **Diagnostic Assessments**: Academic test logging (marks obtained vs max marks).
   - **Weekly Progress Tracking**: Weekly checkpoints to establish score trends.
   - **Predictive Analytics**: Runs **Simple Linear Regression** over weekly checkpoints to forecast next week's score.
   - **Learning Health Score (LHS)**: Composite indicator:
     $$\text{LHS} = 40\% \cdot \text{Academic Avg} + 25\% \cdot \text{Weekly Progress} + 20\% \cdot \text{Attendance \%} + 15\% \cdot \text{Cyber-Wellness Score}$$

2. **Cyber-Wellbeing & Digital Health**:
   - **Cyber Wellness Audits**: Tracks screen time hours (study vs recreational), daily sleep hours, distraction levels, and safety ratings.
   - **Composite Wellness Score**: Calculates digital safety and health levels.
   - **Explainable Teacher Alerts**: Classifies students into **Low, Medium, or High Risk** categories based on combined wellness, attendance, and regression metrics.

3. **Advanced Integrations**:
   - **Matplotlib Visualization Exporter**: Generates line charts, donut charts, and health breakdowns, saving them in the `reports/` folder.
   - **Explainable AI Assistant**: Type or speak (voice synthesis via `pyttsx3`) questions about student performance.
   - **Portability (Dual Backends)**: Automatically connects to local MySQL on port 3306 or falls back to a local `pmla_scwe_fallback.db` SQLite database if the MySQL service is offline.

---

## 📂 Project Structure

```text
PMLA-SCWE/
├── main.py                   # Main entry point (CLI argument router)
├── seed_data.py              # Root-level mock database seeding script
├── diagnose_setup.py         # 5-stage setup verification tool
├── requirements.txt          # Minimal project library dependencies
├── schema.sql                # MySQL Workbench database creation script
│
├── core/                     # Business Logic and Database Services
│   ├── database.py           # MySQL/SQLite query execution and auto-fallback
│   ├── auth_service.py       # Password PBKDF2 hashing and authentication
│   ├── student_service.py    # Student record database transactions
│   ├── analytics.py          # Regression math and LHS computations
│   ├── recommendation.py     # Teacher risk flags and intervention logic
│   ├── graphs.py             # Matplotlib rendering services
│   ├── reports.py            # Text and CSV export builders
│   ├── ai_assistant.py       # OpenAI / Gemini API orchestration
│   └── voice_service.py      # SpeechRecognition and pyttsx3 audio engines
│
├── desktop/                  # CustomTkinter Desktop Client
│   ├── app.py                # Main GUI frame and theme controller
│   └── dashboard.py          # Dashboard visualization widgets
│
├── web/                      # Flask Web Console
│   ├── app.py                # Flask server initializer
│   ├── routes/               # HTTP endpoint routers
│   └── templates/            # HTML presentation pages
│
├── database/                 # Original database schema directory
│   └── schema.sql            # Master schema (Source of truth)
│
└── reports/                  # Generated PDF/PNG charts, text, and CSVs
```

---

## 🛠️ Step-by-Step Installation

### 1. Open the project workspace
Open the `PMLA-SCWE` root directory in VS Code (**File -> Open Folder...**).

### 2. Configure a virtual environment (VENV)
Open the integrated VS Code terminal (`Ctrl + Shift + ~`) and run:
```powershell
python -m venv .venv
```
Select the virtual environment interpreter in VS Code (`Ctrl + Shift + P` -> `Python: Select Interpreter` -> choose `.venv\Scripts\python.exe`). Close and reopen the terminal to activate it.

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Database Setup (Optional MySQL)
1. Ensure the MySQL service is running on your system (e.g. check `services.msc`).
2. Open MySQL Workbench, open the root `schema.sql` script, and execute it to create the database schema.
3. If necessary, change the root database password in `core/config.py`.

*Note: If MySQL is not running or connection fails, the app will automatically switch to SQLite fallback and write data to `pmla_scwe_fallback.db`.*

---

## 🤖 AI Assistant Configuration

1. Create a `.env` file in the root directory (based on `.env.example`).
2. Add your keys:
   - For OpenAI: `OPENAI_API_KEY=your_key_here`
   - For Gemini: `GEMINI_API_KEY=your_key_here`
3. If no key is set, the app will run with the local rules-based engine and bypass API calls gracefully.

---

## 🔍 Troubleshooting

- **ModuleNotFoundError**: Ensure you are running commands from the project root and that your virtual environment `(.venv)` is active.
- **Microphone issues**: If PyAudio fails to install or a mic is missing, the AI Assistant voice mode will gracefully fall back to keyboard entry.
- **Port 3306 error**: Check your Windows Services settings to ensure MySQL is running, or let the app run on the auto-generated SQLite database.
