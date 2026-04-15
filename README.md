# MDM Match Engine

MDM Match Engine is a Week 1 implementation of a multilingual, address-aware customer matching pipeline for Customer Master deduplication. It includes dataset profiling, preprocessing, embedding-based candidate generation, Level 1 exact-match detection, weighted scoring, and integration-ready Groq and Google Maps scaffolding for later matching levels.

## Current capabilities

- Dataset profiling for:
  - schema inspection
  - language distribution
  - missing-value counts
  - normalized duplicate-rate estimation
  - quality issue summaries
- Preprocessing pipeline for:
  - lowercase and whitespace cleanup
  - punctuation and article removal
  - rule-based abbreviation expansion
  - field-level language detection
  - transliteration and deterministic offline translation fallback
  - optional Groq-based translation and abbreviation expansion
- Structured record text generation using:
  - `company: {name} || address: {address} || city: {city} || country: {country}`
- TF-IDF embedding-based candidate generation with configurable threshold `p`
- Level 1 exact match detection on normalized company name and address
- Weighted confidence scoring and classification:
  - High Confidence Match: `> 85`
  - Potential Match: `60-85`
  - Non-Match: `< 60`
- Human-readable reasoning for every scored pair
- Representative multilingual, duplicate, and edge-case datasets
- CI, container, and environment scaffolding

## Project structure

- `src/config.py` - thresholds and scoring weights
- `src/runtime.py` - environment and runtime settings loader
- `src/preprocessing.py` - normalization, translation, and abbreviation expansion
- `src/embedding.py` - structured text and candidate generation
- `src/matcher.py` - level pipeline and scoring
- `src/profiling.py` - dataset profiling and Markdown report generation
- `src/main.py` - run the matching engine
- `src/providers/groq_provider.py` - Groq integration for translation and reasoning
- `src/providers/google_maps.py` - Google Maps scaffolding for future geo checks
- `data/sample_records.csv` - sample data
- `data/edge_case_records.csv` - edge case data for tuning
- `data/known_matches.csv` - expected duplicate pairs
- `docs/technical_design.md` - technical design
- `docs/provider_selections.md` - selected APIs/tools and rationale
- `docs/data_profile.md` - current dataset profile report
- `docs/environment_setup.md` - local and CI environment setup
- `docs/api_contracts.md` - pipeline input/output contracts
- `docs/team_tasks.md` - team task breakdown
- `tests/test_pipeline.py` - unit tests
- `requirements.txt` - dependencies

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

## Run the project

Generate a data profile:

```bash
python3 -m src.profiling
```

Run the match engine:

```bash
python3 -m src.main
```

Or use the Make targets:

```bash
make test
make run
make profile
```

## Environment variables

The `.env.example` file includes:

- `MDM_INPUT_PATH` for the source CSV path
- `MDM_CANDIDATE_SIMILARITY` for candidate threshold tuning
- `MDM_PROFILE_OUTPUT_PATH` for profile report output
- `MDM_ENABLE_LLM_TRANSLATION` to enable Groq-based translation
- `MDM_ENABLE_LLM_ABBREVIATION_EXPANSION` to enable Groq-based abbreviation expansion
- `GROQ_API_KEY` and Groq model names
- `GOOGLE_MAPS_API_KEY` and Google Maps endpoint settings

The app automatically loads `.env` from the repository root if present.

## Example outputs

### Profiling output

The profiling command writes a Markdown report to `docs/data_profile.md` and prints:

- record count
- schema fields
- record-level and field-level language distribution
- missing-value counts
- normalized duplicate-rate estimate
- known quality issues

### Matching output

The match engine prints:

- generated candidate pairs
- cosine similarity
- final score
- classification
- reasoning for each decision

## Provider choices

- LLM provider: Groq
- Geo provider: Google Maps Platform
- Candidate generation baseline: scikit-learn TF-IDF
- Scale-up path: FAISS or another vector index

Details are documented in [docs/provider_selections.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/provider_selections.md).

## Design references

- Technical design: [docs/technical_design.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/technical_design.md)
- API contracts: [docs/api_contracts.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/api_contracts.md)
- Environment setup: [docs/environment_setup.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/environment_setup.md)
- Current profile report: [docs/data_profile.md](/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/docs/data_profile.md)

## Current implementation status

- Field-level language detection is implemented
- Groq-based translation and abbreviation expansion are feature-flagged and API-key driven
- Deterministic translation/transliteration remains the offline fallback
- Alternate company names are considered during Level 1 exact match checks
- Candidate generation uses TF-IDF cosine similarity over the delimited record format
- CI is scaffolded with GitHub Actions
- Environment provisioning includes `.env.example`, `Makefile`, `Dockerfile`, and GitHub Actions
- Dataset profiling is available for schema, language distribution, missing values, and duplicate-rate analysis
- Final scoring currently combines exact match, embedding similarity, city/country match, and address token overlap
- Levels 2-5 are documented, but only Level 1 is fully implemented in scoring today

## Known limitations

- No live MDM table connector yet; input is CSV-based
- Groq integration is implemented but not exercised unless a valid `GROQ_API_KEY` is configured
- Google Maps integration is scaffolded but not yet used in scoring
- TF-IDF is the current candidate-generation baseline, not a production vector database
- Parent-subsidiary and deeper legal-entity reasoning are not yet implemented
