"""Runtime settings for local execution and future API integration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    mdm_data_dir: Path
    profile_output_path: Path
    golden_record_output_path: Path
    match_output_path: Path
    validation_output_path: Path
    calibration_output_path: Path
    enable_llm_translation: bool
    enable_llm_abbreviation_expansion: bool
    groq_api_key: str
    groq_translation_model: str
    groq_reasoning_model: str
    groq_abbreviation_model: str
    azure_maps_api_key: str
    azure_maps_geocoding_base_url: str
    azure_maps_api_version: str


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
        mdm_data_dir=project_root / os.getenv("MDM_DATA_DIR", "MDM- Match and Merge data"),
        profile_output_path=project_root / os.getenv("MDM_PROFILE_OUTPUT_PATH", "docs/data_profile.md"),
        golden_record_output_path=project_root / os.getenv(
            "MDM_GOLDEN_RECORD_OUTPUT_PATH",
            "outputs/golden_records.csv",
        ),
        match_output_path=project_root / os.getenv(
            "MDM_MATCH_OUTPUT_PATH",
            "outputs/match_results.csv",
        ),
        validation_output_path=project_root / os.getenv(
            "MDM_VALIDATION_OUTPUT_PATH",
            "docs/validation_results.md",
        ),
        calibration_output_path=project_root / os.getenv(
            "MDM_CALIBRATION_OUTPUT_PATH",
            "docs/calibration_report.md",
        ),
        enable_llm_translation=_as_bool(os.getenv("MDM_ENABLE_LLM_TRANSLATION"), default=False),
        enable_llm_abbreviation_expansion=_as_bool(
            os.getenv("MDM_ENABLE_LLM_ABBREVIATION_EXPANSION"),
            default=False,
        ),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_translation_model=os.getenv("GROQ_TRANSLATION_MODEL", "llama-3.3-70b-versatile"),
        groq_reasoning_model=os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile"),
        groq_abbreviation_model=os.getenv("GROQ_ABBREVIATION_MODEL", "llama-3.3-70b-versatile"),
        azure_maps_api_key=os.getenv("AZURE_MAPS_API_KEY", ""),
        azure_maps_geocoding_base_url=os.getenv(
            "AZURE_MAPS_GEOCODING_BASE_URL",
            "https://atlas.microsoft.com/geocode",
        ),
        azure_maps_api_version=os.getenv("AZURE_MAPS_API_VERSION", "2025-01-01"),
    )


DEFAULT_RUNTIME_SETTINGS = RuntimeSettings(
    mdm_data_dir=Path("MDM- Match and Merge data"),
    profile_output_path=Path("docs/data_profile.md"),
    golden_record_output_path=Path("outputs/golden_records.csv"),
    match_output_path=Path("outputs/match_results.csv"),
    validation_output_path=Path("docs/validation_results.md"),
    calibration_output_path=Path("docs/calibration_report.md"),
    enable_llm_translation=False,
    enable_llm_abbreviation_expansion=False,
    groq_api_key="",
    groq_translation_model="llama-3.3-70b-versatile",
    groq_reasoning_model="llama-3.3-70b-versatile",
    groq_abbreviation_model="llama-3.3-70b-versatile",
    azure_maps_api_key="",
    azure_maps_geocoding_base_url="https://atlas.microsoft.com/geocode",
    azure_maps_api_version="2025-01-01",
)
