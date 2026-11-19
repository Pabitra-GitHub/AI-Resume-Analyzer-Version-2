#!/usr/bin/env bash

# =======================================================
#    AI-Powered Resume & ATS Analyzer (Resume Intelligence)
#    macOS & Linux One-Click Setup & Launch Script
# =======================================================

set -e

echo "======================================================="
echo "   AI-Powered Resume & ATS Analyzer (Resume Intelligence)"
echo "======================================================="
echo ""

# 1. Detect Python 3
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python detected: $($PY_CMD --version)"
echo ""

# 2. Check and copy .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[INFO] Creating .env from .env.example..."
        cp .env.example .env
        echo "[OK] Created .env file."
    fi
fi

# 3. Create virtual environment if missing
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
    echo "[OK] Virtual environment created."
fi

# 4. Activate virtual environment
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

# 5. Install dependencies
echo "[INFO] Installing / updating dependencies..."
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "[OK] Dependencies are ready."
echo ""

# 6. Launch application
echo "======================================================="
echo "[STARTING] Launching AI Resume Analyzer..."
echo "Open your browser at: http://localhost:7860"
echo "(Press Ctrl+C to stop the application)"
echo "======================================================="
echo ""

# Try to open default browser in background
if command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://localhost:7860) &
elif command -v open &>/dev/null; then
    (sleep 2 && open http://localhost:7860) &
fi

python app.py
