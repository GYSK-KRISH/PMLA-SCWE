@echo off
setlocal enabledelayedexpansion

:: Find script directory for absolute path navigation
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ==================================================
echo         PMLA-SCWE AUTOMATED LAUNCHER
echo ==================================================

:: 1. Verify Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python and check the "Add Python to PATH" box.
    pause
    exit /b 1
)

:: 2. Verify Python version (requires Python 3)
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PMLA-SCWE requires Python 3.x to run.
    pause
    exit /b 1
)

:: 3. Setup Virtual Environment if missing
if not exist "%SCRIPT_DIR%.venv" (
    echo [INFO] Virtual environment not found. Creating .venv...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [PASS] Virtual environment created.
)

:: 4. Activate Virtual Environment
echo [INFO] Activating virtual environment...
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 5. Check dependencies against requirements.installed marker using SHA-256
set INSTALL_DEPS=0
python -c "import hashlib, sys; from pathlib import Path; r=Path('requirements.txt'); m=Path('.venv/requirements.installed'); sys.exit(0 if r.exists() and m.exists() and m.read_text().strip() == hashlib.sha256(r.read_bytes()).hexdigest() else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] requirements.txt is updated or marker is missing. Re-evaluating dependencies...
    set INSTALL_DEPS=1
)

if %INSTALL_DEPS%==0 goto :deps_done

echo [INFO] Installing required dependencies...

if exist "%SCRIPT_DIR%wheels" goto :offline_install

:online_install
echo [INFO] Attempting online installation...
python -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)
goto :write_marker

:offline_install
echo [INFO] Local offline package directory "wheels" found.
echo [INFO] Attempting offline installation...
python -m pip install --no-index --find-links="%SCRIPT_DIR%wheels" -r requirements.txt
if !errorlevel! == 0 goto :write_marker

echo [WARN] Offline installation failed. Offline packages may be incomplete or platform-mismatched.
set /p online_choice="Would you like to attempt online installation via internet? [Y/N]: "
if /i "!online_choice!"=="Y" goto :online_install
echo [ERROR] Cannot proceed without installing required packages.
pause
exit /b 1

:write_marker
python -c "import hashlib; from pathlib import Path; Path('.venv/requirements.installed').write_text(hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest())" >nul 2>&1
echo [PASS] Package installation succeeded.

:deps_done

:: 6. Perform idempotent database initialization/seeding
echo [INFO] Verifying database schema and initial data...
python "%SCRIPT_DIR%seed_database.py"
if %errorlevel% neq 0 (
    echo [WARN] Database verification returned warning code: %errorlevel%
)

:: 7. Mode Selection Menu with Timeout
echo.
echo ==================================================
echo         PMLA-SCWE APPLICATION LAUNCHER
echo ==================================================
echo.
echo 1. Desktop PySide6 Client (Default)
echo 2. Flask Web Server
echo.
choice /c 12 /t 10 /d 1 /m "Select application mode (Auto-launches Desktop in 10s)"

if %errorlevel% == 2 (
    echo [INFO] Launching Flask Web Server...
    python "%SCRIPT_DIR%main.py" --web
) else (
    echo [INFO] Launching Desktop GUI Client...
    python "%SCRIPT_DIR%main.py"
)

pause
