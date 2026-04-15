"""Dataset profiling for MDM source analysis."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from src.runtime import load_settings
from src.preprocessing import RawRecord, preprocess_record


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ProfileReport:
    record_count: int
    fields: list[str]
    language_distribution: dict[str, int]
    company_language_distribution: dict[str, int]
    address_language_distribution: dict[str, int]
    duplicate_rate: float
    exact_duplicate_pairs: int
    missing_value_counts: dict[str, int]
    quality_issues: list[str]


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


def build_profile(records: list[RawRecord]) -> ProfileReport:
    processed = [preprocess_record(record) for record in records]
    fields = list(RawRecord.__dataclass_fields__.keys())
    language_distribution = Counter(item.language for item in processed)
    company_language_distribution = Counter(item.company_language for item in processed)
    address_language_distribution = Counter(item.address_language for item in processed)
    missing_value_counts = {
        "company_name": sum(1 for record in records if not record.company_name.strip()),
        "address": sum(1 for record in records if not record.address.strip()),
        "city": sum(1 for record in records if not record.city.strip()),
        "country": sum(1 for record in records if not record.country.strip()),
        "alternate_name": sum(1 for record in records if not record.alternate_name.strip()),
    }

    seen: dict[tuple[str, str], str] = {}
    duplicate_pairs = 0
    non_ascii_records = 0
    alternate_name_usage = 0
    near_address_variants = 0
    for item in processed:
        key = (item.normalized_company_name, item.normalized_address)
        if key in seen:
            duplicate_pairs += 1
        else:
            seen[key] = item.record_id
        if item.language != "english":
            non_ascii_records += 1
        if item.normalized_alternate_name:
            alternate_name_usage += 1
        if any(token in item.raw_address.lower() for token in ("st.", "rd", "ave", "blvd")):
            near_address_variants += 1

    quality_issues: list[str] = []
    if non_ascii_records:
        quality_issues.append(
            f"{non_ascii_records} record(s) contain multilingual or mixed-language content that need normalization."
        )
    if duplicate_pairs:
        quality_issues.append(
            f"{duplicate_pairs} exact duplicate pair(s) were found after normalization of company name and address."
        )
    if alternate_name_usage:
        quality_issues.append(
            f"{alternate_name_usage} record(s) use alternate names, indicating trade-name or alias handling is required."
        )
    if near_address_variants:
        quality_issues.append(
            f"{near_address_variants} record(s) use abbreviated address tokens, which can mask duplicates without expansion."
        )

    record_count = len(records)
    duplicate_rate = round((duplicate_pairs * 2 / record_count) * 100, 2) if record_count else 0.0
    return ProfileReport(
        record_count=record_count,
        fields=fields,
        language_distribution=dict(language_distribution),
        company_language_distribution=dict(company_language_distribution),
        address_language_distribution=dict(address_language_distribution),
        duplicate_rate=duplicate_rate,
        exact_duplicate_pairs=duplicate_pairs,
        missing_value_counts=missing_value_counts,
        quality_issues=quality_issues,
    )


def render_markdown(report: ProfileReport, dataset_path: Path) -> str:
    quality_lines = "\n".join(f"- {issue}" for issue in report.quality_issues) or "- No major issues detected."
    return f"""# Data Profile

Dataset: `{dataset_path}`

## Summary

- Record count: {report.record_count}
- Current exact duplicate pairs after normalization: {report.exact_duplicate_pairs}
- Approximate duplicate rate: {report.duplicate_rate}%

## Schema

- Fields: {", ".join(report.fields)}

## Language distribution

- Record-level: {report.language_distribution}
- Company field: {report.company_language_distribution}
- Address field: {report.address_language_distribution}

## Missing values

- {report.missing_value_counts}

## Known quality issues

{quality_lines}
"""


def main() -> None:
    settings = load_settings(PROJECT_ROOT)
    parser = argparse.ArgumentParser(description="Profile an MDM CSV dataset.")
    parser.add_argument("--input", type=Path, default=settings.input_path)
    parser.add_argument("--output", type=Path, default=settings.profile_output_path)
    args = parser.parse_args()

    records = load_records(args.input)
    report = build_profile(records)
    rendered = render_markdown(report, args.input)
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
