"""Session-level misconception profile and learning trajectory helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any


class Profile:
    def __init__(self) -> None:
        self.submissions: list[dict[str, Any]] = []

    def add(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        self.submissions.append(diagnosis)
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        diagnosed = [item for item in self.submissions if item.get("diagnosis")]
        counts = Counter(item["diagnosis"] for item in diagnosed)
        topics = Counter(item.get("topic") for item in self.submissions if item.get("topic"))
        latest = diagnosed[-1] if diagnosed else None
        previous = diagnosed[-2] if len(diagnosed) > 1 else None

        if not diagnosed:
            drift = {"label": "Awaiting your first explanation", "direction": "neutral", "color": "blue"}
        elif latest and latest.get("confidence") == "Low Confidence":
            drift = {"label": "Drifting into a new misconception", "direction": "down", "color": "red"}
        elif previous and latest["diagnosis"] == previous["diagnosis"]:
            drift = {"label": "Still stuck in the same misconception", "direction": "flat", "color": "amber"}
        elif len(self.submissions) >= 2:
            drift = {"label": "Moving toward correct understanding", "direction": "up", "color": "green"}
        else:
            drift = {"label": "Building a baseline", "direction": "neutral", "color": "blue"}

        return {
            "submission_count": len(self.submissions),
            "history": [
                {
                    "input": item.get("input", ""),
                    "topic": item.get("topic"),
                    "diagnosis": item.get("diagnosis"),
                    "confidence": item.get("confidence"),
                    "result_state": item.get("result_state"),
                    "source": item.get("source"),
                    "score": (item.get("candidates") or [{}])[0].get("score", 0),
                }
                for item in self.submissions[-10:]
            ],
            "misconception_counts": dict(counts),
            "topic_counts": dict(topics),
            "drift": drift,
            "latest_diagnosis": latest.get("diagnosis") if latest else None,
            "recommendation": self._recommendation(topics, counts),
        }

    @staticmethod
    def _recommendation(topics: Counter, counts: Counter) -> dict[str, str]:
        if counts.get("math-01", 0) + counts.get("math-02", 0) >= 2:
            return {"topic": "Math", "title": "Fractions Foundations", "reason": "Strengthen decimal and scaling intuition next."}
        if topics.get("Physics", 0) >= 2:
            return {"topic": "Physics", "title": "Friction and Forces", "reason": "Build on your growing Newton's Laws profile."}
        if topics.get("Biology", 0) >= 2:
            return {"topic": "Biology", "title": "Cellular Systems", "reason": "Connect your biology ideas through cell structure and function."}
        return {"topic": "Physics", "title": "Newton's Laws", "reason": "Start building a cross-topic reasoning profile."}
