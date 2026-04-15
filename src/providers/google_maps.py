"""Google Maps API scaffolding for future address-aware matching levels."""

from __future__ import annotations

from dataclasses import dataclass
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class GoogleMapsConfig:
    api_key: str
    geocoding_base_url: str
    address_validation_base_url: str


class GoogleMapsProvider:
    """HTTP adapter for Google geocoding and address validation."""

    def __init__(self, config: GoogleMapsConfig) -> None:
        self.config = config

    def geocode_address(self, address: str) -> dict:
        query = urlencode({"address": address, "key": self.config.api_key})
        request = Request(f"{self.config.geocoding_base_url}?{query}")
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    def validate_address(self, address_lines: list[str], region_code: str = "US") -> dict:
        payload = json.dumps(
            {
                "address": {
                    "regionCode": region_code,
                    "addressLines": address_lines,
                }
            }
        ).encode("utf-8")
        request = Request(
            f"{self.config.address_validation_base_url}?key={self.config.api_key}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
