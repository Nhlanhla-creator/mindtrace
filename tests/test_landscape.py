from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_landscape_returns_all_topic_cells_with_scores():
    response = client.post(
        "/api/landscape",
        json={"text": "Heavier objects fall faster because gravity pulls harder.", "topic": "Physics"},
    )

    assert response.status_code == 200
    cells = response.json()["cells"]
    assert len(cells) == 9
    assert cells[0]["id"] == "physics-01"
    assert cells[0]["score"] > 0
    assert all("statement" in cell and "score" in cell for cell in cells)


def test_diagnosis_returns_two_explanation_paragraphs(monkeypatch):
    monkeypatch.setenv("USE_CACHED_RESPONSES", "true")
    response = client.post(
        "/api/diagnose",
        json={"text": "Force keeps things moving.", "topic": "Physics"},
    )

    assert response.status_code == 200
    paragraphs = response.json()["explanation_paragraphs"]
    assert len(paragraphs) >= 2
    assert all(paragraph.strip() for paragraph in paragraphs[:2])
