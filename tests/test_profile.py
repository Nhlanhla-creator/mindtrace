from backend.app.profile import Profile


def test_profile_detects_repeated_misconception():
    profile = Profile()
    first = profile.add({"diagnosis": "physics-01", "topic": "Physics", "confidence": "Confident"})
    second = profile.add({"diagnosis": "physics-01", "topic": "Physics", "confidence": "Confident"})

    assert first["drift"]["direction"] == "neutral"
    assert second["drift"]["direction"] == "flat"
    assert second["misconception_counts"] == {"physics-01": 2}


def test_profile_detects_movement_between_models():
    profile = Profile()
    profile.add({"diagnosis": "physics-01", "topic": "Physics", "confidence": "Confident"})
    result = profile.add({"diagnosis": None, "topic": "Physics", "confidence": "Confident"})

    assert result["drift"]["direction"] == "up"
    assert result["drift"]["color"] == "green"
