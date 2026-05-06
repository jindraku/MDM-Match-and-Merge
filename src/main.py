"""CLI entrypoint for the end-to-end MDM match engine POC."""

from __future__ import annotations

from pathlib import Path

from src.calibration import render_calibration_report
from src.golden_record import write_golden_records
from src.match_pipeline import run_end_to_end_match_pipeline, write_match_results
from src.mdm_loader import load_party_groups
from src.providers.azure_maps import AzureMapsConfig, AzureMapsProvider
from src.providers.groq_provider import GroqProvider, GroqProviderConfig
from src.runtime import load_settings
from src.validation import (
    build_validation_cases,
    render_validation_report,
    validate_match_results,
    write_validation_report,
)


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

    pipeline_output = run_end_to_end_match_pipeline(
        groups,
        settings=settings,
        groq_provider=groq_provider,
        azure_provider=azure_provider,
        maps_provider=azure_provider,
    )
    golden_records = pipeline_output.golden_records
    match_results = pipeline_output.match_results
    settings.golden_record_output_path.parent.mkdir(parents=True, exist_ok=True)
    write_golden_records(settings.golden_record_output_path, golden_records)
    write_match_results(settings.match_output_path, match_results)

    validation_cases = build_validation_cases(pipeline_output.canonical_records)
    validation_summary = validate_match_results(validation_cases, match_results)
    validation_report = render_validation_report(
        validation_summary,
        candidate_threshold=0.30,
        near_distance=2.0,
        far_distance=25.0,
    )
    write_validation_report(settings.validation_output_path, validation_report)

    calibration_report = render_calibration_report(pipeline_output.canonical_records)
    settings.calibration_output_path.write_text(calibration_report, encoding="utf-8")

    print("=== Match Engine POC ===")
    print(f"Loaded parties: {len(groups)}")
    print(f"Wrote golden records to: {settings.golden_record_output_path}")
    print(f"Wrote match results to: {settings.match_output_path}")
    print(f"Wrote validation report to: {settings.validation_output_path}")
    print(f"Wrote calibration report to: {settings.calibration_output_path}")
    print()
    print("=== Golden Record Preview ===")
    for record in golden_records[:5]:
        print(
            f"{record.party_id} | {record.party_name} | "
            f"best_individual={record.best_individual_id} | "
            f"best_phone={record.best_phone_id} | "
            f"best_address={record.best_address_id}"
        )
    print()
    print("=== Match Result Preview ===")
    for result in match_results[:5]:
        print(
            f"{result.record_id_1} <-> {result.record_id_2} | "
            f"score={result.final_score} | class={result.classification}"
        )


if __name__ == "__main__":
    main()
