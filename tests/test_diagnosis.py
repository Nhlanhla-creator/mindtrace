from backend.app.diagnosis import diagnose


def test_cached_demo_returns_exact_diagnosis(monkeypatch):
    monkeypatch.setenv("USE_CACHED_RESPONSES", "true")
    result = diagnose("Heavier objects fall faster than lighter ones.", "Physics")

    assert result["source"] == "cached_demo"
    assert result["diagnosis"] == "physics-01"
    assert result["evidence_quote"] in result["input"]
    assert result["confidence"] == "Confident"


def test_unknown_explanation_is_low_confidence_without_api(monkeypatch):
    monkeypatch.delenv("USE_CACHED_RESPONSES", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = diagnose("The moon is made of polished glass and sings at night.")

    assert result["source"] == "retrieval_fallback"
    assert result["diagnosis"] is None
    assert result["confidence"] == "Low Confidence"


def test_correct_demo_has_no_misconception(monkeypatch):
    monkeypatch.setenv("USE_CACHED_RESPONSES", "true")
    result = diagnose("Objects fall at the same rate regardless of mass.")

    assert result["diagnosis"] is None
    assert result["misconception"] is None
    assert result["confidence"] == "Confident"
