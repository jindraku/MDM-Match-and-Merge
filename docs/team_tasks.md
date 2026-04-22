# Team Tasks

## Week - 1

## Bogdan – Data Analysis
- Understand dataset
- Identify duplicates
- Create test data

## Yashwanth – Design
- Architecture design
- Documentation
- Scoring logic

## Ahmed / Alex – Preprocessing
- Data cleaning
- Normalization
- Text processing

## Joshika – Matching Engine
- Embedding generation
- Candidate selection
- Scoring and classification

## Shared Work
- Testing
- Debugging
- Final submission


## Week - 2

## Bogdan - Geo Distance Agent(Level - 2)
- Update src/providers/google_maps.py
- Implement:
    - geocode_to_lat_lng()
   - distance calculation (Haversine)
- Define rules:
    - near_same_location (< 2 miles)
    - same_company_different_office (> 25 miles)
- Handle failures (invalid address, API issues)

## Yashwanth – System Design & Orchestration
- Design multi-agent architecture
- Add fallback logic in orchestrator.py
- Define orchestration flow:
    - name → geo → address
- Create src/orchestrator.py
- Define:
    - AgentResult structure
    - Week2MatchResult structure
- Document:
    - agent interactions
    - reasoning flow

## Joshika - Name Verification Agent (Level 3)
- Update src/providers/groq_provider.py
- Implement:
    - verify_name_equivalence_structured()
- Design prompts for:
    - typos
    - abbreviations
    - alternate names
    - parent-subsidiary relationships
- Parse JSON response

## Ahmed - Address Analysis Agent (Level 4)
- Implement:
    - analyze_address_pair_structured()
- Detect:
    - street variations
    - zip mismatches
    - city/state conflicts
- Generate structured output

## Alex - Integration & Execution
- Update src/main.py
- Connect:
    - preprocessing → candidates → orchestrator
- Print:
    - agent outputs
    - reasoning
- Create test cases:
    - typo match
    - same company different office
    - address mismatch

## Shared Work
- End-to-end testing of multi-agent pipeline
- Debug API integration (Groq + Google Maps)
- Validate reasoning outputs
- Prepare Week 2 demo results
