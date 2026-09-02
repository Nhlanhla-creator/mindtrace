"""Deterministic misconception retrieval using TF-IDF and cosine similarity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "misconceptions.json"


class MisconceptionRetriever:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        with data_path.open(encoding="utf-8") as file:
            self.entries: list[dict[str, Any]] = json.load(file)

        self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
        self.phrase_matrix = self.vectorizer.fit_transform(
            phrase
            for entry in self.entries
            for phrase in entry["typical_trigger_phrases"]
        )
        self.phrase_ranges: list[tuple[int, int]] = []
        cursor = 0
        for entry in self.entries:
            phrase_count = len(entry["typical_trigger_phrases"])
            self.phrase_ranges.append((cursor, cursor + phrase_count))
            cursor += phrase_count

    def retrieve(
        self,
        text: str,
        topic: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the closest knowledge-base entries with inspectable scores."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        query_vector = self.vectorizer.transform([cleaned_text])
        phrase_scores = cosine_similarity(query_vector, self.phrase_matrix).ravel()
        normalized_topic = topic.casefold() if topic else None

        ranked: list[tuple[int, float, int]] = []
        for index, entry in enumerate(self.entries):
            entry_topic = entry["topic"].casefold()
            if normalized_topic and entry_topic != normalized_topic:
                continue
            start, end = self.phrase_ranges[index]
            best_phrase_offset = max(range(start, end), key=phrase_scores.__getitem__)
            ranked.append((index, float(phrase_scores[best_phrase_offset]), best_phrase_offset))

        ranked.sort(key=lambda item: (-item[1], self.entries[item[0]]["id"]))
        results = []
        for index, score, phrase_index in ranked[: max(1, min(limit, 10))]:
            entry = self.entries[index]
            results.append(
                {
                    "id": entry["id"],
                    "topic": entry["topic"],
                    "misconception_statement": entry["misconception_statement"],
                    "score": round(score, 4),
                    "best_trigger_phrase": entry["typical_trigger_phrases"][phrase_index - self.phrase_ranges[index][0]],
                    "typical_trigger_phrases": entry["typical_trigger_phrases"],
                }
            )
        return results


retriever = MisconceptionRetriever()
