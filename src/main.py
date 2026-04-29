"""CLI entrypoint for MDM golden-record assembly."""

from __future__ import annotations

from pathlib import Path

from src.golden_record import assemble_golden_records, write_golden_records
from src.mdm_loader import load_party_groups
from src.providers.azure_maps import AzureMapsConfig, AzureMapsProvider
from src.providers.groq_provider import GroqProvider, GroqProviderConfig
from src.runtime import load_settings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main() -> None:
    settings = load_settings(PROJECT_ROOT)
    groups = load_party_groups(settings.mdm_data_dir)

    # Initialize Groq provider (LLM)
    groq_provider = None
    if settings.groq_api_key:
        groq_provider = GroqProvider(
            GroqProviderConfig(
                api_key=settings.groq_api_key,
                translation_model=settings.groq_translation_model,
                reasoning_model=settings.groq_reasoning_model,
                abbreviation_model=settings.groq_abbreviation_model,
            )
        )

    # Initialize Azure Maps provider (Address quality)
    azure_provider = None
    if settings.azure_maps_api_key:
        azure_provider = AzureMapsProvider(
            AzureMapsConfig(
                api_key=settings.azure_maps_api_key,
                geocoding_base_url=settings.azure_maps_geocoding_base_url,
                api_version=settings.azure_maps_api_version,
            )
        )

    golden_records = assemble_golden_records(
        groups,
        groq_provider=groq_provider,
        azure_provider=azure_provider,
    )
    settings.golden_record_output_path.parent.mkdir(parents=True, exist_ok=True)
    write_golden_records(settings.golden_record_output_path, golden_records)

    print("=== Golden Record Assembly ===")
    print(f"Loaded parties: {len(groups)}")
    print(f"Wrote golden records to: {settings.golden_record_output_path}")
    print()
    for record in golden_records[:10]:
        print(
            f"{record.party_id} | {record.party_name} | "
            f"best_individual={record.best_individual_id} | "
            f"best_phone={record.best_phone_id} | "
            f"best_address={record.best_address_id}"
        )


if __name__ == "__main__":
    main()
