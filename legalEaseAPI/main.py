"""FastAPI entry point.

Run from the project root:
    uvicorn legalEaseAPI.main:app --reload
"""
import logging
import sys
from pathlib import Path

# Make the project root importable (config.py, ai_core/) however the app is launched.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI  # noqa: E402

from legalEaseAPI.routes import router  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="LegalEase - AI Legal Document Generator")

# Include API routes
app.include_router(router)


# Root endpoint (health-check)
@app.get("/")
def home():
    return {"message": "Welcome to LegalEase AI Legal Document Generator API"}


# Run FastAPI if executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
