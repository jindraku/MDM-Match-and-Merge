"""Golden-record assembly across names, phones, and addresses."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.mdm_loader import PartyGroup
from src.scoring.address_scorer import score_address_variants
from src.scoring.name_scorer import score_name_variants
from src.scoring.phone_scorer import score_phone_variants


@dataclass(frozen=True)
class GoldenRecord:
    party_id: str
    party_name: str
    best_individual_id: str
    best_phone_id: str
    best_address_id: str
    individual_reasoning: str
    phone_reasoning: str
    address_reasoning: str


def assemble_golden_records(
    groups: list[PartyGroup],
    *,
    groq_provider=None,
    azure_provider=None,
) -> list[GoldenRecord]:
    golden_records: list[GoldenRecord] = []
    for group in groups:
        ranked_names = score_name_variants(group, groq_provider=groq_provider)
        ranked_phones = score_phone_variants(group)
        ranked_addresses = score_address_variants(group, azure_provider=azure_provider)

        best_name = ranked_names[0] if ranked_names else None
        best_phone = ranked_phones[0] if ranked_phones else None
        best_address = ranked_addresses[0] if ranked_addresses else None

        golden_records.append(
            GoldenRecord(
                party_id=group.party.party_id,
                party_name=group.party.party_name,
                best_individual_id=best_name.variant_id if best_name else "",
                best_phone_id=best_phone.variant_id if best_phone else "",
                best_address_id=best_address.variant_id if best_address else "",
                individual_reasoning=best_name.reasoning if best_name else "No individual variants available.",
                phone_reasoning=best_phone.reasoning if best_phone else "No phone variants available.",
                address_reasoning=best_address.reasoning if best_address else "No address variants available.",
            )
        )
    return golden_records


def write_golden_records(path: Path, records: list[GoldenRecord]) -> None:
    fieldnames = [
        "party_id",
        "party_name",
        "best_individual_id",
        "best_phone_id",
        "best_address_id",
        "individual_reasoning",
        "phone_reasoning",
        "address_reasoning",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)
