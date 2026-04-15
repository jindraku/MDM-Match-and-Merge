"""Embedding and candidate generation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing import ProcessedRecord


@dataclass(frozen=True)
class CandidatePair:
    left_record_id: str
    right_record_id: str
    similarity: float


def generate_embeddings(records: list[ProcessedRecord]) -> tuple[TfidfVectorizer, np.ndarray]:
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    embeddings = vectorizer.fit_transform([record.structured_text for record in records])
    return vectorizer, embeddings


def generate_candidate_pairs(records: list[ProcessedRecord], threshold: float) -> list[CandidatePair]:
    if len(records) < 2:
        return []

    _, embeddings = generate_embeddings(records)
    similarity_matrix = cosine_similarity(embeddings)
    candidates: list[CandidatePair] = []

    for left_index in range(len(records)):
        for right_index in range(left_index + 1, len(records)):
            score = float(similarity_matrix[left_index, right_index])
            if score >= threshold:
                candidates.append(
                    CandidatePair(
                        left_record_id=records[left_index].record_id,
                        right_record_id=records[right_index].record_id,
                        similarity=round(score, 4),
                    )
                )

    return sorted(candidates, key=lambda candidate: candidate.similarity, reverse=True)
