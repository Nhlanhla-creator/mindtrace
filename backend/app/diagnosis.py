"""Candidate-constrained diagnosis with a deterministic demo fallback."""

from __future__ import annotations

import json
import os
from typing import Any

from .retrieval import retriever


DEMO_RESPONSES: dict[str, dict[str, Any]] = {
    "Heavier objects fall faster than lighter ones.": {
        "diagnosis": "physics-01",
        "confidence": "Confident",
        "evidence_quote": "Heavier objects fall faster",
        "correction": "In a vacuum, a heavy object and a light object accelerate downward at the same rate. Their masses change their weights, but not the acceleration caused by gravity.",
        "reasoning": "The explanation directly matches the documented belief that mass determines falling speed.",
    },
    "Force keeps things moving.": {
        "diagnosis": "physics-02",
        "confidence": "Confident",
        "evidence_quote": "Force keeps things moving",
        "correction": "A net force changes motion; it is not required to sustain constant velocity. Friction often makes it seem that moving objects need continuous force.",
        "reasoning": "The phrase directly expresses the force-sustains-motion model.",
    },
    "0.5 is smaller than 0.25.": {
        "diagnosis": "math-01",
        "confidence": "Confident",
        "evidence_quote": "0.5 is smaller than 0.25",
        "correction": "Rewrite 0.5 as 0.50. Since 50 hundredths is greater than 25 hundredths, 0.5 is larger than 0.25.",
        "reasoning": "The comparison exactly matches the documented decimal-place confusion.",
    },
    "Multiplying by 0.5 makes it bigger.": {
        "diagnosis": "math-02",
        "confidence": "Confident",
        "evidence_quote": "Multiplying by 0.5 makes it bigger",
        "correction": "Multiplying by 0.5 means taking half. For example, 10 × 0.5 = 5, so multiplying by a number between 0 and 1 reduces a positive number.",
        "reasoning": "The statement directly expresses the belief that multiplication always increases magnitude.",
    },
    "Objects fall at the same rate regardless of mass.": {
        "diagnosis": None,
        "confidence": "Confident",
        "evidence_quote": "Objects fall at the same rate regardless of mass",
        "correction": "That is the correct model for ideal free fall: ignoring air resistance, objects near Earth accelerate at approximately 9.8 m/s² regardless of mass.",
        "reasoning": "No documented misconception is supported by this explanation.",
        "result_state": "correct_model",
    },
}


def _cached_response(text: str) -> dict[str, Any] | None:
    normalized = " ".join(text.split()).casefold()
    for example, response in DEMO_RESPONSES.items():
        if " ".join(example.split()).casefold() == normalized:
            return {**response, "source": "cached_demo"}
    return None


def _entry_by_id(entry_id: str | None) -> dict[str, Any] | None:
    return next((entry for entry in retriever.entries if entry["id"] == entry_id), None)


def _fallback(text: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if not candidates or candidates[0]["score"] < 0.45:
        return {
            "diagnosis": None,
            "confidence": "Low Confidence",
            "evidence_quote": None,
            "correction": "No documented misconception matched strongly enough. Try explaining the reasoning step that led to your answer.",
            "reasoning": "Retrieval did not produce a strong enough candidate for a responsible diagnosis.",
            "source": "retrieval_fallback",
            "result_state": "insufficient_evidence",
        }

    top = candidates[0]
    entry = _entry_by_id(top["id"])
    return {
        "diagnosis": top["id"],
        "confidence": "Plausible" if top["score"] < 0.45 else "Confident",
        "evidence_quote": top.get("best_trigger_phrase"),
        "correction": entry["correction_explanation"] if entry else "Review the correct concept and explain your reasoning again.",
        "reasoning": "The diagnosis is based on the highest deterministic retrieval match; live confirmation was unavailable.",
        "source": "retrieval_fallback",
        "result_state": "misconception",
    }


def _claude_confirm(text: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic

        candidate_text = json.dumps(candidates, ensure_ascii=False)
        prompt = f"""You are confirming a diagnosis from a constrained candidate list.
Do not invent a misconception or cite anything outside the candidates.
Return JSON only with keys: diagnosis (candidate id or null), confidence (Confident, Plausible, or Low Confidence), evidence_quote (exact contiguous quote from student text or null), correction (plain-language targeted correction), reasoning (one sentence).
If the explanation is scientifically correct or no candidate is supported, use diagnosis null.

Student explanation:
{text}

Retrieved candidates:
{candidate_text}"""
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            temperature=0,
            system="You are a careful educational assessment assistant. Output valid JSON only.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((block.text for block in message.content if hasattr(block, "text")), "")
        result = json.loads(raw)
        candidate_ids = {candidate["id"] for candidate in candidates}
        if result.get("diagnosis") not in candidate_ids and result.get("diagnosis") is not None:
            return None
        if result.get("evidence_quote") and result["evidence_quote"] not in text:
            return None
        if result.get("confidence") not in {"Confident", "Plausible", "Low Confidence"}:
            return None
        return {**result, "source": "claude", "result_state": "correct_model" if result.get("diagnosis") is None else "misconception"}
    except Exception:
        return None


def diagnose(text: str, topic: str | None = None) -> dict[str, Any]:
    candidates = retriever.retrieve(text, topic=topic, limit=5)
    use_cache = os.getenv("USE_CACHED_RESPONSES", "false").casefold() == "true"
    result = _cached_response(text) if use_cache else None
    if result is None:
        result = _claude_confirm(text, candidates) or _fallback(text, candidates)
    if "result_state" not in result:
        result["result_state"] = "correct_model" if result.get("diagnosis") is None else "misconception"
    matched_entry = _entry_by_id(result.get("diagnosis"))
    correction = result.get("correction") or ""
    if matched_entry:
        explanation_paragraphs = [
            correction,
            f"The key idea to revise is: {matched_entry['correct_concept']} This gives you a more reliable model to use when explaining a new example."
        ]
    elif result.get("result_state") == "correct_model":
        explanation_paragraphs = [
            correction,
            "Your explanation agrees with the accepted model. Keep testing it against a new situation to check that the idea transfers beyond this example."
        ]
    else:
        explanation_paragraphs = [
            correction,
            "A low-confidence result is not a judgment about your ability. Add the reasoning step, evidence, or example that led you to the answer so MindTrace can make a more responsible comparison."
        ]
    return {
        **result,
        "input": text,
        "topic": topic,
        "candidates": candidates,
        "misconception": matched_entry,
        "explanation_paragraphs": explanation_paragraphs,
    }
