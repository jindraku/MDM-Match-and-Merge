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

    def geocode_to_lat_lng(self, address: str) -> tuple[float, float] | None:
        """Convert an address into a latitude/longitude tuple."""
        try:
            response = self.geocode_address(address)
            results = response.get("results", [])
            if not results:
                return None

            location = results[0].get("geometry", {}).get("location", {})
            lat = location.get("lat")
            lng = location.get("lng")

            if lat is None or lng is None:
                return None

            return float(lat), float(lng)

        except Exception:
            return None

    def get_distance_miles(
        self,
        coord_a: tuple[float, float],
        coord_b: tuple[float, float],
    ) -> float:
        """Compute distance in miles between two coordinates using Haversine."""
        from math import atan2, cos, radians, sin, sqrt

        lat1, lon1 = coord_a
        lat2, lon2 = coord_b

        earth_radius_miles = 3958.8

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius_miles * c
