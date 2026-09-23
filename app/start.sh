#!/bin/bash
# ============================================================
# Streaming Live RAG — Samsung PRISM Hackathon · Theme 04
# Unified startup script: launches FastAPI backend + Next.js frontend
# ============================================================
# Usage:
#   ./start.sh          # Start both backend and frontend (default)
#   ./start.sh backend  # Start backend only
#   ./start.sh frontend # Start frontend only
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=========================================================="
echo "  Samsung PRISM GenAI Hackathon (3rd Edition) · Theme 04  "
echo "  Streaming Live RAG — Full-Duplex Conversational Engine   "
echo "=========================================================="
echo ""

case "${1:-both}" in
  b|backend)
    echo "[1/1] Starting Backend on http://localhost:8000 ..."
    cd "$BACKEND_DIR"
    PYTHONPATH="$BACKEND_DIR" "$BACKEND_DIR/backend-venv/bin/python3" -m src --host 0.0.0.0 --port 8000
    ;;
  f|frontend)
    echo "[1/1] Starting Frontend on http://localhost:3000 ..."
    cd "$FRONTEND_DIR"
    npm run start -- -p 3000
    ;;
  *)
    echo "[1/2] Starting FastAPI Backend on http://localhost:8000 ..."
    cd "$BACKEND_DIR"
    PYTHONPATH="$BACKEND_DIR" "$BACKEND_DIR/backend-venv/bin/python3" -m src --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    # Wait for backend health
    echo "      Waiting for backend to initialize..."
    for i in $(seq 1 30); do
      if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "      ✓ Backend healthy and ready (PID: $BACKEND_PID)"
        break
      fi
      sleep 1
    done

    echo ""
    echo "[2/2] Starting Next.js Production Frontend on http://localhost:3000 ..."
    cd "$FRONTEND_DIR"
    npm run start -- -p 3000 &
    FRONTEND_PID=$!

    # Wait for frontend
    echo "      Waiting for frontend..."
    for i in $(seq 1 30); do
      if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
        echo "      ✓ Frontend healthy and ready (PID: $FRONTEND_PID)"
        break
      fi
      sleep 1
    done

    echo ""
    echo "=========================================================="
    echo "  🚀 ALL SERVICES OPERATIONAL"
    echo "=========================================================="
    echo "  • Web Application: http://localhost:3000"
    echo "  • FastAPI Backend: http://localhost:8000"
    echo "  • Swagger API Docs: http://localhost:8000/docs"
    echo "  • Telemetry HUD:   http://localhost:8000/api/telemetry"
    echo "=========================================================="
    echo "  Press Ctrl+C to gracefully shut down."
    echo ""

    trap 'echo ""; echo "Shutting down services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' SIGINT SIGTERM
    wait
    ;;
esac
