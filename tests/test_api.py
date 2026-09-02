from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_library_has_all_documented_entries():
    response = client.get("/api/library")
    assert response.status_code == 200
    assert response.json()["count"] == 25


def test_profile_is_session_scoped():
    response = client.get("/api/profile/test-session")
    assert response.status_code == 200
    assert response.json()["submission_count"] == 0


def test_room_creation_returns_joinable_id():
    response = client.post("/api/rooms", json={})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["room_id"]) == 8
    assert payload["join_url"] == f"/room/{payload['room_id']}"
