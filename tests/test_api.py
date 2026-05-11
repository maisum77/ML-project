import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "SocialPulse AI"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_trending_endpoint():
    response = client.get("/api/v1/trending")
    assert response.status_code == 200
    assert "topics" in response.json()


def test_sentiment_overall():
    response = client.get("/api/v1/sentiment/overall")
    assert response.status_code == 200
    assert "sentiment_breakdown" in response.json()


def test_feed_endpoint():
    response = client.get("/api/v1/feed")
    assert response.status_code == 200
    assert "posts" in response.json()


def test_export_endpoint():
    response = client.get("/api/v1/export?format=json")
    assert response.status_code == 200
    assert "data" in response.json()
