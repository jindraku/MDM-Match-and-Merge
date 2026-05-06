# Threshold Calibration Report

## Candidate Threshold Sweep

- Candidate counts by threshold: {0.2: 14, 0.25: 12, 0.3: 8, 0.35: 6, 0.4: 6, 0.5: 3}
- Recommended threshold `p`: 0.3

## Distance Thresholds

- Near-distance threshold `x`: 2.0 miles
- Far-distance threshold `y`: 25.0 miles

## Notes

- `p=0.3` preserves strong candidate recall while reducing unnecessary pair comparisons.
- `x` and `y` remain at the design defaults because this offline workspace does not have live geocoding enabled for empirical re-tuning.
- The next calibration pass should use stakeholder-reviewed truth labels and live geo signals.
