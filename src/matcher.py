"""Week 1 matching pipeline implementation."""

from __future__ import annotations

from dataclasses import dataclass

from src.config import SCORING, THRESHOLDS
from src.embedding import CandidatePair
from src.preprocessing import ProcessedRecord

from src.orchestrator import evaluate_candidate_week2


@dataclass(frozen=True)
class MatchResult:
    record_id_1: str
    record_id_2: str
    similarity: float
    final_score: int
    classification: str
    exact_match: bool
    reasoning: list[str]


def _token_set(text: str) -> set[str]:
    return {token for token in text.split() if token}


def exact_match(left: ProcessedRecord, right: ProcessedRecord) -> bool:
    name_pool_left = {left.normalized_company_name, left.normalized_alternate_name} - {""}
    name_pool_right = {right.normalized_company_name, right.normalized_alternate_name} - {""}
    same_name = bool(name_pool_left.intersection(name_pool_right))
    same_address = left.normalized_address == right.normalized_address and left.normalized_address != ""
    return same_name and same_address


def address_overlap(left: ProcessedRecord, right: ProcessedRecord) -> float:
    left_tokens = _token_set(left.normalized_address)
    right_tokens = _token_set(right.normalized_address)
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
    return round(overlap, 4)


def city_country_match(left: ProcessedRecord, right: ProcessedRecord) -> bool:
    return (
        left.normalized_city == right.normalized_city
        and left.normalized_country == right.normalized_country
        and left.normalized_city != ""
        and left.normalized_country != ""
    )


def classify(score: int) -> str:
    if score > THRESHOLDS.high_confidence_match:
        return "High Confidence Match"
    if score >= THRESHOLDS.potential_match:
        return "Potential Match"
    return "Non-Match"


def evaluate_candidate(
    candidate: CandidatePair,
    records_by_id: dict[str, ProcessedRecord],
) -> MatchResult:
    left = records_by_id[candidate.left_record_id]
    right = records_by_id[candidate.right_record_id]
    reasoning: list[str] = []
    score = 0.0

    is_exact = exact_match(left, right)
    if is_exact:
        score += SCORING.exact_match
        reasoning.append("Level 1 exact match succeeded on normalized company name and address.")
    else:
        reasoning.append("Level 1 exact match did not fully align on both name and address.")

    similarity_points = candidate.similarity * SCORING.embedding_similarity
    score += similarity_points
    reasoning.append(
        f"Embedding similarity contributed {similarity_points:.1f}/{SCORING.embedding_similarity} points."
    )

    same_city_country = city_country_match(left, right)
    if same_city_country:
        score += SCORING.city_country_match
        reasoning.append("City and country are an exact normalized match.")
    else:
        reasoning.append("City and/or country differ after normalization.")

    address_overlap_score = address_overlap(left, right)
    overlap_points = address_overlap_score * SCORING.address_overlap
    score += overlap_points
    reasoning.append(
        f"Address token overlap contributed {overlap_points:.1f}/{SCORING.address_overlap} points."
    )

    if left.language != "english" or right.language != "english":
        reasoning.append("Multilingual preprocessing was applied through language detection and transliteration.")

    final_score = min(100, round(score))
    return MatchResult(
        record_id_1=left.record_id,
        record_id_2=right.record_id,
        similarity=candidate.similarity,
        final_score=final_score,
        classification=classify(final_score),
        exact_match=is_exact,
        reasoning=reasoning,
    )
