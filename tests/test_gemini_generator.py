import pytest
from google.genai import errors

import config
from ai_core import gemini_generator as gg


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.candidates = []


class FakeModels:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.calls = []

    def generate_content(self, model, contents, config):
        self.calls.append(model)
        result = self.behaviour(model)
        if isinstance(result, Exception):
            raise result
        return FakeResponse(result)


def make_generator(behaviour, monkeypatch, models=("m1", "m2")):
    monkeypatch.setattr(gg.time, "sleep", lambda *_: None)
    gen = gg.GeminiDocumentGenerator(
        model_name=models[0], api_key="test-key", fallback_models=list(models[1:]), max_retries=1
    )
    fake = FakeModels(behaviour)
    gen.client = type("FakeClient", (), {"models": fake})()
    return gen


def api_error(code, msg="boom", status="ERR"):
    cls = errors.ClientError if code < 500 else errors.ServerError
    return cls(code, {"error": {"code": code, "message": msg, "status": status}})


def test_missing_key(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    with pytest.raises(gg.MissingAPIKeyError):
        gg.GeminiDocumentGenerator()


def test_placeholder_key_is_rejected():
    with pytest.raises(gg.MissingAPIKeyError):
        gg.GeminiDocumentGenerator(api_key="your_api_key_here")


def test_prompt_contains_inputs():
    prompt = gg.GeminiDocumentGenerator.build_prompt("NDA", "A and B", "x; y", "1 Jan 2026")
    assert "'NDA'" in prompt and "A and B" in prompt and "- x" in prompt and "- y" in prompt


def test_success(monkeypatch):
    gen = make_generator(lambda m: "  Hello doc  ", monkeypatch)
    assert gen.generate_document("NDA", "A, B", "", "") == "Hello doc"


def test_falls_back_on_404(monkeypatch):
    gen = make_generator(lambda m: api_error(404, "not found") if m == "m1" else "ok", monkeypatch)
    assert gen.generate_document("NDA", "A, B", "", "") == "ok"
    assert gen.client.models.calls == ["m1", "m2"]


def test_retries_on_503_then_succeeds(monkeypatch):
    state = {"n": 0}

    def behaviour(model):
        state["n"] += 1
        return api_error(503) if state["n"] == 1 else "recovered"

    gen = make_generator(behaviour, monkeypatch)
    assert gen.generate_document("NDA", "A, B", "", "") == "recovered"


def test_bad_key_is_fatal_and_friendly(monkeypatch):
    gen = make_generator(lambda m: api_error(400, "API key not valid. Please pass a valid API key."), monkeypatch)
    with pytest.raises(gg.GenerationError, match="API key was rejected"):
        gen.generate_document("NDA", "A, B", "", "")
    assert gen.client.models.calls == ["m1"]


def test_all_models_fail(monkeypatch):
    gen = make_generator(lambda m: api_error(404), monkeypatch)
    with pytest.raises(gg.GenerationError, match="All configured models failed"):
        gen.generate_document("NDA", "A, B", "", "")


def test_empty_response_moves_on(monkeypatch):
    gen = make_generator(lambda m: "" if m == "m1" else "second", monkeypatch)
    assert gen.generate_document("NDA", "A, B", "", "") == "second"
