@echo off
REM Windows launcher: opens the backend in a second window, then starts the frontend.
cd /d "%~dp0"
call venv\Scripts\activate
start "LegalEase Backend" cmd /k "venv\Scripts\activate && uvicorn legalEaseAPI.main:app --reload --port 8000"
streamlit run frontend/app.py --server.port 8501
