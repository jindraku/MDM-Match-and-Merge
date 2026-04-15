# Technical Design – MDM Match Engine

## Problem Statement
The current MDM system lacks multilingual normalization and reasoning-based matching, causing duplicate customer records.

## Objective
Build a matching engine that:
- Cleans and normalizes data
- Generates candidate pairs efficiently
- Scores matches
- Classifies matches with reasoning

## Architecture
1. Input: MDM records
2. Preprocessing:
   - lowercase
   - remove punctuation
   - trim spaces
3. Embedding generation (TF-IDF)
4. Candidate pair generation (similarity-based)
5. Matching engine:
   - Level 1: exact match
6. Scoring
7. Classification

## Matching Pipeline

### Level 1 – Exact Match
Compare cleaned company name and address.

### Level 2 – (future)
Geo distance check

### Level 3 – (future)
LLM-based name verification

### Level 4 – (future)
Address deep analysis

### Level 5 – Final scoring

## Scoring
- similarity score (0–100)
- name match bonus
- location match bonus

## Output
- record pairs
- similarity score
- final score
- classification
- reasoning
