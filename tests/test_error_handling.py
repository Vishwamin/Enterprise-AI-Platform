"""
Tests for the global exception handler in app/main.py.

We use raise_server_exceptions=False so the TestClient behaves like a
real HTTP client would — it gets back our JSON 500 response, instead of
pytest re-raising the exception itself.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_unhandled_exception_returns_500():
    response = client.get("/debug/trigger-error")
    assert response.status_code == 500


def test_unhandled_exception_returns_generic_safe_body():
    response = client.get("/debug/trigger-error")
    body = response.json()
    assert body == {
        "error": "internal_error",
        "message": "Something went wrong. Please try again later.",
    }


def test_unhandled_exception_does_not_leak_internals():
    response = client.get("/debug/trigger-error")
    # The client should never see the exception type, message, or a
    # traceback — only the generic response above.
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
