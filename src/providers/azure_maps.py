"""Azure Maps provider used for address quality scoring."""

from __future__ import annotations

from dataclasses import dataclass
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class AzureMapsConfig:
    api_key: str
    geocoding_base_url: str
    api_version: str


class AzureMapsProvider:
    """HTTP adapter for Azure Maps geocoding quality lookups."""

    def __init__(self, config: AzureMapsConfig) -> None:
        self.config = config

    def geocode_address(
        self,
        *,
        query: str = "",
        address_line: str = "",
        locality: str = "",
        admin_district: str = "",
        postal_code: str = "",
        country_region: str = "",
    ) -> dict:
        params = {
            "api-version": self.config.api_version,
            "subscription-key": self.config.api_key,
        }
        if query:
            params["query"] = query
        else:
            if address_line:
                params["addressLine"] = address_line
            if locality:
                params["locality"] = locality
            if admin_district:
                params["adminDistrict"] = admin_district
            if postal_code:
                params["postalCode"] = postal_code
            if country_region:
                params["countryRegion"] = country_region

        request = Request(f"{self.config.geocoding_base_url}?{urlencode(params)}")
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
