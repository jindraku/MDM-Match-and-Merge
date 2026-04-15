"""Configuration for the MDM match engine."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Thresholds:
    """Scoring and candidate thresholds."""

    candidate_similarity: float = 0.30
    high_confidence_match: int = 85
    potential_match: int = 60


@dataclass(frozen=True)
class ScoringWeights:
    """Weights for the Week 1 matching pipeline."""

    exact_match: int = 40
    embedding_similarity: int = 35
    city_country_match: int = 10
    address_overlap: int = 15


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
        }
    )


THRESHOLDS = Thresholds()
SCORING = ScoringWeights()
NORMALIZATION = NormalizationConfig()
