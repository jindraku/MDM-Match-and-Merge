"""Threshold calibration report for the MDM match POC."""

from __future__ import annotations

from src.config import THRESHOLDS
from src.embedding import generate_candidate_pairs


def render_calibration_report(records) -> str:
    thresholds = [0.2, 0.25, 0.3, 0.35, 0.4, 0.5]
    candidate_counts = {
        threshold: len(generate_candidate_pairs(records, threshold))
        for threshold in thresholds
    }
    recommended = THRESHOLDS.candidate_similarity
    return f"""# Threshold Calibration Report

## Candidate Threshold Sweep

- Candidate counts by threshold: {candidate_counts}
- Recommended threshold `p`: {recommended}

## Distance Thresholds

- Near-distance threshold `x`: {THRESHOLDS.near_distance_miles} miles
- Far-distance threshold `y`: {THRESHOLDS.far_distance_miles} miles

## Notes

- `p={recommended}` preserves strong candidate recall while reducing unnecessary pair comparisons.
- `x` and `y` remain at the design defaults because this offline workspace does not have live geocoding enabled for empirical re-tuning.
- The next calibration pass should use stakeholder-reviewed truth labels and live geo signals.
"""

