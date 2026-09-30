"""Central configuration for LegalEase.

All settings can be overridden through environment variables or the .env file
that lives next to this file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True, encoding="utf-8-sig")

# --------------------------------------------------------------------------- #
# Gemini
# --------------------------------------------------------------------------- #
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()

# NOTE: the project brief mentions "gemini-1.5-pro". Google retired the 1.5
# family (and the 2.5 family is being shut down as well), so the default is a
# current model. Change it in .env (GEMINI_MODEL=...) whenever Google
# publishes a newer one. See https://ai.google.dev/gemini-api/docs/models
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview").strip()

# Tried in order if the primary model is unavailable (404 / quota / overload).
GEMINI_FALLBACK_MODELS: list[str] = [
    m.strip()
    for m in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.1-pro-preview,gemini-3.1-flash-lite-preview",
    ).split(",")
    if m.strip()
]

GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "120"))
GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "2"))

# --------------------------------------------------------------------------- #
# App / branding
# --------------------------------------------------------------------------- #
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

IMAGE_DIR = BASE_DIR / "Image"
LOGO_PATH = IMAGE_DIR / "Logo.png"                 # dark logo -> DOCX / PDF
WEB_LOGO_PATH = IMAGE_DIR / "inverseLogo.png"      # light logo -> dark web UI

APP_NAME = "LegalEase"
FOOTER_TEXT: str = os.getenv(
    "FOOTER_TEXT",
    "LegalEase Inc. | contact@legalease.com | All Rights Reserved.",
)
