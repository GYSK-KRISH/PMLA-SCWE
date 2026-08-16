# PMLA-SCWE: Installation, Setup & Verification Guide
## Comprehensive Start-to-Finish Runbook — Version 2.0 (Phase 1 Checkpoint)

---

## 1. System Requirements & Prerequisites

### 1.1 Hardware Specifications
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM**: 4 GB minimum (8 GB recommended for graphical rendering and local AI).
- **Storage**: 500 MB free hard disk space.
- **Display**: $1280 \times 720$ minimum resolution ($1920 \times 1080$ recommended).

### 1.2 Software Prerequisites
- **Operating System**: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+).
- **Python**: Python 3.10, 3.11, 3.12, 3.13, or 3.14.
  - *Windows*: Ensure the checkbox **"Add Python to PATH"** was checked during installation.
- **Database (Optional)**: MySQL Server 8.0+ (if uninstalled or offline, the built-in SQLite auto-fallback engages automatically).

---

## 2. Quick-Start (Automated Launcher)

### Windows Automated Launcher
Double-click `setup_and_run.bat` or run:
```cmd
setup_and_run.bat
```
*This launcher automatically checks Python, creates `.venv`, installs dependencies from `requirements.txt` (or local `wheels/` if offline), verifies database tables, and presents a launch menu.*

### Cross-Platform Python Setup Utility
```powershell
.venv\Scripts\python.exe scripts\setup_project.py
```

---

## 3. Step-by-Step Manual Installation

### Step 1: Clone or Open Workspace
```powershell
cd d:\PMLA-SCWE
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv .venv
.\.venv\Scripts\activate.bat

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Package Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (`.env`)
Copy `.env.example` to create your local `.env`:
```powershell
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS / CMD
cp .env.example .env
```

Edit `.env` to configure your database credentials and optional AI keys:
```env
# AI Provider Configuration (auto, gemini, openai, offline)
AI_PROVIDER=auto

# OpenAI Configuration (Optional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Google Gemini Configuration (Optional)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Database Configuration (MySQL Primary)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pmla_scwe
DB_PORT=3306
```

### Step 5: Run Setup Diagnostics
```powershell
python diagnose_setup.py
```
*Verify that all 5 diagnostic stages report `[PASS]`.*

---

## 4. Database Setup, Migrations & Seeding

### 4.1 Non-Destructive Schema Initialization
```powershell
python -c "from core.database import initialize_database; initialize_database()"
```

### 4.2 Execute Version 2.0 Phase 1 Migration
```powershell
python -m database.migrations.v2_0_phase_1
```

### 4.3 Populate Clean Demonstration Mock Data (100 Students)
```powershell
python seed_database.py --reset
```
*Type `YES` when prompted to seed 100 mock students with attendance, diagnostic logs, weekly progress trends, and cyber wellness audits.*

---

## 5. Launching Applications

### Option A: PySide6 Desktop GUI Client (Primary Interface)
```powershell
python main.py
```
- **Default Administrator**: Username: `admin` | Password: `admin123`
- Features modern dark UI (`#080A12` base), KPI cards, Student 360° modals, attendance registry, regression insights, intervention pipeline, and ReportLab PDF exports.

### Option B: Flask Web Server (Browser Interface)
```powershell
python main.py --web
```
- Open your browser to: `http://127.0.0.1:5000`
- **Default Administrator**: Username: `admin` | Password: `admin123`
- Features responsive glassmorphism, AJAX notification updates, live markdown previews, and full analytics dashboards.

---

## 6. Offline Installation (Evaluator Laptop Without Internet)

If the target evaluator computer has no internet connection:

1. **On an internet-connected machine**:
   ```powershell
   download_wheels.bat
   ```
   *Downloads all dependencies into a local `wheels/` directory.*
2. **Copy the entire project folder** (including `wheels/` and `pmla_scwe_fallback.db`) via USB drive to the target computer.
3. **On the offline machine**:
   ```powershell
   setup_and_run.bat
   ```
   *The launcher automatically detects the `wheels/` folder and performs offline installation without internet.*

---

## 7. Verification & Testing

### Running All Unit Tests
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```
*Expected baseline: 78 tests passing (100% OK).*

### Running Version 2.0 Phase 1 Smoke Test
```powershell
.venv\Scripts\python.exe tests\smoke_test_v2.py
```
*Expected baseline: All 5 smoke test checkpoints passing.*

---

## 8. Troubleshooting & Common Setup Issues

### Problem 1: PowerShell Script Execution Disabled
- **Error**: `.\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
- **Solution**: Open PowerShell and run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```

### Problem 2: MySQL Connection Refused
- **Behavior**: MySQL server is offline or uninstalled.
- **Resolution**: No action required! PMLA-SCWE automatically engages the SQLite fallback engine (`pmla_scwe_fallback.db`) without crashing.

### Problem 3: PySide6 Display Scaling on High-DPI Monitors
- **Solution**: High-DPI pixmap scaling is enabled by default in `desktop/app.py`. Ensure your display scaling is set between 100% and 150% for optimal layout.
