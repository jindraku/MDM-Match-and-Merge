"""Load the 5-table MDM schema and assemble party-centered groups."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def _clean(value: object) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


@dataclass(frozen=True)
class PartyRecord:
    party_id: str
    party_name: str
    domain_code: str
    active_flag: str
    source_record_no: str


@dataclass(frozen=True)
class IndividualVariant:
    individual_id: str
    party_id: str
    first_name: str
    middle_name: str
    last_name: str
    full_name: str
    account_name: str
    prefix_name: str
    suffix_name: str

    @property
    def display_name(self) -> str:
        parts = [self.prefix_name, self.first_name, self.middle_name, self.last_name, self.suffix_name]
        composed = " ".join(part for part in parts if part).strip()
        return composed or self.full_name or self.account_name


@dataclass(frozen=True)
class PhoneVariant:
    phone_id: str
    party_id: str
    phone_text: str
    phone_type_code: str
    active_flag: str


@dataclass(frozen=True)
class AddressVariant:
    address_id: str
    party_id: str
    party_address_id: str
    party_postal_addr_id: str
    address_usage_type_code: str
    is_primary: str
    address_line_one: str
    address_line_two: str
    address_line_three: str
    city: str
    state_code: str
    postal_code: str
    country_code: str
    country_name: str
    is_standardized: str

    @property
    def freeform_address(self) -> str:
        parts = [
            self.address_line_one,
            self.address_line_two,
            self.address_line_three,
            self.city,
            self.state_code,
            self.postal_code,
            self.country_code or self.country_name,
        ]
        return ", ".join(part for part in parts if part)


@dataclass(frozen=True)
class PartyGroup:
    party: PartyRecord
    individuals: list[IndividualVariant]
    phones: list[PhoneVariant]
    addresses: list[AddressVariant]


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def load_party_groups(base_path: Path) -> list[PartyGroup]:
    party_df = _read_csv(base_path / "party.csv")
    individual_df = _read_csv(base_path / "individual.csv")
    phone_df = _read_csv(base_path / "electronic_address.csv")
    party_address_df = _read_csv(base_path / "party_address.csv")
    postal_df = _read_csv(base_path / "party_postal_address.csv")

    individual_df = individual_df.copy()
    individual_df["individual_id"] = (
        individual_df["PARTY_ID"] + "-IND-" + (individual_df.groupby("PARTY_ID").cumcount() + 1).astype(str)
    )

    address_df = party_address_df.merge(
        postal_df,
        on="PARTY_POSTAL_ADDR_ID",
        how="left",
        suffixes=("_party", "_postal"),
    )
    address_df["address_id"] = (
        address_df["PARTY_ID"] + "-ADDR-" + (address_df.groupby("PARTY_ID").cumcount() + 1).astype(str)
    )

    party_groups: list[PartyGroup] = []

    individuals_by_party = {
        party_id: frame.to_dict("records")
        for party_id, frame in individual_df.groupby("PARTY_ID", sort=False)
    }
    phones_by_party = {
        party_id: frame.to_dict("records")
        for party_id, frame in phone_df.groupby("PARTY_ID", sort=False)
    }
    addresses_by_party = {
        party_id: frame.to_dict("records")
        for party_id, frame in address_df.groupby("PARTY_ID", sort=False)
    }

    for row in party_df.to_dict("records"):
        party_id = _clean(row["PARTY_ID"])
        party = PartyRecord(
            party_id=party_id,
            party_name=_clean(row.get("PARTY_NAME")),
            domain_code=_clean(row.get("DOMAIN_CODE")),
            active_flag=_clean(row.get("ACTIVE_FLG")),
            source_record_no=_clean(row.get("RECORD_NO")),
        )

        individuals = [
            IndividualVariant(
                individual_id=_clean(record["individual_id"]),
                party_id=party_id,
                first_name=_clean(record.get("FIRST_NAME")),
                middle_name=_clean(record.get("MIDDLE_NAME")),
                last_name=_clean(record.get("LAST_NAME")),
                full_name=_clean(record.get("FULL_NAME")),
                account_name=_clean(record.get("ACCOUNT_NAME")),
                prefix_name=_clean(record.get("PREFIX_NAME")),
                suffix_name=_clean(record.get("SUFFIX_NAME")),
            )
            for record in individuals_by_party.get(party_id, [])
        ]

        phones = [
            PhoneVariant(
                phone_id=_clean(record.get("ELECTRONIC_ADDR_ID")),
                party_id=party_id,
                phone_text=_clean(record.get("ELECTRONIC_ADDR_TEXT")),
                phone_type_code=_clean(record.get("ELECTRONIC_ADDR_TYPE_CODE")),
                active_flag=_clean(record.get("ACTIVE_FLG")),
            )
            for record in phones_by_party.get(party_id, [])
        ]

        addresses = [
            AddressVariant(
                address_id=_clean(record.get("address_id")),
                party_id=party_id,
                party_address_id=_clean(record.get("PARTY_ADDRESS_ID")),
                party_postal_addr_id=_clean(record.get("PARTY_POSTAL_ADDR_ID")),
                address_usage_type_code=_clean(record.get("ADDRESS_USAGE_TYPE_CODE")),
                is_primary=_clean(record.get("IS_PRIMARY")),
                address_line_one=_clean(record.get("ADDR_LINE_ONE")),
                address_line_two=_clean(record.get("ADDR_LINE_TWO")),
                address_line_three=_clean(record.get("ADDR_LINE_THREE")),
                city=_clean(record.get("CITY")),
                state_code=_clean(record.get("STATE_CODE") or record.get("STATE_VALUE")),
                postal_code=_clean(record.get("POSTAL_CODE")),
                country_code=_clean(record.get("COUNTRY_CODE")),
                country_name=_clean(record.get("COUNTRY_NAME")),
                is_standardized=_clean(record.get("IS_STARDARDIZED")),
            )
            for record in addresses_by_party.get(party_id, [])
        ]

        party_groups.append(
            PartyGroup(
                party=party,
                individuals=individuals,
                phones=phones,
                addresses=addresses,
            )
        )

    return party_groups
