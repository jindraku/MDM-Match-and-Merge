"""Dataset profiling for the 5-table MDM source schema."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.mdm_loader import load_party_groups
from src.runtime import load_settings


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ProfileReport:
    party_count: int
    table_row_counts: dict[str, int]
    schema_fields: dict[str, list[str]]
    name_variant_distribution: dict[int, int]
    phone_variant_distribution: dict[int, int]
    address_variant_distribution: dict[int, int]
    duplicate_rate: float
    exact_duplicate_groups: int
    quality_issues: list[str]


def build_profile(base_path: Path) -> ProfileReport:
    groups = load_party_groups(base_path)
    table_names = [
        "party",
        "individual",
        "electronic_address",
        "party_address",
        "party_postal_address",
    ]
    frames = {name: pd.read_csv(base_path / f"{name}.csv", dtype=str).fillna("") for name in table_names}
    schema_fields = {name: list(frame.columns) for name, frame in frames.items()}
    table_row_counts = {name: len(frame) for name, frame in frames.items()}
    name_variant_distribution = Counter(len(group.individuals) for group in groups)
    phone_variant_distribution = Counter(len(group.phones) for group in groups)
    address_variant_distribution = Counter(len(group.addresses) for group in groups)

    exact_duplicate_groups = 0
    quality_issues: list[str] = []
    groups_with_name_variants = sum(1 for group in groups if len(group.individuals) > 1)
    groups_with_phone_variants = sum(1 for group in groups if len(group.phones) > 1)
    groups_with_address_variants = sum(1 for group in groups if len(group.addresses) > 1)
    if groups_with_name_variants:
        quality_issues.append(
            f"{groups_with_name_variants} party groups contain multiple individual-name variants."
        )
    if groups_with_phone_variants:
        quality_issues.append(
            f"{groups_with_phone_variants} party groups contain multiple phone variants."
        )
    if groups_with_address_variants:
        quality_issues.append(
            f"{groups_with_address_variants} party groups contain multiple address variants."
        )
    for group in groups:
        seen_addresses = set()
        duplicate_found = False
        for address in group.addresses:
            key = (
                address.address_line_one.lower(),
                address.address_line_two.lower(),
                address.city.lower(),
                address.postal_code.lower(),
            )
            if key in seen_addresses:
                duplicate_found = True
                break
            seen_addresses.add(key)
        if duplicate_found:
            exact_duplicate_groups += 1
    if exact_duplicate_groups:
        quality_issues.append(
            f"{exact_duplicate_groups} party groups already contain exact duplicate address variants."
        )

    duplicate_rate = round((exact_duplicate_groups / len(groups)) * 100, 2) if groups else 0.0
    return ProfileReport(
        party_count=len(groups),
        table_row_counts=table_row_counts,
        schema_fields=schema_fields,
        name_variant_distribution=dict(name_variant_distribution),
        phone_variant_distribution=dict(phone_variant_distribution),
        address_variant_distribution=dict(address_variant_distribution),
        duplicate_rate=duplicate_rate,
        exact_duplicate_groups=exact_duplicate_groups,
        quality_issues=quality_issues,
    )


def render_markdown(report: ProfileReport, dataset_path: Path) -> str:
    quality_lines = "\n".join(f"- {issue}" for issue in report.quality_issues) or "- No major issues detected."
    return f"""# Data Profile

Dataset: `{dataset_path}`

## Summary

- Party count: {report.party_count}
- Current exact duplicate groups by address variants: {report.exact_duplicate_groups}
- Approximate duplicate-group rate: {report.duplicate_rate}%

## Table row counts

- {report.table_row_counts}

## Schema

- {report.schema_fields}

## Variant distribution by party

- Name variants per party: {report.name_variant_distribution}
- Phone variants per party: {report.phone_variant_distribution}
- Address variants per party: {report.address_variant_distribution}

## Known quality issues

{quality_lines}
"""


def main() -> None:
    settings = load_settings(PROJECT_ROOT)
    parser = argparse.ArgumentParser(description="Profile the 5-table MDM dataset.")
    parser.add_argument("--input-dir", type=Path, default=settings.mdm_data_dir)
    parser.add_argument("--output", type=Path, default=settings.profile_output_path)
    args = parser.parse_args()

    report = build_profile(args.input_dir)
    rendered = render_markdown(report, args.input_dir)
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
