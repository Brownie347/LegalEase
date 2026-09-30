#!/usr/bin/env bash
# Start backend (port 8000) and frontend (port 8501). Works on macOS/Linux/Git-Bash.
set -e
cd "$(dirname "$0")"

if [ -f venv/bin/activate ]; then source venv/bin/activate
elif [ -f venv/Scripts/activate ]; then source venv/Scripts/activate
fi

uvicorn legalEaseAPI.main:app --reload --port 8000 &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null' EXIT

streamlit run frontend/app.py --server.port 8501
