"""End-to-end pairwise match pipeline on canonical MDM party records."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from src.config import SCORING, THRESHOLDS
from src.embedding import CandidatePair, generate_candidate_pairs
from src.golden_record import GoldenRecord, assemble_golden_records
from src.matcher import classify
from src.mdm_loader import PartyGroup
from src.orchestrator import evaluate_candidate_week2
from src.preprocessing import ProcessedRecord, RawRecord, preprocess_record


@dataclass(frozen=True)
class MatchPipelineOutput:
    golden_records: list[GoldenRecord]
    canonical_records: list[ProcessedRecord]
    candidate_pairs: list[CandidatePair]
    match_results: list["FinalMatchResult"]


@dataclass(frozen=True)
class FinalMatchResult:
    record_id_1: str
    record_id_2: str
    similarity: float
    exact_match: bool
    name_status: str
    geo_status: str
    address_status: str
    final_score: int
    classification: str
    reasoning: list[str]


def build_canonical_records(
    groups: list[PartyGroup],
    golden_records: list[GoldenRecord],
    *,
    settings,
    groq_provider=None,
) -> list[ProcessedRecord]:
    golden_by_party = {record.party_id: record for record in golden_records}
    processed: list[ProcessedRecord] = []

    for group in groups:
        golden = golden_by_party[group.party.party_id]
        best_name_variant = next(
            (item for item in group.individuals if item.individual_id == golden.best_individual_id),
            None,
        )
        best_address_variant = next(
            (item for item in group.addresses if item.address_id == golden.best_address_id),
            None,
        )

        raw = RawRecord(
            record_id=group.party.party_id,
            company_name=group.party.party_name,
            address=best_address_variant.freeform_address if best_address_variant else "",
            city=best_address_variant.city if best_address_variant else "",
            country=(best_address_variant.country_code or best_address_variant.country_name)
            if best_address_variant
            else "",
            alternate_name=best_name_variant.display_name if best_name_variant else "",
        )
        processed.append(preprocess_record(raw, settings=settings, provider=groq_provider))

    return processed


def compute_final_score(match_result) -> tuple[int, str, list[str]]:
    score = 0.0
    reasoning: list[str] = []

    exact_points = SCORING.final_exact_match if match_result.exact_match else 0
    score += exact_points
    reasoning.append(f"Level 1 exact match contribution: {exact_points}/{SCORING.final_exact_match}.")

    embedding_points = round(match_result.similarity * SCORING.final_embedding_similarity, 1)
    score += embedding_points
    reasoning.append(
        f"Embedding similarity contribution: {embedding_points}/{SCORING.final_embedding_similarity}."
    )

    score += match_result.name_result.score
    reasoning.append(
        f"Level 3 name verification contribution: {match_result.name_result.score}/{SCORING.name_verification}."
    )

    score += match_result.geo_result.score
    reasoning.append(
        f"Level 2 geo-distance contribution: {match_result.geo_result.score}/{SCORING.geo_distance}."
    )

    score += match_result.address_result.score
    reasoning.append(
        f"Level 4 address analysis contribution: {match_result.address_result.score}/{SCORING.address_analysis}."
    )

    if match_result.name_result.status == "exact_business_match" and match_result.similarity >= 0.9:
        score += 10
        reasoning.append("Level 5 bonus applied for exact semantic name alignment with strong candidate similarity: +10.")

    if match_result.name_result.status == "no_name_match":
        score -= SCORING.penalty_name_conflict
        reasoning.append(f"Penalty applied for name conflict: -{SCORING.penalty_name_conflict}.")
    if match_result.address_result.status == "conflicting_address":
        score -= SCORING.penalty_address_conflict
        reasoning.append(f"Penalty applied for address conflict: -{SCORING.penalty_address_conflict}.")
    if match_result.geo_result.status == "same_company_different_office":
        score -= SCORING.penalty_different_office
        reasoning.append(f"Penalty applied for distant offices: -{SCORING.penalty_different_office}.")

    final_score = max(0, min(100, round(score)))
    classification = classify(final_score)
    reasoning.extend(match_result.reasoning)
    return final_score, classification, reasoning


def generate_mdm_candidate_pairs(processed_records: list[ProcessedRecord]) -> list[CandidatePair]:
    structured_candidates = generate_candidate_pairs(processed_records, THRESHOLDS.candidate_similarity)
    candidate_map: dict[tuple[str, str], float] = {
        (candidate.left_record_id, candidate.right_record_id): candidate.similarity
        for candidate in structured_candidates
    }

    for left_index in range(len(processed_records)):
        for right_index in range(left_index + 1, len(processed_records)):
            left = processed_records[left_index]
            right = processed_records[right_index]
            name_ratio = SequenceMatcher(
                None,
                left.normalized_company_name,
                right.normalized_company_name,
            ).ratio()
            if name_ratio >= THRESHOLDS.validation_name_similarity:
                key = (left.record_id, right.record_id)
                candidate_map[key] = max(candidate_map.get(key, 0.0), round(name_ratio, 4))

    return sorted(
        [
            CandidatePair(left_record_id=left, right_record_id=right, similarity=similarity)
            for (left, right), similarity in candidate_map.items()
        ],
        key=lambda candidate: candidate.similarity,
        reverse=True,
    )


def evaluate_final_matches(
    processed_records: list[ProcessedRecord],
    *,
    groq_provider=None,
    maps_provider=None,
) -> tuple[list[CandidatePair], list[FinalMatchResult]]:
    records_by_id = {record.record_id: record for record in processed_records}
    candidates = generate_mdm_candidate_pairs(processed_records)
    results: list[FinalMatchResult] = []

    for candidate in candidates:
        week2 = evaluate_candidate_week2(
            candidate,
            records_by_id,
            groq_provider=groq_provider,
            maps_provider=maps_provider,
        )
        final_score, classification, reasoning = compute_final_score(week2)
        results.append(
            FinalMatchResult(
                record_id_1=week2.record_id_1,
                record_id_2=week2.record_id_2,
                similarity=week2.similarity,
                exact_match=week2.exact_match,
                name_status=week2.name_result.status,
                geo_status=week2.geo_result.status,
                address_status=week2.address_result.status,
                final_score=final_score,
                classification=classification,
                reasoning=reasoning,
            )
        )

    results.sort(key=lambda item: (-item.final_score, -item.similarity, item.record_id_1, item.record_id_2))
    return candidates, results


def run_end_to_end_match_pipeline(
    groups: list[PartyGroup],
    *,
    settings,
    groq_provider=None,
    azure_provider=None,
    maps_provider=None,
) -> MatchPipelineOutput:
    golden_records = assemble_golden_records(
        groups,
        groq_provider=groq_provider,
        azure_provider=azure_provider,
    )
    canonical_records = build_canonical_records(
        groups,
        golden_records,
        settings=settings,
        groq_provider=groq_provider,
    )
    candidates, match_results = evaluate_final_matches(
        canonical_records,
        groq_provider=groq_provider,
        maps_provider=maps_provider,
    )
    return MatchPipelineOutput(
        golden_records=golden_records,
        canonical_records=canonical_records,
        candidate_pairs=candidates,
        match_results=match_results,
    )


def write_match_results(path: Path, results: list[FinalMatchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_id_1",
        "record_id_2",
        "similarity",
        "exact_match",
        "name_status",
        "geo_status",
        "address_status",
        "final_score",
        "classification",
        "reasoning",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    **result.__dict__,
                    "reasoning": " | ".join(result.reasoning),
                }
            )
