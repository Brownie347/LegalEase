"""Drives the real Streamlit script headlessly (backend HTTP call is mocked)."""
from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "frontend" / "app.py")
DOC = "Freelance Work Contract\n\n1. Services:\n\nThe provider shall deliver the work by the agreed date, in full."


class FakeResp:
    status_code = 200

    def __init__(self, payload=None, status=200):
        self._payload, self.status_code = payload or {}, status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


def fill(at):
    at.text_input[0].set_value("Freelance Work Contract")
    at.text_area[0].set_value("Jane Doe (Provider), TechNova (Client)")
    at.text_area[1].set_value("Payment in 7 days; Work due May 15")
    at.text_input[1].set_value("April 15, 2025")


def test_initial_state_shows_hint():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("Generate Document" in i.value for i in at.info)


def test_generate_edit_and_download(monkeypatch):
    sent = {}

    def fake_post(url, json, timeout):
        sent.update(url=url, json=json)
        return FakeResp({"document": DOC})

    monkeypatch.setattr(requests, "post", fake_post)
    at = AppTest.from_file(APP, default_timeout=30).run()
    fill(at)
    at.button[0].click().run()
    assert not at.exception
    assert sent["url"].endswith("/generate")
    assert sent["json"]["document_type"] == "Freelance Work Contract"
    assert any("Generated Successfully" in s.value for s in at.success)
    assert "Freelance Work Contract" in at.session_state["generated_text"]

    # open editor and change the text
    edit_btn = [b for b in at.button if "Edit Document" in b.label][0]
    edit_btn.click().run()
    assert at.session_state["show_edit"] is True
    at.text_area(key="editor_text").set_value("I AM EDITING\n\n" + DOC).run()
    assert at.session_state["generated_text"].startswith("I AM EDITING")


def test_backend_down_shows_friendly_error(monkeypatch):
    def fake_post(*a, **k):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(requests, "post", fake_post)
    at = AppTest.from_file(APP, default_timeout=30).run()
    fill(at)
    at.button[0].click().run()
    assert not at.exception
    assert any("Cannot reach the backend" in e.value for e in at.error)


def test_backend_error_detail_is_shown(monkeypatch):
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: FakeResp({"detail": "GEMINI_API_KEY is not set"}, status=500)
    )
    at = AppTest.from_file(APP, default_timeout=30).run()
    fill(at)
    at.button[0].click().run()
    assert any("GEMINI_API_KEY is not set" in e.value for e in at.error)


def test_requires_type_and_parties():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()
    assert any("Document Type" in w.value for w in at.warning)
