#!/bin/bash
# ULTIMATE E-COMMERCE PLATFORM - Run Script
# Builds and runs all 7 platform variants

set -e

PLATFORM=${1:-ULTIMATE}

echo "=========================================="
echo "ULTIMATE E-COMMERCE PLATFORM"
echo "Platform: $PLATFORM"
echo "=========================================="

cd "$(dirname "$0")"

# Backend
echo "[1/4] Installing Python dependencies..."
python3 -m pip install -r requirements.txt -q

echo "[2/4] Initializing database..."
python3 -c "from backend.database import init_db; init_db(); print('Database initialized!')"

echo "[3/4] Starting backend (uvicorn)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "[4/4] Frontend..."
cd frontend
npm install --silent 2>/dev/null || true
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "DONE! Access:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Platform: $PLATFORM"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop"

# Wait
wait
