# Validation Results

## Summary

- Validation cases: 6
- Cases meeting expectation: 6
- Candidate threshold p: 0.3
- Near-distance threshold x: 2.0 miles
- Far-distance threshold y: 25.0 miles

## Case Review

- `86562104931718915415` vs `78971437179729157414`
  Expected: Potential Match
  Actual: Potential Match
  Final score: 65
  Rationale: Exact normalized party names with non-conflicting address evidence should not score below Potential Match.
- `31745064816837711707` vs `80509458826989478798`
  Expected: Non-Match
  Actual: Non-Match
  Final score: 0
  Rationale: Very low normalized name similarity should remain a Non-Match.
- `31745064816837711707` vs `66959897308405950035`
  Expected: Non-Match
  Actual: Non-Match
  Final score: 0
  Rationale: Very low normalized name similarity should remain a Non-Match.
- `31745064816837711707` vs `79559381425218213118`
  Expected: Non-Match
  Actual: Non-Match
  Final score: 0
  Rationale: Very low normalized name similarity should remain a Non-Match.
- `31745064816837711707` vs `15730599386666221017`
  Expected: Non-Match
  Actual: Non-Match
  Final score: 0
  Rationale: Very low normalized name similarity should remain a Non-Match.
- `31745064816837711707` vs `14726287225935641379`
  Expected: Non-Match
  Actual: Non-Match
  Final score: 0
  Rationale: Very low normalized name similarity should remain a Non-Match.

## Findings

- The pipeline now produces Level 5 final scores and classifications on the real MDM data.
- Exact-name multilingual duplicates are reaching at least Potential Match in validation checks.
- Clear low-similarity pairs remain Non-Matches under the current threshold set.

## Next Steps

- Review top-scoring cross-party pairs with business stakeholders for human validation.
- Enable Azure Maps and Groq keys to strengthen geo and semantic signals in production-like runs.
- Tune thresholds further once stakeholder-reviewed truth labels are available.