"""CLI entrypoint for the Week 1 MDM match engine."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.embedding import generate_candidate_pairs
from src.matcher import evaluate_candidate
from src.preprocessing import RawRecord, preprocess_record
from src.providers.groq_provider import GroqProvider, GroqProviderConfig
from src.runtime import load_settings


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_records(path: Path) -> list[RawRecord]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            RawRecord(
                record_id=row["record_id"],
                company_name=row["company_name"],
                address=row["address"],
                city=row["city"],
                country=row["country"],
                alternate_name=row.get("alternate_name", ""),
            )
            for row in reader
        ]


def parse_args(default_input_path: Path, default_candidate_similarity: float) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MDM match engine starter pipeline.")
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input_path,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--candidate-threshold",
        type=float,
        default=default_candidate_similarity,
        help="Cosine similarity threshold for candidate generation.",
    )
    return parser.parse_args()


def main() -> None:
    settings = load_settings(PROJECT_ROOT)
    args = parse_args(settings.input_path, settings.candidate_similarity)
    raw_records = load_records(args.input)
    provider = None
    if settings.groq_api_key:
        provider = GroqProvider(
            GroqProviderConfig(
                api_key=settings.groq_api_key,
                translation_model=settings.groq_translation_model,
                reasoning_model=settings.groq_reasoning_model,
                abbreviation_model=settings.groq_abbreviation_model,
            )
        )
    processed_records = [preprocess_record(record, settings=settings, provider=provider) for record in raw_records]
    records_by_id = {record.record_id: record for record in processed_records}
    candidates = generate_candidate_pairs(processed_records, args.candidate_threshold)

    print("=== Candidate Pairs ===")
    for candidate in candidates:
        print(
            f"{candidate.left_record_id} <-> {candidate.right_record_id} | "
            f"similarity={candidate.similarity:.4f}"
        )

    print("\n=== Match Results ===")
    for candidate in candidates:
        result = evaluate_candidate(candidate, records_by_id)
        print(
            f"{result.record_id_1} vs {result.record_id_2} | "
            f"score={result.final_score} | class={result.classification}"
        )
        for reason in result.reasoning:
            print(f"  - {reason}")
        print()


if __name__ == "__main__":
    main()
