from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_with_valid_question_returns_200():
    response = client.post("/api/v1/ask", json={"question": "What is our leave policy?"})
    assert response.status_code == 200


def test_ask_echoes_question_back():
    response = client.post("/api/v1/ask", json={"question": "What is our leave policy?"})
    body = response.json()
    assert body["question"] == "What is our leave policy?"
    assert "answer" in body


def test_ask_with_missing_question_returns_422():
    # No "question" field at all — Pydantic should reject this
    # before our function body ever runs.
    response = client.post("/api/v1/ask", json={})
    assert response.status_code == 422


def test_ask_with_wrong_type_returns_422():
    # "question" must be a string, not a number.
    response = client.post("/api/v1/ask", json={"question": 12345})
    assert response.status_code == 422


def test_ask_with_empty_question_returns_400():
    # This is an EXPECTED error we handle on purpose (app/api/v1/ask.py),
    # distinct from Pydantic's automatic 422 for malformed input.
    response = client.post("/api/v1/ask", json={"question": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "question must not be empty"
