from fastapi.testclient import TestClient

from platform_demo import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_double():
    response = client.post("/v1/double", json={"value": 9})
    assert response.status_code == 200
    assert response.json() == {"result": 18}


def test_invalid_negative():
    assert client.post("/v1/double", json={"value": -1}).status_code == 422


def test_missing_value():
    assert client.post("/v1/double", json={}).status_code == 422


def test_upper_bound():
    assert client.post("/v1/double", json={"value": 1001}).status_code == 422
