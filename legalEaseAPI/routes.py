"""API routes: request validation + document generation."""
from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import (
    GeminiDocumentGenerator,
    GenerationError,
    MissingAPIKeyError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=2000)
    terms: str = Field("", max_length=8000)
    dates: str = Field("", max_length=100)

    @field_validator("document_type", "parties", "terms", "dates", mode="before")
    @classmethod
    def _strip(cls, value):
        return value.strip() if isinstance(value, str) else value


@lru_cache(maxsize=1)
def get_generator() -> GeminiDocumentGenerator:
    """Created on first use so the server still starts without an API key."""
    return GeminiDocumentGenerator()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    try:
        generator = get_generator()
        response = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
    except MissingAPIKeyError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except GenerationError as exc:
        logger.error("Generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    return {"document": response}
