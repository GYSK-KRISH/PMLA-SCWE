@echo off
setlocal enabledelayedexpansion

:: Find script directory for absolute path navigation
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ==================================================
echo   PMLA-SCWE OFFLINE PACKAGE WHEELS DOWNLOADER
echo ==================================================
echo This script downloads all required Python dependencies into
echo a local "wheels" folder for offline installation on computers
echo without internet access.
echo.
echo Target folder: %SCRIPT_DIR%wheels
echo ==================================================
pause

:: 1. Verify Python installation
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
    echo Please install Python and check the "Add Python to PATH" box.
    pause
    exit /b 1
)

:: 2. Create wheels directory if missing
if not exist "%SCRIPT_DIR%wheels" mkdir "%SCRIPT_DIR%wheels"

:: 3. Upgrade pip and download dependencies
echo.
echo [INFO] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip --quiet

echo.
echo [INFO] Downloading dependency wheels to %SCRIPT_DIR%wheels...
%PYTHON_CMD% -m pip download -r requirements.txt -d "%SCRIPT_DIR%wheels"

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [SUCCESS] All packages downloaded to "%SCRIPT_DIR%wheels".
    echo.
    echo OFFLINE DEPLOYMENT INSTRUCTIONS:
    echo 1. Copy this entire project directory (including the 'wheels'
    echo    folder and 'pmla_scwe_fallback.db') to a USB flash drive.
    echo 2. Paste the folder onto the offline computer.
    echo 3. Run 'setup_and_run.bat' on the offline computer.
    echo    The launcher will automatically install packages from 'wheels'.
    echo ==================================================
) else (
    echo.
    echo [ERROR] Failed to download package wheels.
    echo Please verify your internet connection and retry.
)

pause
