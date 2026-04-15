"""CLI entrypoint for the Week 1 MDM match engine."""

from __future__ import annotations

import csv
from pathlib import Path

from src.config import THRESHOLDS
from src.embedding import generate_candidate_pairs
from src.matcher import evaluate_candidate
from src.preprocessing import RawRecord, preprocess_record


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_records.csv"


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


def main() -> None:
    raw_records = load_records(DATA_PATH)
    processed_records = [preprocess_record(record) for record in raw_records]
    records_by_id = {record.record_id: record for record in processed_records}
    candidates = generate_candidate_pairs(processed_records, THRESHOLDS.candidate_similarity)

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
