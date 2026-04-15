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

   
4. Data Flow
 - Raw records are ingested
 - Each record is cleaned and normalized
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

   
6. Embedding Design
6.1 Structured Input Format
Each record is converted into:
  company: {name} || address: {address} || city: {city} || country: {country}
6.2 Embedding Method
Current:
 - TF-IDF vectorization
Future:
 - Sentence Transformers
 - OpenAI embeddings

   
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

12. Technology Stack
Component	                                                Technology
Language                                                      	Python
Embeddings	                                                   TF-IDF
Similarity	                                                   cosine similarity
Data handling	                                                pandas
ML	                                                            scikit-learn
Future AI	                                                   LLM APIs

13. Limitations
 - no real-time LLM integration yet
 - no Geo API integration
 - limited translation capability
 - small dataset

   
14. Future Enhancements
 - integrate OpenAI / LLM APIs
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
