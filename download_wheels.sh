#!/usr/bin/env bash
# ==============================================================================
#  PMLA-SCWE OFFLINE PACKAGE WHEELS DOWNLOADER (Linux & macOS)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "   PMLA-SCWE OFFLINE PACKAGE WHEELS DOWNLOADER"
echo "=================================================="
echo "This script downloads all required Python dependencies into"
echo "a local 'wheels' folder for offline installation on computers"
echo "without internet access."
echo ""
echo "Target folder: $SCRIPT_DIR/wheels"
echo "=================================================="
read -p "Press Enter to continue..."

# 1. Identify Python 3 interpreter
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi

# 2. Create wheels folder if missing
mkdir -p "$SCRIPT_DIR/wheels"

# 3. Upgrade pip and download dependency wheels
echo ""
echo "[INFO] Downloading dependency wheels to $SCRIPT_DIR/wheels..."
$PYTHON_BIN -m pip download -r requirements.txt -d "$SCRIPT_DIR/wheels"

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "[SUCCESS] All packages downloaded to '$SCRIPT_DIR/wheels'."
    echo ""
    echo "OFFLINE DEPLOYMENT INSTRUCTIONS:"
    echo "1. Copy this entire project directory (including the 'wheels'"
    echo "   folder and 'pmla_scwe_fallback.db') to a USB flash drive."
    echo "2. Paste the folder onto the offline computer."
    echo "3. Run './setup_and_run.sh' on the offline computer."
    echo "   The launcher will automatically install packages from 'wheels'."
    echo "=================================================="
else
    echo ""
    echo "[ERROR] Failed to download package wheels."
    echo "Please verify your internet connection and retry."
    exit 1
fi
