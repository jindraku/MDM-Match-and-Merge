# MDM Match Engine

This is a starter implementation of an MDM Match and Merge engine for multilingual, address-aware customer matching.

## What this project includes

- Pre-processing pipeline
  - lowercase
  - trim
  - punctuation cleanup
  - article removal
  - abbreviation expansion
- Structured record text generation
- TF-IDF embedding-based candidate generation
- Level 1 exact match detection
- Final confidence score
- Match classification:
  - High Confidence Match: > 85
  - Potential Match: 60-85
  - Non-Match: < 60
- Human-readable reasoning
- Sample multilingual and duplicate-style dataset
- Architecture notes and task breakdown

## Project structure

- `src/config.py` - thresholds and scoring weights
- `src/preprocessing.py` - normalization and abbreviation expansion
- `src/embedding.py` - structured text and candidate generation
- `src/matcher.py` - level pipeline and scoring
- `src/main.py` - run the engine
- `data/sample_records.csv` - sample data
- `docs/technical_design.md` - technical design
- `docs/team_tasks.md` - team task breakdown
- `requirements.txt` - dependencies

## Setup

```bash
python3 -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python3 -m src.main
```

## Output

The program prints:
- generated candidate pairs
- similarity score
- level 1 exact match result
- final confidence score
- classification
- reasoning

## Notes

This version is a strong undergraduate starter project. It uses TF-IDF instead of a production vector database to keep it easy to run locally.
You can later replace TF-IDF with:
- sentence-transformers
- OpenAI embeddings
- FAISS / Pinecone / Chroma

## Current Week 1 implementation details

- Lightweight language detection identifies English vs mixed/non-English text
- Deterministic translation/transliteration placeholders normalize accented and common multilingual tokens
- Alternate company names are considered during Level 1 exact match checks
- Candidate generation uses TF-IDF cosine similarity over the delimited record format
- Final scoring combines:
  - exact match
  - embedding similarity
  - city/country match
  - address token overlap

## Suggested Week 1 scope

1. Run this project locally
2. Validate preprocessing rules on your own dataset
3. Replace sample data with MDM records
4. Tune thresholds
5. Extend Level 2-5 logic with Geo API and LLM calls
