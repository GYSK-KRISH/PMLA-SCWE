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

### Step 1: Clone the GitHub Repository
1. Open the Windows Command Prompt (`cmd`) or PowerShell.
2. Navigate to your desktop or desired folder:
   ```cmd
   cd C:\Users\YourUsername\Desktop
   ```
3. Clone the project using Git:
   ```cmd
   git clone https://github.com/your-username/PMLA-SCWE.git
   ```
   *(If Git is not installed on the target computer, download the project as a `.ZIP` file from GitHub, copy it via a USB drive, and extract it on your PC).*

4. Open the extracted folder in **VS Code**:
   - Open VS Code.
   - Go to **File -> Open Folder...**
   - Select the `PMLA-SCWE` folder.

---

### Step 2: Set Up the Python Virtual Environment (VENV)
Virtual environments keep your dependencies isolated. Here is how to configure VENV inside VS Code on Windows:

1. **Open the Integrated Terminal** in VS Code (Press `Ctrl + Shift + ~` or go to **Terminal -> New Terminal**).
2. **Create the VENV**:
   Run this command in the terminal to create a virtual environment folder named `.venv`:
   ```powershell
   python -m venv .venv
   ```
   *Tip: If you encounter compiler errors (such as a `meson setup` failure when installing `pandas`) because the target PC lacks build tools, recreate your VENV with the `--system-site-packages` flag so it inherits working global Python libraries:*
   ```powershell
   python -m venv .venv --system-site-packages
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
   - Open the Windows search box, search for **Services**, and open it.
   - Scroll down to find **MySQL80** (or similar).
   - If its status is not "Running", right-click it and click **Start**.
3. **Initialize the Schema**:
   - Open **MySQL Workbench**.
   - Connect to your local server connection (`localhost:3306`).
   - Click **File -> Open SQL Script...** and select `schema.sql` located in the root of your project folder.
   - Click the **lightning bolt icon** at the top of Workbench to execute the script. This creates the database `pmla_scwe` and all tables.
4. **Update Project Configuration**:
   - Open [PMLA_SCWE/config.py](file:///d:/PMLA-SCWE/PMLA_SCWE/config.py) in VS Code.
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

*Note: If MySQL is not installed or refuses to connect, the application will automatically fall back to using SQLite in `pmla_scwe_fallback.db`, allowing you to present your project offline without any MySQL issues!*

---

### Step 5: Run Setup Diagnostics 🔍
We have provided a powerful diagnostics script `diagnose_setup.py` at the root of the project to help you verify your environment. Run it to detect and resolve errors immediately:

1. In your activated terminal, run:
   ```powershell
   python diagnose_setup.py
   ```
2. The script will check:
   - Python installation and environment status.
   - VENV activation.
   - All library dependencies.
   - MySQL service connection on port 3306.
   - Database schema status and table structures.
   - SQLite fallback write/read permissions.
3. If there are any errors, the script will show red `[FAIL]` markers with exact **"ACTION REQUIRED"** troubleshooting steps to resolve them.

---

### Step 6: Seed Database & Run App
Once diagnostics pass with a green or yellow status:
1. **Load mock data** (100 students + test logs):
   ```powershell
   python -m PMLA_SCWE.seed_data
   ```
2. **Start the application**:
   ```powershell
   python -m PMLA_SCWE.main
   ```

---

## 🛠️ Troubleshooting & Common Setup Problems

Here are detailed instructions to solve any error or issue you might face during setup:

### Problem 1: 'python' is not recognized as an internal or external command
* **Cause**: Python was not added to the Windows environment PATH variables during installation.
* **Solution**:
  1. Open the Windows search bar, type **"environment variables"**, and select **"Edit the system environment variables"**.
  2. Click the **"Environment Variables..."** button at the bottom.
  3. Under "User variables", select **Path** and click **Edit...**
  4. Click **New** and add the path to your Python installation directory (e.g., `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\`).
  5. Click **New** again and add the path to the Scripts directory (e.g., `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\Scripts\`).
  6. Click **OK** on all windows, close your current command prompts/VS Code, and open a new terminal.

---

### Problem 2: Red VENV Activation Error (`Script execution is disabled on this system`)
* **Cause**: Windows PowerShell default security settings restrict running scripts (like the VENV activation script).
* **Solution**:
  - **Option A (Bypass in PowerShell)**: Run this command in your VS Code terminal to bypass execution policy restrictions for the current terminal session, then activate:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .\.venv\Scripts\Activate.ps1
    ```
  - **Option B (Use Command Prompt)**: Change your default shell in VS Code to Command Prompt (`cmd`). Go to the terminal dropdown arrow in VS Code, choose **"Select Default Profile"**, select **"Command Prompt"**, open a new terminal, and run:
    ```cmd
    .venv\Scripts\activate.bat
    ```

---

### Problem 3: `ModuleNotFoundError: No module named 'PMLA_SCWE'`
* **Cause**: Running Python scripts directly (e.g., clicking F5 or running `python main.py` inside the package directory) breaks relative package imports.
* **Solution**:
  - **Always run from the root folder** of the project (one level above `PMLA_SCWE`).
  - **Always run using the module flag (`-m`)**:
    ```powershell
    python -m PMLA_SCWE.main
    ```

---

### Problem 4: `ModuleNotFoundError: No module named 'pandas'` (or other libraries)
* **Cause**: Either your VENV is not active, or you installed packages globally instead of inside the VENV.
* **Solution**:
  1. Check the left side of your terminal line. It must show `(.venv)` in parenthesis.
  2. If it is active but the error persists, install the dependencies again:
     ```powershell
     pip install -r requirements.txt
     ```
  3. Run `python diagnose_setup.py` to see a detailed report of which dependencies are missing.

---

### Problem 5: Meson Build / C++ Compiler Error during `pip install pandas`
* **Cause**: Installing packages on new/unreleased Python versions (like Python 3.14+) requires compiling C++ libraries from source if binary wheels aren't published on PyPI.
* **Solution**:
  - Re-create your virtual environment with `--system-site-packages` so that the virtual environment inherits packages already installed on your global Python system:
    ```powershell
    rmdir /s /q .venv
    python -m venv .venv --system-site-packages
    ```

---

### Problem 6: MySQL Database Authentication Failures (`Access denied for user...`)
* **Cause**: The password configured in [PMLA_SCWE/config.py](file:///d:/PMLA-SCWE/PMLA_SCWE/config.py) does not match the MySQL Server root password of the current PC.
* **Solution**:
  1. Open [PMLA_SCWE/config.py](file:///d:/PMLA-SCWE/PMLA_SCWE/config.py) in VS Code.
  2. Modify the `password` field in `DATABASE_CONFIG` to match your local password.
  3. Run `python diagnose_setup.py` to confirm that authentication passes.

---

### Problem 7: Speech Recognition / PyAudio Install Failures
* **Cause**: `PyAudio` is an optional dependency required for voice command capture, but it can be difficult to install on some Windows PCs without compilers.
* **Solution**:
  - The application is designed to catch voice errors gracefully. If you select Option 8 -> Voice command, it will print a warning and fall back to manual text input.
  - To install `PyAudio` manually:
    ```powershell
    pip install pyaudio
    ```
    If that fails, you can rely entirely on the text-to-speech fallback, which works out of the box!

