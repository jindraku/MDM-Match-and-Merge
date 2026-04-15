"""Runtime settings for local execution and future API integration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    input_path: Path
    candidate_similarity: float
    openai_responses_model: str
    openai_reasoning_model: str
    openai_embedding_model: str
    openai_api_key: str
    google_maps_api_key: str
    google_geocoding_base_url: str
    google_address_validation_base_url: str


def load_settings(project_root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        input_path=project_root / os.getenv("MDM_INPUT_PATH", "data/sample_records.csv"),
        candidate_similarity=float(os.getenv("MDM_CANDIDATE_SIMILARITY", "0.30")),
        openai_responses_model=os.getenv("OPENAI_RESPONSES_MODEL", "gpt-5.4-mini"),
        openai_reasoning_model=os.getenv("OPENAI_REASONING_MODEL", "gpt-5.4"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""),
        google_geocoding_base_url=os.getenv(
            "GOOGLE_GEOCODING_BASE_URL",
            "https://maps.googleapis.com/maps/api/geocode/json",
        ),
        google_address_validation_base_url=os.getenv(
            "GOOGLE_ADDRESS_VALIDATION_BASE_URL",
            "https://addressvalidation.googleapis.com/v1:validateAddress",
        ),
    )
