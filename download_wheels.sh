#!/usr/bin/env bash
# Determine script directory to ensure relative execution works
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo " PMLA-SCWE Offline Wheels Downloader"
echo "=================================================="
echo "This script downloads all required Python packages into the 'wheels' folder."
echo "You MUST have an active internet connection to run this."
echo ""
echo "Target folder: $SCRIPT_DIR/wheels"
echo "=================================================="
read -p "Press Enter to continue..."

# Verify Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi

mkdir -p wheels

echo "[INFO] Downloading packages to wheels..."
python3 -m pip download -r requirements.txt -d wheels

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Packages downloaded successfully to the 'wheels' directory."
    echo "Copy this entire project directory to the offline computer."
else
    echo ""
    echo "[ERROR] Failed to download package wheels. Please check your internet connection."
fi
