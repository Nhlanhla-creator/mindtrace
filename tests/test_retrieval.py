from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_physics_retrieval_ranks_heavy_objects_first():
    response = client.post(
        "/api/retrieve",
        json={"text": "Heavier objects fall faster because gravity pulls harder on them.", "topic": "Physics"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"][0]["id"] == "physics-01"
    assert 0 < payload["results"][0]["score"] <= 1
    assert len(payload["results"]) == 5


def test_math_retrieval_ranks_decimal_confusion_first():
    response = client.post(
        "/api/retrieve",
        json={"text": "0.5 is smaller than 0.25 because 5 is less than 25.", "topic": "Math"},
    )

    assert response.status_code == 200
    assert response.json()["results"][0]["id"] == "math-01"


def test_empty_text_is_rejected():
    response = client.post("/api/retrieve", json={"text": "   "})

    assert response.status_code == 422
