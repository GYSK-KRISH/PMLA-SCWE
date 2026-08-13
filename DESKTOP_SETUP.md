# PMLA-SCWE: Desktop Computer Installation & Setup Guide

This guide provides step-by-step instructions to get the **PMLA-SCWE** application up and running on a computer (running Windows and VS Code) from scratch.

---

## 📋 Prerequisites
Before you start, make sure you have:
1. **VS Code** installed on the target PC.
2. **Python 3.x** installed. (Ensure you check the box **"Add Python to PATH"** during installation).
3. **MySQL Server & MySQL Workbench** (optional - if you want to use the MySQL server instead of the automatic SQLite database fallback).

---

## 🚀 Step-by-Step Setup

### Step 1: Open the Project in VS Code
1. Transfer the project folder to the target computer via USB drive (or clone it from git).
2. Open **VS Code**.
3. Go to **File -> Open Folder...** and select the `PMLA-SCWE` folder.

---

### Step 2: Set Up the Python Virtual Environment (VENV)
1. **Open the Integrated Terminal** in VS Code (Press `Ctrl + Shift + ~` or go to **Terminal -> New Terminal**).
2. **Create the VENV**:
   Run this command in the terminal to create a virtual environment folder named `.venv`:
   ```powershell
   python -m venv .venv
   ```
3. **Configure VS Code Python Interpreter**:
   - Open the VS Code Command Palette: `Ctrl + Shift + P`.
   - Type `Python: Select Interpreter` and press `Enter`.
   - Choose the interpreter that points to your virtual environment: `('venv': .venv\Scripts\python.exe)`.
4. **Activate the VENV**:
   - Close the current terminal in VS Code (click the trash bin icon).
   - Open a **New Terminal** (`Ctrl + Shift + ~`). VS Code will automatically detect the select interpreter and activate VENV. You will see `(.venv)` displayed at the start of your command prompt.
   - *If activation fails because of Windows execution policies, run this command in PowerShell to bypass the restriction, then restart your terminal*:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     ```
     *Then run*:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```

---

### Step 3: Install Required Dependencies

#### Scenario A: The PC has Internet Connection
Run the following command in your activated terminal:
```powershell
pip install -r requirements.txt
```

#### Scenario B: The PC is OFFLINE (No Internet)
If the target PC has no internet connection, download wheels on a machine with internet and install them on the offline machine:
1. **On the machine with internet**: Open terminal in your project directory and download packages to a local `wheels` folder:
   ```powershell
   pip download -r requirements.txt -d ./wheels
   ```
   Copy the entire `wheels/` folder to your USB drive along with the project.
2. **On the offline PC**: Plug in your USB, open the terminal in the project directory, and install using the downloaded wheels:
   ```powershell
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```

---

### Step 4: Configure MySQL Database (Optional)

If the target computer has a MySQL installation, follow these steps to link the project:
1. **Install MySQL Community Server & Workbench** if they aren't already installed.
2. **Start the MySQL Service**:
   - Open Windows **Services** (`services.msc`).
   - Scroll down to find **MySQL80** (or similar).
   - Right-click it and click **Start**.
3. **Initialize the Schema**:
   - Open **MySQL Workbench**.
   - Connect to your local server connection (`localhost:3306`).
   - Click **File -> Open SQL Script...** and select `schema.sql` located in the root of your project folder.
   - Click the **lightning bolt icon** at the top of Workbench to execute the script. This creates the database `pmla_scwe` and all tables.
4. **Update Project Configuration**:
   - Open [core/config.py](file:///d:/PMLA-SCWE/core/config.py) in VS Code.
   - Update `DATABASE_CONFIG` to match your local MySQL server password and port:
     ```python
     DATABASE_CONFIG = {
         "host": "localhost",
         "user": "root",
         "password": "your_local_mysql_password",  # Modify this!
         "database": "pmla_scwe",
         "port": 3306,
     }
     ```

*Note: If MySQL is not installed or refuses to connect, the application will automatically fall back to using SQLite in `pmla_scwe_fallback.db`, allowing you to run and present your project offline without any MySQL issues!*

---

### Step 5: Run Setup Diagnostics 🔍
We have provided a diagnostics script `diagnose_setup.py` at the root of the project to verify your environment. Run it to detect and resolve errors immediately:

1. In your activated terminal, run:
   ```powershell
   python diagnose_setup.py
   ```
2. The script runs a 5-stage setup verification:
   - [1/5] Python environment status
   - [2/5] Dependencies status
   - [3/5] Database configuration
   - [4/5] Database connection (MySQL port 3306 & SQLite fallback)
   - [5/5] Database schema (verifying all 12 tables)
3. If diagnostics pass successfully, it will print a summary with green checks.

---

### Step 6: Seed Database & Run App
Once diagnostics pass:
1. **Load mock data** (100 students + test logs):
   ```powershell
   python seed_data.py
   ```
2. **Start the application**:
   - To launch the **Desktop GUI**:
     ```powershell
     python main.py
     ```
   - To launch the **Flask Web Server**:
     ```powershell
     python main.py --web
     ```

---

## 🛠️ Troubleshooting & Common Setup Problems

### Problem 1: 'python' is not recognized as an internal or external command
* **Solution**: Re-run the Python installer, check **"Add Python to PATH"**, and complete installation, or manually add Python to system Environment Variables.

### Problem 2: Red VENV Activation Error (`Script execution is disabled on this system`)
* **Solution**: Change your default terminal in VS Code to Command Prompt (`cmd`) and activate VENV using:
  ```cmd
  .venv\Scripts\activate.bat
  ```

### Problem 3: `ModuleNotFoundError`
* **Solution**: Always run commands from the project root and ensure the virtual environment `(.venv)` is active.
