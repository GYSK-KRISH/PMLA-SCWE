@echo off
setlocal enabledelayedexpansion

:: Find script directory for absolute path navigation
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ==================================================
echo         PMLA-SCWE AUTOMATED LAUNCHER
echo ==================================================

:: 1. Auto-create .env configuration from template if missing
if not exist "%SCRIPT_DIR%.env" (
    if exist "%SCRIPT_DIR%.env.example" (
        echo [INFO] .env not found. Initializing from .env.example...
        copy "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
        echo [PASS] Created .env configuration file.
    )
)

:: 2. Verify Python installation (support python, py, python3)
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 set PYTHON_CMD=python

if "%PYTHON_CMD%"=="" (
    where py >nul 2>nul
    if %errorlevel% equ 0 set PYTHON_CMD=py -3
)

if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>nul
    if %errorlevel% equ 0 set PYTHON_CMD=python3
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and check the "Add Python to PATH" box.
    pause
    exit /b 1
)

:: 3. Verify Python version is 3.x
%PYTHON_CMD% -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PMLA-SCWE requires Python 3.x to run.
    pause
    exit /b 1
)

:: 4. Setup Virtual Environment if missing
if not exist "%SCRIPT_DIR%.venv" (
    echo [INFO] Virtual environment not found. Creating .venv...
    %PYTHON_CMD% -m venv "%SCRIPT_DIR%.venv"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [PASS] Virtual environment created.
)

:: 5. Activate Virtual Environment
echo [INFO] Activating virtual environment...
if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment activation script missing.
    pause
    exit /b 1
)

:: 6. Check dependencies against requirements.installed marker using SHA-256
set INSTALL_DEPS=0
python -c "import hashlib, sys; from pathlib import Path; r=Path('requirements.txt'); m=Path('.venv/requirements.installed'); sys.exit(0 if r.exists() and m.exists() and m.read_text().strip() == hashlib.sha256(r.read_bytes()).hexdigest() else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Evaluating and installing required dependencies...
    set INSTALL_DEPS=1
)

if %INSTALL_DEPS%==0 goto :deps_done

echo [INFO] Ensuring pip is up to date...
python -m pip install --upgrade pip --quiet >nul 2>&1

if exist "%SCRIPT_DIR%wheels" goto :offline_install

:online_install
echo [INFO] Installing packages via pip...
python -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)
goto :write_marker

:offline_install
echo [INFO] Local offline package directory "wheels" found.
echo [INFO] Attempting offline installation from local wheels...
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
echo [PASS] Package installation verified.

:deps_done

:: 7. Perform idempotent database initialization/seeding
echo [INFO] Verifying database schema, tenant boundaries, and initial data...
python "%SCRIPT_DIR%seed_database.py"
if %errorlevel% neq 0 (
    echo [WARN] Database verification returned warning code: %errorlevel%
)

:: 8. Mode Selection Menu with Timeout
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
