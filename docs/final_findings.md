# Final Findings and Next Steps

## Current POC Status

- The project now loads the real five-table MDM schema and groups records by `PARTY_ID`.
- It assembles a golden record per party across name, phone, and address tracks.
- It generates pairwise candidate matches across canonical party records.
- It computes a Level 5 final score, classification, and reasoning for each candidate pair.
- It produces validation and calibration artifacts from the actual MDM data.

## Results Snapshot

- Golden record output: `outputs/golden_records.csv`
- Pairwise match output: `outputs/match_results.csv`
- Validation report: `docs/validation_results.md`
- Calibration report: `docs/calibration_report.md`

## Key Findings

- The current threshold set successfully elevates strong multilingual exact-name duplicates into `Potential Match`.
- Clear low-similarity pairs remain `Non-Match` under the current rules.
- Address and geo quality will improve materially once live Azure Maps keys are available.
- Semantic name scoring will improve once Groq is enabled in a production-like environment.

## Stakeholder Walkthrough Focus

- Review the top-scoring candidate pairs in `outputs/match_results.csv`.
- Confirm whether `Potential Match` should be the correct business outcome for exact-name duplicates with sparse address evidence.
- Validate whether current penalties for conflicting address evidence are strict enough.
- Decide whether additional business rules are needed for moved individuals, alias patterns, and parent-subsidiary cases.

## Recommended Next Steps

1. Enable Groq and Azure Maps keys and rerun the pipeline.
2. Collect stakeholder-reviewed truth labels for the top candidate pairs.
3. Recalibrate thresholds `p`, `x`, and `y` using reviewed labels.
4. Expand validation beyond heuristic cases into a maintained benchmark set.
5. Decide whether the production merge workflow should consume pairwise match results, golden records, or both.
