import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_crud_flow(client):
    r = client.post(
        "/api/customers",
        json={"name": "Alice", "email": "alice@example.com", "company": "Acme"},
    )
    assert r.status_code == 201
    customer = r.json()
    assert customer["name"] == "Alice"
    assert customer["id"] > 0
    assert customer["created_at"]

    r = client.get("/api/customers")
    assert [c["name"] for c in r.json()] == ["Alice"]

    r = client.put(
        f"/api/customers/{customer['id']}", json={"name": "Alice Li", "phone": "123"}
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Alice Li"
    assert r.json()["phone"] == "123"

    r = client.delete(f"/api/customers/{customer['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/customers/{customer['id']}").status_code == 404


def test_name_required(client):
    assert client.post("/api/customers", json={"name": ""}).status_code == 422


def test_missing_customer_returns_404(client):
    assert client.get("/api/customers/999").status_code == 404
    assert client.put("/api/customers/999", json={"name": "x"}).status_code == 404
    assert client.delete("/api/customers/999").status_code == 404
