# MDM Match and Merge Engine

## Problem Statement

Honeywell's existing Master Data Management (MDM) system lacks multilingual normalization, reasoning-based matching, and address-aware validation. This leads to inconsistent and duplicate Customer Master records, reducing data quality, operational efficiency, and decision-making accuracy.

---

## Project Overview

This project builds an **enterprise-grade MDM Match and Merge Engine** that identifies duplicate Customer Master records using:

* multilingual normalization
* LLM-based reasoning
* address-aware validation
* embedding-based candidate generation

The system compares company records, assigns a **confidence score (0–100)**, and classifies each pair as:

* **High Confidence Match (>85)**
* **Potential Match (60–85)**
* **Non-Match (<60)**

Each decision includes **human-readable reasoning**.

---

## Goal

Develop a **multi-level matching pipeline**:

```
Preprocessing → Candidate Selection → Multi-Level Matching → Scoring → Classification → Reasoning
```

The system avoids brute-force comparisons and supports scalable, intelligent matching across multilingual datasets.

---

## Pipeline Architecture

### 1. Preprocessing Layer

* Language detection (field-level)
* Translation (LLM + fallback)
* Transliteration
* Lowercasing and whitespace normalization
* Punctuation and article removal
* Abbreviation expansion

---

### 2. Candidate Generation Layer

* Structured record format:

  ```
  company: {name} || address: {address} || city: {city} || country: {country}
  ```
* TF-IDF embeddings
* Cosine similarity
* Threshold-based filtering (`p`)
* Reduces O(N²) comparisons

---

### 3. Multi-Level Matching Engine

#### Level 1 — Exact Match

* Exact match on cleaned company name + address

---

#### Level 2 — Geo Distance Agent

* Uses Google Maps API
* Rules:

  * Same name + distance < 2 miles → strong match
  * Same name + distance > 25 miles → same company, different office

---

#### Level 3 — Company Name Verification Agent

LLM-based reasoning for:

* typos
* abbreviations
* alternate names
* trade names
* multilingual variations
* transliteration
* parent-subsidiary relationships

**Examples:**

* Boieng → Boeing
* IBM → International Business Machines
* Alphabet ↔ Google

---

#### Level 4 — Address Deep Analysis Agent

Checks:

* zip code mismatches
* street spelling differences
* directional variations (N vs North)
* street types (St vs Street)
* suite/unit differences
* city/state mismatches
* formatting inconsistencies

---

#### Level 5 — Final Score Computation

* Aggregates signals from Levels 1–4
* Produces final confidence score (0–100)

---

## Multi-Agent Orchestration Flow

1. Receive candidate pair from embedding stage
2. Run Company Name Verification Agent
3. Run Geo Distance Agent
4. Run Address Analysis Agent
5. Aggregate signals
6. Compute final score
7. Classify result
8. Generate reasoning

---

## Scoring Mechanism

### Weights

* Embedding similarity: 0–10
* Level 1 Exact Match: 0–15
* Level 2 Geo Distance: 0–10
* Level 3 Name Verification: 0–40
* Level 4 Address Analysis: 0–25

### Penalties

* Name conflict: −30
* Address conflict: −20
* Same company, different office: −10

---

## Classification

* **High Confidence Match:** >85
* **Potential Match:** 60–85
* **Non-Match:** <60

---

## Business Rules

* Same company but different office is **not automatically a duplicate**
* Parent-subsidiary relationships are identified but **not merged automatically**
* Strong name mismatch overrides address similarity
* Minor address variations do not block matches if name evidence is strong

---

## Input and Output

### Input

* Record A (company + address)
* Record B (company + address)
* Embedding similarity score
* Level 1 exact match result

### Output

* Confidence score (0–100)
* Classification
* Agent-level evidence
* Human-readable reasoning

---

## Example Scenarios

1. **Boieng vs Boeing (same address)**
   → High Confidence Match

2. **Google CA vs Google NY**
   → Same company, different office

3. **Same company, zip typo**
   → Potential Match

4. **Alphabet vs Google**
   → Related entity (not duplicate)

5. **Delta Plumbing vs Delta Airlines**
   → Non-Match

---

## Project Structure

```
src/
  config.py
  runtime.py
  preprocessing.py
  embedding.py
  matcher.py
  scoring.py
  orchestrator.py
  profiling.py
  main.py
  providers/
    groq_provider.py
    google_maps.py

data/
docs/
tests/
requirements.txt
```

---

## Technologies Used

* **LLM Provider:** Groq
* **Geo API:** Google Maps Platform
* **Embeddings:** TF-IDF (baseline)
* **Future Scale:** FAISS / vector DB
* **Language Detection:** rule-based + libraries

---

## Week-wise Implementation

### Week 1 — Preprocessing & Candidate Generation

* Data profiling
* Multilingual preprocessing
* Embedding generation
* Candidate pair selection
* Level 1 exact match

---

### Week 2 — Multi-Agent Matching Engine

* Geo-distance agent
* Company name verification agent (LLM)
* Address deep analysis agent
* Multi-agent orchestration

---

### Week 3 — Scoring & Integration

* Final score computation
* Classification logic
* Reasoning generation
* End-to-end validation
* Performance tuning

---

## Current Status

* Preprocessing pipeline implemented
* Candidate generation using TF-IDF
* Level 1 exact match complete
* Multi-agent design completed
* LLM and Geo integrations scaffolded
* Scoring and classification logic defined

---

## Known Limitations

* CSV-based input (no live MDM connector yet)
* Geo API not fully integrated into scoring
* LLM reasoning partially implemented
* TF-IDF not suitable for large-scale production
* Parent-subsidiary logic needs business rules

---

## Deliverable

A complete MDM Match Engine that performs:

* preprocessing
* candidate generation
* multi-level matching
* scoring
* classification
* reasoning

and produces validated duplicate detection results across multilingual datasets.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run

```bash
python3 -m src.main
```

---

## Testing

```bash
pytest
```
