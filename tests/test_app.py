"""
tests/test_app.py - Basic smoke tests for CI/CD pipeline.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


def test_health_endpoint(client):
    """GET /health returns 200 with status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "service" in data


def test_index_endpoint(client):
    """GET / returns 200 HTML."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"PolicyBot" in resp.data


def test_chat_missing_question(client):
    """POST /chat with no body returns 400."""
    resp = client.post("/chat", json={})
    assert resp.status_code == 400


def test_chat_empty_question(client):
    """POST /chat with empty question returns 400."""
    resp = client.post("/chat", json={"question": "   "})
    assert resp.status_code == 400


def test_chat_question_too_long(client):
    """POST /chat with question > 500 chars returns 400."""
    resp = client.post("/chat", json={"question": "x" * 501})
    assert resp.status_code == 400


def test_app_imports():
    """Verify the app module imports cleanly (used in CI)."""
    import app
    assert app.app is not None
