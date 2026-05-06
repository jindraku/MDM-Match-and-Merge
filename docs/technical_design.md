# Technical Design – MDM Match and Merge Engine

## 1. Overview

The MDM Match and Merge Engine identifies duplicate Customer Master records using a multi-stage pipeline over the real five-table MDM schema. The system first assembles a golden record per `PARTY_ID`, then preprocesses those canonical records, generates candidate pairs, evaluates Levels 1–4, and computes a final Level 5 confidence score with classification and reasoning.

The design follows a modular and scalable architecture to support future extensions across multiple master data domains.

---

## 2. System Architecture

The system is structured as a pipeline:

```
Raw MDM Tables → Golden Record Assembly → Preprocessing → Embedding Generation → Candidate Selection → Multi-Agent Matching → Level 5 Score Aggregation → Output
```

### Components

* **MDM Loader** – joins the five-table schema and groups records by `PARTY_ID`
* **Golden Record Assembly** – ranks name, phone, and address variants
* **Preprocessing Module** – cleans and normalizes canonical records
* **Embedding Module** – generates similarity vectors
* **Candidate Generator** – filters record pairs
* **Multi-Agent Matching Engine** – evaluates candidate pairs through Levels 1–4
* **Level 5 Aggregator** – computes final score and classification
* **Output Layer** – produces match results, reasoning, validation, and calibration artifacts

---

## 3. Preprocessing Layer (Week 1)

### Responsibilities

* Language detection
* Translation (LLM-based or fallback)
* Lowercasing and trimming
* Removal of punctuation and articles
* Abbreviation expansion
* Transliteration support

### Output

Standardized records with normalized fields:

* company name
* address
* city
* country

---

## 4. Candidate Generation Layer (Week 1)

### Process

* Convert records into structured text format:

  ```
  company: {name} || address: {address} || city: {city} || country: {country}
  ```
* Generate TF-IDF embeddings
* Compute cosine similarity
* Apply threshold filtering

### Goal

Reduce O(N²) comparisons to a manageable subset of candidate pairs.

---

## 5. Multi-Agent Matching Engine

The matching engine introduces three agents to evaluate candidate pairs beyond exact matching.

### Agents

* **Level 2 – Geo Distance Agent**
* **Level 3 – Company Name Verification Agent**
* **Level 4 – Address Deep Analysis Agent**

Each agent produces:

* status
* score contribution
* reasoning

---

## 6. Orchestration Flow

The agents operate sequentially:

1. Receive candidate pair from embedding stage
2. Perform Level 1 exact match check
3. Execute Company Name Verification Agent
4. Execute Geo Distance Agent
5. Execute Address Deep Analysis Agent
6. Aggregate outputs into a 0–100 final score
7. Apply classification thresholds
8. Emit structured reasoning

---

## 7. Level 2 – Geo Distance Agent

### Purpose

Determine physical proximity between two records.

### Implementation

* Uses Azure Maps geocoding when available
* Converts addresses to latitude/longitude
* Computes distance using Haversine formula

### Rules

* Distance < 2 miles → `near_same_location`
* Distance > 25 miles → `same_company_different_office`
* Otherwise → `ambiguous_geo`

### Output Example

```
status: near_same_location
score: 10
reason: Addresses are only 0.5 miles apart
```

---

## 8. Level 3 – Company Name Verification Agent

### Purpose

Resolve semantic similarity between company names.

### Implementation

* Uses Groq LLM
* Returns structured JSON output

### Handles

* typographical errors
* abbreviations
* alternate spellings
* trade names
* multilingual variations
* parent-subsidiary relationships

### Examples

* Boieng → Boeing
* IBM → International Business Machines
* Alphabet ↔ Google

### Output Example

```
status: exact_business_match
relationship: typo
score: 40
reason: Names refer to same entity with minor spelling variation
```

---

## 9. Level 4 – Address Deep Analysis Agent

### Purpose

Analyze structured address similarity.

### Implementation

* LLM-based reasoning
* Rule-based fallback

### Checks

* zip code mismatches
* street spelling differences
* directional variations (N vs North)
* city/state mismatches
* formatting inconsistencies

### Output Example

```
status: same_address
score: 25
reason: Addresses match after normalization
```

---

## 10. Level 5 Final Scoring

The final scorer combines:

* Level 1 exact match
* embedding similarity
* Level 2 geo distance
* Level 3 name verification
* Level 4 address analysis

Current thresholds:

* High Confidence Match: `>85`
* Potential Match: `60–85`
* Non-Match: `<60`

The pipeline also applies penalties for:

* name conflict
* address conflict
* same company but different office

## 11. Data Flow

```
Raw MDM Tables  
→ Golden Record Assembly
→ Preprocessing  
→ Embedding Generation  
→ Candidate Selection  
→ Multi-Agent Matching  
→ Level 5 Final Score  
→ Classification + Reasoning  
```

## 12. Output Format

For each candidate pair:

* record_id_1
* record_id_2
* similarity score
* exact match flag
* name agent result
* geo agent result
* address agent result
* final score
* classification
* reasoning log

## 13. Example Output

```
A101 vs B442
Similarity: 0.91

Name: exact_business_match
Geo: near_same_location
Address: same_address
Final score: 93
Classification: High Confidence Match

Reasoning:
- Names refer to same entity
- Addresses are geographically close
- Address components match after normalization
```

## 14. Validation and Calibration

The repository now generates:

* `docs/validation_results.md`
* `docs/calibration_report.md`

These artifacts document:

* expected vs actual classifications on heuristic validation cases
* candidate-threshold sweep results
* selected threshold values `p`, `x`, and `y`
* next-step recommendations for stakeholder review

## 15. Limitations

* Geo API requires valid and complete addresses
* LLM responses may vary slightly
* Validation currently uses heuristic cases rather than stakeholder-approved truth labels
* Parent-subsidiary logic depends on LLM interpretation

## 16. Technology Stack

* Python
* Groq (LLM provider)
* Azure Maps
* TF-IDF embeddings
* Cosine similarity

## 17. Summary

The current POC provides scoring, classification, reasoning, validation, and calibration over the real MDM schema. It is ready for the next step of stakeholder walkthrough and truth-label-based threshold tuning.
