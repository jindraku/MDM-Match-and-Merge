# MDM Match and Merge Engine

This project now runs against the real five-table Honeywell-style MDM dataset in [`MDM- Match and Merge data/`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/MDM-%20Match%20and%20Merge%20data), assembles a golden record for each `PARTY_ID`, and then performs end-to-end pairwise duplicate matching with final scoring, classification, reasoning, validation, and calibration artifacts.

## What it does now

The current pipeline:

1. loads the five-table MDM schema
2. groups records by `PARTY_ID`
3. scores name variants from `individual`
4. scores phone variants from `electronic_address`
5. scores address variants from `party_postal_address`
6. selects the top-ranked variant from each track
7. builds one canonical record per `PARTY_ID`
8. generates cross-party candidate pairs
9. runs Levels 1-4 matching signals
10. computes a Level 5 final score and classification
11. writes golden-record, match-result, validation, and calibration outputs

## Source schema

The project uses these tables:

- `party.csv`
- `individual.csv`
- `electronic_address.csv`
- `party_address.csv`
- `party_postal_address.csv`

The `party_address -> party_postal_address` relationship is joined through `PARTY_POSTAL_ADDR_ID`, and all outputs are grouped by `PARTY_ID`.

## Scoring tracks

### Name quality scorer

- compares `FIRST_NAME + MIDDLE_NAME + LAST_NAME` against `PARTY_NAME`
- uses Groq when configured
- falls back to rule-based normalization, token overlap, and string similarity

### Phone quality scorer

- uses `phonenumbers` when available
- checks parseability, validity, country code, and plausible digit length
- falls back to rule-based scoring if parsing fails

### Address quality scorer

- is wired for Azure Maps geocoding quality checks
- uses address completeness and source flags as fallback scoring when the API is unavailable
- ranks each address variant per `PARTY_ID`

## Outputs

### Golden records

The main pipeline writes:

- [`outputs/golden_records.csv`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/outputs/golden_records.csv)

Each row contains:

- `party_id`
- `party_name`
- `best_individual_id`
- `best_phone_id`
- `best_address_id`
- plain-English reasoning for each selected track

### Match results

The end-to-end match pipeline writes:

- [`outputs/match_results.csv`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/outputs/match_results.csv)

Each row contains:

- `record_id_1`
- `record_id_2`
- `similarity`
- `exact_match`
- `name_status`
- `geo_status`
- `address_status`
- `final_score`
- `classification`
- aggregated reasoning

### Data profile

The profiling command writes:

- [`docs/data_profile.md`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/data_profile.md)

It summarizes:

- row counts by table
- schema fields
- variant distribution per `PARTY_ID`
- approximate duplicate-group rate
- quality issues in the MDM data

### Validation and calibration

The main run also updates:

- [`docs/validation_results.md`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/validation_results.md)
- [`docs/calibration_report.md`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/calibration_report.md)

## Project structure

```text
src/
  main.py
  mdm_loader.py
  golden_record.py
  match_pipeline.py
  validation.py
  calibration.py
  profiling.py
  preprocessing.py
  providers/
    groq_provider.py
    azure_maps.py
  scoring/
    address_scorer.py
    name_scorer.py
    phone_scorer.py

MDM- Match and Merge data/
docs/
tests/
requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Test and run

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Generate the MDM data profile:

```bash
python3 -m src.profiling
```

Run the full match engine POC:

```bash
python3 -m src.main
```

Or use the Make targets:

```bash
make test
make profile
make run
```

## What to expect

`python3 -m src.profiling`:

- reads the five CSV tables in [`MDM- Match and Merge data/`](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/MDM-%20Match%20and%20Merge%20data)
- prints a summary in the terminal
- updates [docs/data_profile.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/data_profile.md)

`python3 -m src.main`:

- loads the same five-table MDM dataset
- ranks individual, phone, and address variants per `PARTY_ID`
- builds canonical party records
- generates candidate pairs across parties
- computes final Level 5 scores and classifications
- writes [outputs/golden_records.csv](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/outputs/golden_records.csv)
- writes [outputs/match_results.csv](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/outputs/match_results.csv)
- updates [docs/validation_results.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/validation_results.md)
- updates [docs/calibration_report.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/calibration_report.md)

## Environment variables

The runtime now expects:

- `MDM_DATA_DIR`
- `MDM_PROFILE_OUTPUT_PATH`
- `MDM_GOLDEN_RECORD_OUTPUT_PATH`
- `MDM_MATCH_OUTPUT_PATH`
- `MDM_VALIDATION_OUTPUT_PATH`
- `MDM_CALIBRATION_OUTPUT_PATH`
- `GROQ_API_KEY`
- `AZURE_MAPS_API_KEY`

Groq and Azure Maps are optional at runtime. If keys are missing or calls fail, the scorers fall back gracefully to rule-based logic.

## Current limitations

- Azure Maps scoring is integration-ready but not live-tested here because no API key is configured in this workspace
- Groq name scoring is integration-ready but also depends on a valid API key
- `individual` and address variants do not have native row-level primary keys in the source data, so synthetic IDs are generated for ranking outputs
- validation currently uses heuristic cases from the real MDM data and should be strengthened with stakeholder-reviewed truth labels
