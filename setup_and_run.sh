#!/usr/bin/env bash
# ==============================================================================
#  PMLA-SCWE AUTOMATED SETUP & LAUNCHER (Linux & macOS)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "         PMLA-SCWE AUTOMATED LAUNCHER"
echo "=================================================="

# 1. Auto-create .env from .env.example if missing
if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    echo "[INFO] .env not found. Initializing from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "[PASS] Created .env configuration file."
fi

# 2. Identify Python 3 interpreter
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.10+ (e.g. 'sudo apt install python3 python3-venv python3-pip')."
    exit 1
fi

# Verify Python version >= 3.10
$PYTHON_BIN -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || {
    echo "[ERROR] PMLA-SCWE requires Python 3.10 or higher."
    exit 1
}

# 3. Create virtual environment if missing
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "[INFO] Virtual environment not found. Creating .venv..."
    $PYTHON_BIN -m venv "$SCRIPT_DIR/.venv"
    echo "[PASS] Virtual environment created."
fi

# 4. Activate virtual environment
# shellcheck source=/dev/null
source "$SCRIPT_DIR/.venv/bin/activate"

# 5. Check and install dependencies
INSTALL_DEPS=0
if ! python -c "import hashlib, sys; from pathlib import Path; r=Path('requirements.txt'); m=Path('.venv/requirements.installed'); sys.exit(0 if r.exists() and m.exists() and m.read_text().strip() == hashlib.sha256(r.read_bytes()).hexdigest() else 1)" 2>/dev/null; then
    INSTALL_DEPS=1
fi

if [ "$INSTALL_DEPS" -eq 1 ]; then
    echo "[INFO] Installing/verifying package dependencies..."
    python -m pip install --upgrade pip --quiet 2>/dev/null || true

    if [ -d "$SCRIPT_DIR/wheels" ]; then
        echo "[INFO] Local offline package directory 'wheels' found."
        echo "[INFO] Attempting offline installation from local wheels..."
        if python -m pip install --no-index --find-links="$SCRIPT_DIR/wheels" -r requirements.txt; then
            python -c "import hashlib; from pathlib import Path; Path('.venv/requirements.installed').write_text(hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest())" 2>/dev/null || true
            echo "[PASS] Package installation verified from local wheels."
        else
            echo "[WARN] Offline install incomplete. Falling back to PyPI online installation..."
            python -m pip install -r requirements.txt
            python -c "import hashlib; from pathlib import Path; Path('.venv/requirements.installed').write_text(hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest())" 2>/dev/null || true
            echo "[PASS] Package installation verified."
        fi
    else
        echo "[INFO] Installing packages via pip..."
        python -m pip install -r requirements.txt
        python -c "import hashlib; from pathlib import Path; Path('.venv/requirements.installed').write_text(hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest())" 2>/dev/null || true
        echo "[PASS] Package installation verified."
    fi
fi

# 6. Idempotent Database Initialization & Seeding
echo "[INFO] Verifying database schema, tenant boundaries, and initial data..."
python "$SCRIPT_DIR/seed_database.py" || {
    echo "[WARN] Database verification returned warning."
}

# 7. Application Launch Menu
echo ""
echo "=================================================="
echo "         PMLA-SCWE APPLICATION LAUNCHER"
echo "=================================================="
echo ""
echo "1. Desktop PySide6 Client (Default)"
echo "2. Flask Web Server"
echo ""

# Read with 10 second timeout default to Option 1
read -t 10 -p "Select application mode [1,2] (Auto-launches Desktop in 10s): " choice || choice="1"
echo ""

case "$choice" in
    2)
        echo "[INFO] Launching Flask Web Server at http://127.0.0.1:5000..."
        python "$SCRIPT_DIR/main.py" --web
        ;;
    *)
        echo "[INFO] Launching PySide6 Desktop GUI Client..."
        python "$SCRIPT_DIR/main.py"
        ;;
esac
