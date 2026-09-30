from fastapi.testclient import TestClient

from ai_core.gemini_generator import GenerationError, MissingAPIKeyError
from legalEaseAPI import routes
from legalEaseAPI.main import app

client = TestClient(app)
PAYLOAD = {"document_type": "NDA", "parties": "A (Disclosing), B (Receiving)", "terms": "x; y", "dates": "May 1, 2026"}


class FakeGen:
    def generate_document(self, document_type, parties, terms, dates):
        return f"DOC for {document_type} / {parties} / {terms} / {dates}"


def test_root_and_health():
    assert client.get("/").json() == {"message": "Welcome to LegalEase AI Legal Document Generator API"}
    assert client.get("/health").json() == {"status": "ok"}


def test_generate_ok(monkeypatch):
    monkeypatch.setattr(routes, "get_generator", lambda: FakeGen())
    r = client.post("/generate", json=PAYLOAD)
    assert r.status_code == 200
    assert r.json()["document"].startswith("DOC for NDA")


def test_generate_validation():
    r = client.post("/generate", json={"document_type": "", "parties": ""})
    assert r.status_code == 422


def test_generate_missing_key(monkeypatch):
    def boom():
        raise MissingAPIKeyError("GEMINI_API_KEY is not set")
    monkeypatch.setattr(routes, "get_generator", boom)
    r = client.post("/generate", json=PAYLOAD)
    assert r.status_code == 500 and "GEMINI_API_KEY" in r.json()["detail"]


def test_generate_model_failure(monkeypatch):
    class Bad:
        def generate_document(self, *a):
            raise GenerationError("all models failed")
    monkeypatch.setattr(routes, "get_generator", lambda: Bad())
    r = client.post("/generate", json=PAYLOAD)
    assert r.status_code == 502 and "all models failed" in r.json()["detail"]
