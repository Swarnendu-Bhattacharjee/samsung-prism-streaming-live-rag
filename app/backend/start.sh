#!/bin/bash
# Streaming Live RAG — Backend startup script
# Activates venv, loads demo corpus, starts FastAPI server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "  Streaming Live RAG — Backend"
echo "  Samsung Prism Hackathon · Theme 04"
echo "=============================================="
echo ""

# Activate virtual environment
if [ -f "$SCRIPT_DIR/backend-venv/bin/activate" ]; then
    source "$SCRIPT_DIR/backend-venv/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found at $SCRIPT_DIR/backend-venv"
    exit 1
fi

# Verify we're using the venv python
VENV_PYTHON="$SCRIPT_DIR/backend-venv/bin/python3"
if [ -x "$VENV_PYTHON" ]; then
    echo "✓ Using venv python: $VENV_PYTHON"
    PYTHON_CMD="$VENV_PYTHON"
else
    echo "✗ Venv python not found, falling back to system python"
    PYTHON_CMD="python3"
fi

# Start the server
echo ""
echo "Starting FastAPI server on http://localhost:8000 ..."
echo "API docs: http://localhost:8000/docs"
echo ""

exec $PYTHON_CMD -m src --host 0.0.0.0 --port 8000
