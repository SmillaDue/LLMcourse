from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_positive_sentiment():
    response = client.post(
        "/v1/sentiment",
        json={"text": "This course is really good"}
    )
    assert response.status_code == 200
    assert response.json() == {"sentiment": "positive"}


def test_negative_sentiment():
    response = client.post(
        "/v1/sentiment",
        json={"text": "This course is really bad"}
    )
    assert response.status_code == 200
    assert response.json() == {"sentiment": "negative"}


def test_neutral_sentiment():
    response = client.post(
        "/v1/sentiment",
        json={"text": "This is a course"}
    )
    assert response.status_code == 200
    assert response.json() == {"sentiment": "neutral"}
