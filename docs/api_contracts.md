# API Contracts

## Pipeline stages

### Preprocessing input

```json
{
  "record_id": "123",
  "company_name": "ABC Co.",
  "address": "12 King St.",
  "city": "London",
  "country": "UK",
  "alternate_name": "ABC Company"
}
```

### Preprocessing output

```json
{
  "record_id": "123",
  "company_language": "english",
  "address_language": "english",
  "city_language": "english",
  "country_language": "english",
  "language": "english",
  "translated_company_name": "ABC Company",
  "translated_address": "12 King Street",
  "translated_city": "London",
  "translated_country": "UK",
  "normalized_company_name": "abc company",
  "normalized_alternate_name": "abc company",
  "normalized_address": "12 king street",
  "normalized_city": "london",
  "normalized_country": "uk",
  "structured_text": "company: abc company || address: 12 king street || city: london || country: uk"
}
```

### Candidate pair output

```json
{
  "left_record_id": "123",
  "right_record_id": "456",
  "similarity": 0.91
}
```

### Match result output

```json
{
  "record_id_1": "123",
  "record_id_2": "456",
  "similarity": 0.91,
  "final_score": 93,
  "classification": "High Confidence Match",
  "exact_match": true,
  "reasoning": [
    "Level 1 exact match succeeded on normalized company name and address.",
    "Embedding similarity contributed 31.9/35 points."
  ]
}
```

## Future external service contracts

### Groq translation and reasoning request
- Input: normalized company and address context
- Output: translated text, explanation, or semantic equivalence decision
- Planned use: Levels 3 and 5

### Google geocoding request
- Input: full normalized address string
- Output: latitude, longitude, formatted address, place ID
- Planned use: Level 2 geo-distance scoring
