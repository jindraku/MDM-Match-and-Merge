"""Runtime settings for local execution and future API integration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    input_path: Path
    candidate_similarity: float
    profile_output_path: Path
    enable_llm_translation: bool
    enable_llm_abbreviation_expansion: bool
    groq_api_key: str
    groq_translation_model: str
    groq_reasoning_model: str
    groq_abbreviation_model: str
    google_maps_api_key: str
    google_geocoding_base_url: str
    google_address_validation_base_url: str


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_settings(project_root: Path) -> RuntimeSettings:
    load_env_file(project_root)
    return RuntimeSettings(
        input_path=project_root / os.getenv("MDM_INPUT_PATH", "data/sample_records.csv"),
        candidate_similarity=float(os.getenv("MDM_CANDIDATE_SIMILARITY", "0.30")),
        profile_output_path=project_root / os.getenv("MDM_PROFILE_OUTPUT_PATH", "docs/data_profile.md"),
        enable_llm_translation=_as_bool(os.getenv("MDM_ENABLE_LLM_TRANSLATION"), default=False),
        enable_llm_abbreviation_expansion=_as_bool(
            os.getenv("MDM_ENABLE_LLM_ABBREVIATION_EXPANSION"),
            default=False,
        ),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_translation_model=os.getenv("GROQ_TRANSLATION_MODEL", "llama-3.3-70b-versatile"),
        groq_reasoning_model=os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile"),
        groq_abbreviation_model=os.getenv("GROQ_ABBREVIATION_MODEL", "llama-3.3-70b-versatile"),
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


DEFAULT_RUNTIME_SETTINGS = RuntimeSettings(
    input_path=Path("data/sample_records.csv"),
    candidate_similarity=0.30,
    profile_output_path=Path("docs/data_profile.md"),
    enable_llm_translation=False,
    enable_llm_abbreviation_expansion=False,
    groq_api_key="",
    groq_translation_model="llama-3.3-70b-versatile",
    groq_reasoning_model="llama-3.3-70b-versatile",
    groq_abbreviation_model="llama-3.3-70b-versatile",
    google_maps_api_key="",
    google_geocoding_base_url="https://maps.googleapis.com/maps/api/geocode/json",
    google_address_validation_base_url="https://addressvalidation.googleapis.com/v1:validateAddress",
)
