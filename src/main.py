"""CLI entrypoint for the MDM match engine (Week 2 enabled)."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.embedding import generate_candidate_pairs
from src.orchestrator import evaluate_candidate_week2
from src.preprocessing import RawRecord, preprocess_record
from src.providers.google_maps import GoogleMapsConfig, GoogleMapsProvider
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
    parser = argparse.ArgumentParser(description="Run the MDM match engine pipeline (Week 2).")
    parser.add_argument("--input", type=Path, default=default_input_path)
    parser.add_argument("--candidate-threshold", type=float, default=default_candidate_similarity)
    return parser.parse_args()


def main() -> None:
    settings = load_settings(PROJECT_ROOT)
    args = parse_args(settings.input_path, settings.candidate_similarity)

    raw_records = load_records(args.input)

    # Initialize Groq provider (LLM)
    groq_provider = None
    if settings.groq_api_key:
        groq_provider = GroqProvider(
            GroqProviderConfig(
                api_key=settings.groq_api_key,
                translation_model=settings.groq_translation_model,
                reasoning_model=settings.groq_reasoning_model,
                abbreviation_model=settings.groq_abbreviation_model,
            )
        )

    # Initialize Google Maps provider (Geo)
    maps_provider = None
    if settings.google_maps_api_key:
        maps_provider = GoogleMapsProvider(
            GoogleMapsConfig(
                api_key=settings.google_maps_api_key,
                geocoding_base_url=settings.google_geocoding_base_url,
                address_validation_base_url=settings.google_address_validation_base_url,
            )
        )

    # Preprocessing
    processed_records = [
        preprocess_record(record, settings=settings, provider=groq_provider)
        for record in raw_records
    ]

    records_by_id = {record.record_id: record for record in processed_records}

    # Candidate generation (Week 1)
    candidates = generate_candidate_pairs(processed_records, args.candidate_threshold)

    print("\n=== Candidate Pairs ===")
    for c in candidates:
        print(f"{c.left_record_id} <-> {c.right_record_id} | similarity={c.similarity:.4f}")

    # Week 2 matching
    print("\n=== Week 2 Multi-Agent Results ===")

    for candidate in candidates:
        result = evaluate_candidate_week2(
            candidate,
            records_by_id,
            groq_provider=groq_provider,
            maps_provider=maps_provider,
        )

        print(f"\n{result.record_id_1} vs {result.record_id_2}")
        print(f"Similarity: {result.similarity:.4f}")
        print(f"Exact Match: {result.exact_match}")

        print("\n--- Agent Outputs ---")
        print(f"Name Agent: {result.name_result.status} | score={result.name_result.score}")
        print(f"Geo Agent: {result.geo_result.status} | score={result.geo_result.score}")
        print(f"Address Agent: {result.address_result.status} | score={result.address_result.score}")

        print("\n--- Reasoning ---")
        for r in result.reasoning:
            print(f"- {r}")


if __name__ == "__main__":
    main()
