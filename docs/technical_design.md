Technical Design Document 
1. Introduction
1.1 Problem Statement

The existing Master Data Management (MDM) system lacks:

 - multilingual normalization
 - intelligent reasoning-based matching
 - address-aware comparison

This results in:

 - duplicate customer records
 - inconsistent data
 - poor data quality and downstream impact

1.2 Objective

Design and implement an intelligent match and merge engine that:

 - identifies duplicate company records
 - supports multilingual data
 - handles abbreviations, typos, and variations
 - assigns confidence scores
 - provides human-readable reasoning
   
2. System Overview

The system compares company records and classifies them into:

 - High Confidence Match (>85)
 - Potential Match (60–85)
 - Non-Match (<60)

The architecture follows a multi-stage pipeline:

Raw Data → Preprocessing → Embedding → Candidate Selection → Matching Engine → Scoring → Classification


3. Architecture Design
3.1 High-Level Components
Input Layer
 - MDM table (company_name, address, city, country)
Preprocessing Layer
 - normalization
 - translation
 - abbreviation expansion
Embedding Layer
 - convert records into vector representations
Candidate Generation Layer
 - similarity search to reduce comparisons
Matching Engine (5 Levels)
 - rule-based + AI-based checks
Scoring Engine
 - weighted scoring
Output Layer
 - match classification + reasoning

3.2 Architecture Diagram

```mermaid
flowchart LR
    A["MDM source table / CSV"] --> B["Profiling stage<br/>schema, language mix, duplicate rate"]
    B --> C["Preprocessing<br/>cleanup, language detection, Groq translation, abbreviation expansion"]
    C --> D["Structured text builder<br/>company || address || city || country"]
    D --> E["Embedding and candidate selection<br/>TF-IDF now, FAISS later"]
    E --> F["Level 1 exact match"]
    F --> G["Level 2 geo-distance (future)"]
    G --> H["Level 3 name verification with Groq (future scoring hook)"]
    H --> I["Level 4 address analysis"]
    I --> J["Level 5 score aggregation"]
    J --> K["Classification + reasoning output"]
```

3.3 Agent Orchestration Plan
 - Profiling agent: analyzes incoming datasets and produces schema, language distribution, and duplicate-rate reports.
 - Preprocessing agent: detects language per field, performs cleanup, and optionally calls Groq for translation and abbreviation expansion.
 - Candidate generation agent: creates record embeddings and reduces pair count using similarity threshold `p`.
 - Matching agent: runs Level 1 exact match today and will own Levels 2-5 as integrations are added.
 - Review agent: surfaces human-readable reasoning and routes borderline pairs for business review.

   
4. Data Flow
 - Raw records are ingested
 - Each record is cleaned and normalized
 - Language is detected and transliteration/placeholder translation is applied
 - Structured text is created
 - Embeddings are generated
 - Similarity search produces candidate pairs
 - Candidate pairs pass through multi-level matching
 - Final score is calculated
 - Classification and reasoning are generated


5. Preprocessing Design
5.1 Steps
Lowercasing
 - Example: ABC Co. → abc co
Trim whitespace
 - remove leading/trailing spaces
Remove punctuation
 - Co. → Co
Article removal
 - remove “the”, “a”, “an”
Abbreviation expansion
 - co → company
 - ltd → limited
Language detection (basic)
 - detect non-English strings
Translation (LLM-based future)
 Example:
 - Sociedad Internacional → International Company

5.2 Week 1 Implementation Scope
Implemented in repository:
 - field-level language detection
 - accent folding / transliteration
 - Groq-backed translation and abbreviation expansion behind environment flags
 - deterministic placeholder translation for offline fallback
 - rule-based abbreviation expansion plus optional Groq expansion
 - alternate-name normalization
  - structured record text generation

Deferred to later phases:
 - transliteration for non-Latin scripts with model assistance
 - country-specific address parsers

   
6. Embedding Design
6.1 Structured Input Format
Each record is converted into:
  company: {name} || address: {address} || city: {city} || country: {country}
6.2 Embedding Method
Current:
 - TF-IDF vectorization
Future:
 - Sentence Transformers
 - model-based embeddings if production retrieval quality needs exceed TF-IDF

   
7. Candidate Selection
7.1 Problem
Brute-force comparison:
   N(N-1)/2  → not scalable
7.2 Solution
 - cosine similarity between embeddings
 - threshold-based filtering
Example:
   similarity > 0.3 → candidate pair

   
8. Matching Engine Design
Multi-Level Matching Pipeline
Level 1 – Exact Match
   Compare cleaned company name and address
   Also allow alternate company name to satisfy the name side of the exact match
Example:
   abc company == abc company
   12 king street == 12 king street
Level 2 – Geo Distance (future)
   convert address → coordinates
   check distance threshold
Level 3 – Name Verification (future LLM)
   semantic similarity of company names
Example:
   "IBM" vs "International Business Machines"
Level 4 – Address Analysis
   token overlap
   partial matching
   street similarity
Level 5 – Final Aggregation
   combine all scores

   
9. Scoring Model
9.1 Weight Distribution
Component	                        Weight
Exact match	                          40
Embedding similarity	                 35
City/Country match	                 10
Address overlap	                    15
Total                               100

9.2 Example
Embedding similarity = 0.9 → 31 points
Exact match = yes → +40
City match = yes → +10
Address overlap = 0.8 → +12
Final score = 93


10. Classification Logic
   Score > 85 → High Confidence Match
   60–85 → Potential Match
   <60 → Non-Match


11. Output Design
Each match result contains:

{
  "record_id_1": 1,
  "record_id_2": 2,
  "similarity": 0.91,
  "final_score": 93,
  "classification": "High Confidence Match",
  "reasoning": [
    "Exact name match",
    "Same address",
    "High embedding similarity"
  ]
}

11.1 Human-Readable Reasoning
The Week 1 engine returns plain-language reasons such as:
 - Level 1 exact match succeeded on normalized company name and address
 - Embedding similarity contributed X/Y points
 - City and country are an exact normalized match
 - Multilingual preprocessing was applied through language detection and transliteration

12.1 Repository Module Contracts
`src/preprocessing.py`
 - input: raw CSV record
 - output: processed record with normalized fields and structured text

`src/embedding.py`
 - input: processed records
 - output: TF-IDF vectors and candidate record pairs above threshold p

`src/matcher.py`
 - input: candidate pair + processed record map
 - output: score, classification, exact-match flag, and reasoning

`src/main.py`
 - orchestrates CSV load → preprocessing → candidate generation → scoring output

12. Technology Stack
Component	                                                Technology
Language                                                      	Python
Embeddings	                                                   TF-IDF
Similarity	                                                   cosine similarity
Data handling	                                                pandas
ML	                                                            scikit-learn
Future AI	                                                   LLM APIs

12.2 Confirmed Tool and API Selections
LLM provider
 - Groq Chat Completions API
 - Translation model: `llama-3.3-70b-versatile`
 - Complex-case reasoning model: `llama-3.3-70b-versatile`
 - Abbreviation expansion model: `llama-3.3-70b-versatile`

Geo provider
 - Google Maps Geocoding API for lat/long retrieval
 - Google Address Validation API for future postal normalization

Similarity infrastructure
 - Week 1 local baseline: scikit-learn TF-IDF
 - Production scale-up path: FAISS

12.3 Environment Provisioning Status
Repository now includes:
 - dependency definition in `requirements.txt`
 - local environment template in `.env.example`
 - `Makefile` run/test targets
 - `Dockerfile` for containerized execution
 - GitHub Actions CI workflow in `.github/workflows/ci.yml`
 - integration-ready provider adapters in `src/providers/`

13. Limitations
 - no Geo API integration
 - Groq integration requires API key and is disabled by default
 - offline translation fallback is heuristic and intentionally lightweight
 - no fuzzy legal-entity hierarchy handling yet
 - sample dataset is small and local-only

   
14. Future Enhancements
 - add address geocoding
 - use FAISS or vector DB
 - scale to large datasets
 - add UI dashboard

   
15. Conclusion
The proposed system provides a scalable and intelligent solution for identifying duplicate customer records by combining:
 - preprocessing
 - embeddings
 - multi-level matching
 - scoring
This significantly improves data quality and reduces duplication in MDM systems.
