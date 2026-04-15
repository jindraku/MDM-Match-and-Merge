# Data Profile

Dataset: `/Users/joshikaindrakumar/Documents/GitHub/MDM-Match-and-Merge/data/sample_records.csv`

## Summary

- Record count: 10
- Current exact duplicate pairs after normalization: 2
- Approximate duplicate rate: 40.0%

## Schema

- Fields: record_id, company_name, address, city, country, alternate_name

## Language distribution

- Record-level: {'english': 7, 'mixed_or_non_english': 3}
- Company field: {'english': 8, 'possible_non_english': 2}
- Address field: {'english': 8, 'possible_non_english': 2}

## Missing values

- {'company_name': 0, 'address': 0, 'city': 0, 'country': 0, 'alternate_name': 5}

## Known quality issues

- 3 record(s) contain multilingual or mixed-language content that need normalization.
- 2 exact duplicate pair(s) were found after normalization of company name and address.
- 5 record(s) use alternate names, indicating trade-name or alias handling is required.
- 4 record(s) use abbreviated address tokens, which can mask duplicates without expansion.
