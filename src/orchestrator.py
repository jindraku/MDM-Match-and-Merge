"""Week 2 multi-agent orchestration for Levels 2-4."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Any

from src.config import SCORING, THRESHOLDS


@dataclass(frozen=True)
class AgentResult:
    """Standard result returned by each Week 2 agent."""

    status: str
    score: int
    reason: str
    details: dict[str, Any]


@dataclass(frozen=True)
class Week2MatchResult:
    """Combined output of the Week 2 orchestration flow."""

    record_id_1: str
    record_id_2: str
    similarity: float
    exact_match: bool
    name_result: AgentResult
    geo_result: AgentResult
    address_result: AgentResult
    reasoning: list[str]


def _safe_get(record: Any, field: str, default: str = "") -> str:
    value = getattr(record, field, default)
    if value is None:
        return default
    return str(value).strip()


def _token_set(text: str) -> set[str]:
    return {token for token in text.split() if token}


def _build_name_text(record: Any) -> str:
    return (
        _safe_get(record, "translated_company_name")
        or _safe_get(record, "normalized_company_name")
        or _safe_get(record, "company_name")
        or _safe_get(record, "raw_company_name")
    )


def _build_alt_name_text(record: Any) -> str:
    return (
        _safe_get(record, "normalized_alternate_name")
        or _safe_get(record, "alternate_name")
        or _safe_get(record, "raw_alternate_name")
    )


def _build_address_text(record: Any) -> str:
    parts = [
        _safe_get(record, "translated_address")
        or _safe_get(record, "normalized_address")
        or _safe_get(record, "address")
        or _safe_get(record, "raw_address"),
        _safe_get(record, "translated_city")
        or _safe_get(record, "normalized_city")
        or _safe_get(record, "city")
        or _safe_get(record, "raw_city"),
        _safe_get(record, "translated_country")
        or _safe_get(record, "normalized_country")
        or _safe_get(record, "country")
        or _safe_get(record, "raw_country"),
    ]
    return ", ".join([part for part in parts if part])


def _normalized_company_pool(record: Any) -> set[str]:
    values = {
        _safe_get(record, "normalized_company_name"),
        _safe_get(record, "normalized_alternate_name"),
        _safe_get(record, "translated_company_name"),
        _safe_get(record, "company_name"),
        _safe_get(record, "raw_company_name"),
    }
    return {value for value in values if value}


def _normalized_address_text(record: Any) -> str:
    return (
        _safe_get(record, "normalized_address")
        or _safe_get(record, "translated_address")
        or _safe_get(record, "address")
        or _safe_get(record, "raw_address")
    )


def _normalized_city_text(record: Any) -> str:
    return (
        _safe_get(record, "normalized_city")
        or _safe_get(record, "translated_city")
        or _safe_get(record, "city")
        or _safe_get(record, "raw_city")
    )


def _normalized_country_text(record: Any) -> str:
    return (
        _safe_get(record, "normalized_country")
        or _safe_get(record, "translated_country")
        or _safe_get(record, "country")
        or _safe_get(record, "raw_country")
    )


def exact_match(left: Any, right: Any) -> bool:
    """Week 1 exact match check reused in Week 2 orchestration."""
    left_names = _normalized_company_pool(left)
    right_names = _normalized_company_pool(right)

    same_name = bool(left_names.intersection(right_names))
    same_address = (
        _normalized_address_text(left) == _normalized_address_text(right)
        and _normalized_address_text(left) != ""
    )
    return same_name and same_address


def _haversine_miles(left: tuple[float, float], right: tuple[float, float]) -> float:
    lat1, lon1 = left
    lat2, lon2 = right

    earth_radius_miles = 3958.8

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_miles * c


def run_name_agent(left: Any, right: Any, groq_provider=None) -> AgentResult:
    """Level 3 - Company name verification agent."""
    left_name = _build_name_text(left)
    right_name = _build_name_text(right)

    if groq_provider is not None:
        try:
            result = groq_provider.verify_name_equivalence_structured(left_name, right_name)
            return AgentResult(
                status=result["status"],
                score=result["score"],
                reason=result["reason"],
                details={"relationship": result.get("relationship", "unknown")},
            )
        except Exception:
            pass

    left_names = _normalized_company_pool(left)
    right_names = _normalized_company_pool(right)

    if left_names.intersection(right_names):
        return AgentResult(
            status="exact_business_match",
            score=SCORING.name_verification,
            reason="Normalized company names or alternate names match exactly.",
            details={"relationship": "same_or_alternate_name"},
        )

    left_tokens = _token_set(_safe_get(left, "normalized_company_name") or left_name.lower())
    right_tokens = _token_set(_safe_get(right, "normalized_company_name") or right_name.lower())

    if left_tokens and right_tokens:
        overlap = len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
        if overlap >= 0.6:
            return AgentResult(
                status="likely_match",
                score=round(SCORING.name_verification * 0.7),
                reason="Company names have strong normalized token overlap.",
                details={"relationship": "token_overlap", "overlap": round(overlap, 2)},
            )

    return AgentResult(
        status="no_name_match",
        score=0,
        reason="Company names do not appear to refer to the same business entity.",
        details={"relationship": "unrelated"},
    )


def run_geo_agent(left: Any, right: Any, name_status: str, maps_provider=None) -> AgentResult:
    """Level 2 - Geo distance agent."""
    if maps_provider is None:
        return AgentResult(
            status="geo_unavailable",
            score=0,
            reason="Google Maps provider is not configured.",
            details={},
        )

    if name_status not in {
        "exact_business_match",
        "likely_match",
        "trade_name_related",
        "parent_subsidiary_related",
    }:
        return AgentResult(
            status="geo_skipped",
            score=0,
            reason="Geo-distance check skipped because names are not sufficiently related.",
            details={},
        )

    left_address = _build_address_text(left)
    right_address = _build_address_text(right)

    try:
        left_coords = maps_provider.geocode_to_lat_lng(left_address)
        right_coords = maps_provider.geocode_to_lat_lng(right_address)
    except Exception:
        return AgentResult(
            status="geo_unavailable",
            score=0,
            reason="Geocoding request failed.",
            details={},
        )

    if not left_coords or not right_coords:
        return AgentResult(
            status="geo_unavailable",
            score=0,
            reason="One or both addresses could not be geocoded.",
            details={},
        )

    distance = _haversine_miles(left_coords, right_coords)

    if distance < THRESHOLDS.near_distance_miles:
        return AgentResult(
            status="near_same_location",
            score=SCORING.geo_distance,
            reason=f"Addresses are only {distance:.2f} miles apart.",
            details={"distance_miles": round(distance, 2)},
        )

    if distance > THRESHOLDS.far_distance_miles:
        return AgentResult(
            status="same_company_different_office",
            score=2,
            reason=f"Addresses are {distance:.2f} miles apart, suggesting different offices.",
            details={"distance_miles": round(distance, 2)},
        )

    return AgentResult(
        status="ambiguous_geo",
        score=5,
        reason=f"Addresses are {distance:.2f} miles apart and require deeper review.",
        details={"distance_miles": round(distance, 2)},
    )


def run_address_agent(left: Any, right: Any, groq_provider=None) -> AgentResult:
    """Level 4 - Address deep analysis agent."""
    left_address = _build_address_text(left)
    right_address = _build_address_text(right)

    if groq_provider is not None:
        try:
            result = groq_provider.analyze_address_pair_structured(left_address, right_address)
            return AgentResult(
                status=result["status"],
                score=result["score"],
                reason=result["reason"],
                details={"issues": result.get("issues", [])},
            )
        except Exception:
            pass

    left_normalized = _normalized_address_text(left)
    right_normalized = _normalized_address_text(right)

    if left_normalized == right_normalized and left_normalized:
        return AgentResult(
            status="same_address",
            score=SCORING.address_analysis,
            reason="Normalized addresses are identical.",
            details={"issues": []},
        )

    left_tokens = _token_set(left_normalized)
    right_tokens = _token_set(right_normalized)

    if left_tokens and right_tokens:
        overlap = len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
        if overlap >= 0.7:
            return AgentResult(
                status="near_equivalent_address",
                score=round(SCORING.address_analysis * 0.7),
                reason="Addresses have strong normalized token overlap.",
                details={"issues": ["token_overlap"], "overlap": round(overlap, 2)},
            )

    if (
        _normalized_city_text(left)
        and _normalized_city_text(right)
        and _normalized_city_text(left) != _normalized_city_text(right)
        and _normalized_country_text(left) == _normalized_country_text(right)
    ):
        return AgentResult(
            status="conflicting_address",
            score=0,
            reason="Addresses conflict because the normalized cities differ.",
            details={"issues": ["city_mismatch"]},
        )

    return AgentResult(
        status="insufficient_address_data",
        score=5,
        reason="Address comparison is inconclusive with current rules.",
        details={"issues": []},
    )


def _get_candidate_attr(candidate: Any, primary: str, fallback: str = "") -> Any:
    if hasattr(candidate, primary):
        return getattr(candidate, primary)
    if fallback and hasattr(candidate, fallback):
        return getattr(candidate, fallback)
    return None


def evaluate_candidate_week2(
    candidate: Any,
    records_by_id: dict[str, Any],
    groq_provider=None,
    maps_provider=None,
) -> Week2MatchResult:
    """Run Week 2 orchestration across Levels 2-4 for one candidate pair."""
    left_record_id = _get_candidate_attr(candidate, "left_record_id")
    right_record_id = _get_candidate_attr(candidate, "right_record_id")
    similarity = float(_get_candidate_attr(candidate, "similarity") or 0.0)

    left = records_by_id[left_record_id]
    right = records_by_id[right_record_id]

    reasoning: list[str] = []

    is_exact = exact_match(left, right)
    if is_exact:
        reasoning.append("Level 1 exact match succeeded on normalized company name and address.")
    else:
        reasoning.append("Level 1 exact match did not fully align on both name and address.")

    name_result = run_name_agent(left, right, groq_provider=groq_provider)
    reasoning.append(f"Level 3 name verification: {name_result.reason}")

    geo_result = run_geo_agent(
        left,
        right,
        name_status=name_result.status,
        maps_provider=maps_provider,
    )
    reasoning.append(f"Level 2 geo-distance: {geo_result.reason}")

    address_result = run_address_agent(left, right, groq_provider=groq_provider)
    reasoning.append(f"Level 4 address analysis: {address_result.reason}")

    return Week2MatchResult(
        record_id_1=_safe_get(left, "record_id"),
        record_id_2=_safe_get(right, "record_id"),
        similarity=similarity,
        exact_match=is_exact,
        name_result=name_result,
        geo_result=geo_result,
        address_result=address_result,
        reasoning=reasoning,
    )
