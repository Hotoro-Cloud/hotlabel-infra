from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "HotLabel",
        "version": "0.1.0",
        "description": "Crowdsourced Data Labeling Solution",
        "docs": "/docs",
    }

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}