# PMLA-SCWE: Desktop Computer Installation & Setup Guide

> [!NOTE]
> **STATUS: HISTORICAL / ARCHIVAL DOCUMENT (Desktop Setup Reference)**  
> This file is preserved for historical reference. For current, verified setup and installation documentation, see:
> - Master Documentation: [PROJECT_MASTER_DOCUMENTATION.md](file:///d:/PMLA-SCWE/documentation/PROJECT_MASTER_DOCUMENTATION.md)
> - Installation & Setup: [INSTALLATION_AND_SETUP.md](file:///d:/PMLA-SCWE/documentation/INSTALLATION_AND_SETUP.md)
> - Main Overview: [README.md](file:///d:/PMLA-SCWE/README.md)

---

## 📋 Prerequisites
Before you start, make sure you have:
1. **VS Code** installed on the target PC.
2. **Python 3.x** installed. (Ensure you check the box **"Add Python to PATH"** during installation).
3. **MySQL Server & MySQL Workbench** (optional - if you want to use the MySQL server instead of the automatic SQLite database fallback).

---

## 🚀 Step-by-Step Setup

Choose one of the following three options to get PMLA-SCWE running on your target machine.

---

### Option 1 — Recommended: Automated Setup (Online)
If your computer has an active internet connection, you can set up and run the entire project in a single step:

1. **Open the project folder** in VS Code (**File -> Open Folder...** and select `PMLA-SCWE`).
2. **Open a terminal** or your system file manager.
3. Run the automated script:
   - **Windows**: Double-click `setup_and_run.bat` (or run `./setup_and_run.bat` in terminal).
   - **macOS/Linux**: Run `./setup_and_run.sh` in terminal (ensure executable permissions: `chmod +x setup_and_run.sh`).
4. **Follow the on-screen prompts**:
   - The script will automatically check Python, create a virtual environment (`.venv`), install all required dependencies (caching them so it only downloads them once), run database schema diagnostics, create the default admin (`admin` / `admin123`), and prompt you to launch either the **Desktop GUI** or **Flask Web Server**.

---

### Option 2: Automated Setup (Offline / Evaluator Machine)
If the target computer (e.g. the evaluator's system) has no internet connection, you can pre-download the requirements on another machine:

1. **On a machine WITH internet**:
   - Open terminal in the project folder and run `download_wheels.bat` (Windows) or `./download_wheels.sh` (macOS/Linux).
   - This downloads all required package installers (wheels) into a folder named `wheels`.
   - Copy the entire project folder (now containing the `wheels` directory) onto your USB drive.
2. **On the OFFLINE machine**:
   - Copy the project folder from your USB drive to the target computer.
   - Run `setup_and_run.bat` (Windows) or `./setup_and_run.sh` (macOS/Linux).
   - The setup script will detect the `wheels` directory and install all packages offline without internet!

---

### Option 3: Manual Installation (Advanced Fallback)
If you prefer to perform the setup commands step-by-step:

1. **Create the Virtual Environment**:
   ```powershell
   python -m venv .venv
   ```
2. **Activate the Virtual Environment**:
   - Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
   - Windows (Cmd): `.\.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
3. **Install Dependencies**:
   - **Online**: `pip install -r requirements.txt`
   - **Offline**: `pip install --no-index --find-links=./wheels -r requirements.txt`
4. **Initialize & Seed Database**:
   ```powershell
   python seed_database.py
   ```
   *Note: Add `--reset` if you wish to wipe the database and generate 100 mock students.*
5. **Run the Application**:
   - To launch **Desktop GUI**: `python main.py`
   - To launch **Flask Web Server**: `python main.py --web`

---

## 🛠️ Troubleshooting & Common Setup Problems

### Problem 1: 'python' is not recognized as an internal or external command
* **Solution**: Re-run the Python installer, check **"Add Python to PATH"**, and complete installation, or manually add Python to system Environment Variables.

### Problem 2: Script execution is disabled on this system (VENV Activation Error)
* **Solution**: Run this command in PowerShell as Administrator to enable script execution:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```

### Problem 3: Platform-Specific Wheels Warning
* **Warning**: Offline wheel packages should ideally be downloaded on the same operating system and Python version where the application will be installed. If you are downloading wheels for an offline Windows machine, make sure to run `download_wheels.bat` on a Windows machine.

