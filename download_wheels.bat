@echo off
:: Find script directory for absolute path navigation
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ==================================================
echo PMLA-SCWE Offline Wheels Downloader
echo ==================================================
echo This script downloads all required Python packages into the "wheels" folder.
echo You MUST have an active internet connection to run this.
echo.
echo Target folder: %SCRIPT_DIR%wheels
echo ==================================================
pause

:: Verify Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python and check the "Add Python to PATH" box.
    pause
    exit /b 1
)

:: Create wheels directory if it doesn't exist
if not exist wheels mkdir wheels

echo [INFO] Downloading packages to wheels...
python -m pip download -r requirements.txt -d wheels

if %errorlevel% eq 0 (
    echo.
    echo [SUCCESS] Packages downloaded successfully to the "wheels" directory.
    echo Copy this entire project directory to the offline computer.
) else (
    echo.
    echo [ERROR] Failed to download package wheels. Please check your internet connection.
)

pause
