from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_root_contains_version():
    response = client.get("/")
    body = response.json()
    assert "version" in body
    assert "message" in body
