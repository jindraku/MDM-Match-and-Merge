"""Configuration for the MDM match engine."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Thresholds:
    """Scoring and candidate thresholds."""

    candidate_similarity: float = 0.30
    high_confidence_match: int = 85
    potential_match: int = 60
    near_distance_miles: float = 2.0
    far_distance_miles: float = 25.0


@dataclass(frozen=True)
class ScoringWeights:
    """Weights for the Week 1 + Week 2 matching pipeline."""

    # Week 1
    exact_match: int = 40
    embedding_similarity: int = 35
    city_country_match: int = 10
    address_overlap: int = 15

    # Week 2
    geo_distance: int = 10
    name_verification: int = 40
    address_analysis: int = 25


@dataclass(frozen=True)
class NormalizationConfig:
    """Text normalization rules."""

    articles: tuple[str, ...] = ("the", "a", "an")
    abbreviations: dict[str, str] = field(
        default_factory=lambda: {
            "co": "company",
            "corp": "corporation",
            "inc": "incorporated",
            "intl": "international",
            "ltd": "limited",
            "mfg": "manufacturing",
            "svc": "services",
            "st": "street",
            "rd": "road",
            "ave": "avenue",
            "blvd": "boulevard",
            "apt": "apartment",
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "plz": "plaza",
        }
    )


THRESHOLDS = Thresholds()
SCORING = ScoringWeights()
NORMALIZATION = NormalizationConfig()
