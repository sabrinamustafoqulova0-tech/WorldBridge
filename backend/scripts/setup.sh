#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# WorldBridge Backend — Quick Setup Script (Git Bash / MINGW64)
# Run from: WorldBridge-backend/
# Usage: bash scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

PYTHON=""

echo "🔍 Looking for Python 3.10+..."

# Try common Windows Python locations
for candidate in \
    "/c/Python312/python.exe" \
    "/c/Python311/python.exe" \
    "/c/Python310/python.exe" \
    "/c/Users/$USERNAME/AppData/Local/Programs/Python/Python312/python.exe" \
    "/c/Users/$USERNAME/AppData/Local/Programs/Python/Python311/python.exe" \
    "/c/Users/$USERNAME/AppData/Local/Programs/Python/Python310/python.exe" \
    "python3" \
    "python"; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
        if [ "$ver" = "True" ]; then
            PYTHON="$candidate"
            echo "✅ Found Python: $PYTHON ($($PYTHON --version))"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "❌  Python 3.10+ not found."
    echo ""
    echo "👉  Install Python from: https://www.python.org/downloads/"
    echo "    ➡  During install: CHECK 'Add Python to PATH'"
    echo "    ➡  Then re-run this script."
    echo ""
    exit 1
fi

# ── Create virtual environment ────────────────────────────────────────────────
echo ""
echo "📦 Creating virtual environment..."
"$PYTHON" -m venv .venv
source .venv/Scripts/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

echo "📥 Installing dependencies..."
pip install -r requirements.txt

# ── Copy .env if not exists ───────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example"
else
    echo "ℹ️  .env already exists, skipping"
fi

# ── Seed the database ─────────────────────────────────────────────────────────
echo ""
echo "🌱 Seeding database with sample data..."
python scripts/seed.py

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  WorldBridge Backend is ready!                   ║"
echo "║                                                      ║"
echo "║  Start server:                                       ║"
echo "║    source .venv/Scripts/activate                     ║"
echo "║    uvicorn app.main:app --reload                     ║"
echo "║                                                      ║"
echo "║  API Docs: http://localhost:8000/docs                ║"
echo "╚══════════════════════════════════════════════════════╝"
