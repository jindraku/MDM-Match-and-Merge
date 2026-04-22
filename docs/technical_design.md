# Technical Design – MDM Match and Merge Engine

## 1. Overview

The MDM Match and Merge Engine is designed to identify duplicate Customer Master records using a multi-stage pipeline. The system processes multilingual, inconsistent data and applies a combination of preprocessing, embedding-based filtering, and multi-agent reasoning to evaluate candidate record pairs.

The design follows a modular and scalable architecture to support future extensions across multiple master data domains.

---

## 2. System Architecture

The system is structured as a pipeline:

```
Raw Data → Preprocessing → Embedding Generation → Candidate Selection → Multi-Agent Matching → Output
```

### Components

* **Preprocessing Module** – cleans and normalizes input data
* **Embedding Module** – generates similarity vectors
* **Candidate Generator** – filters record pairs
* **Multi-Agent Matching Engine (Week 2)** – evaluates candidate pairs
* **Output Layer** – produces structured reasoning

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

## 5. Multi-Agent Matching Engine (Week 2)

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
6. Aggregate outputs into structured reasoning

---

## 7. Level 2 – Geo Distance Agent

### Purpose

Determine physical proximity between two records.

### Implementation

* Uses Google Maps Geocoding API
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

## 10. Data Flow

```
Raw Records  
→ Preprocessing  
→ Embedding Generation  
→ Candidate Selection  
→ Multi-Agent Matching  
→ Agent Outputs + Reasoning  
```

---

## 11. Output Format (Week 2)

For each candidate pair:

* record_id_1
* record_id_2
* similarity score
* exact match flag
* name agent result
* geo agent result
* address agent result
* reasoning log

---

## 12. Example Output

```
A101 vs B442
Similarity: 0.91

Name: exact_business_match
Geo: near_same_location
Address: same_address

Reasoning:
- Names refer to same entity
- Addresses are geographically close
- Address components match after normalization
```

---

## 13. Limitations

* Geo API requires valid and complete addresses
* LLM responses may vary slightly
* No final confidence scoring (Week 3)
* Parent-subsidiary logic depends on LLM interpretation

---

## 14. Future Work (Week 3)

* Final confidence score computation (0–100)
* Classification:

  * High Confidence Match
  * Potential Match
  * Non-Match
* Business rule enforcement
* Merge decision logic
* Performance optimization (FAISS / vector DB)

---

## 15. Technology Stack

* Python
* Groq (LLM provider)
* Google Maps API
* TF-IDF embeddings
* Cosine similarity

---

## 16. Summary

The Week 2 design introduces a multi-agent architecture that enhances traditional matching by incorporating semantic reasoning and spatial validation. This approach improves matching accuracy and provides explainable results for enterprise MDM systems.
