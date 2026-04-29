"""Score address variants using Azure Maps when available."""

from __future__ import annotations

from src.mdm_loader import AddressVariant, PartyGroup
from src.scoring.common import RankedVariant


CONFIDENCE_TO_SCORE = {
    "HIGH": 0.95,
    "MEDIUM": 0.75,
    "LOW": 0.55,
}


def _rule_based_score(address: AddressVariant) -> tuple[float, str]:
    score = 0.0
    reasons: list[str] = []

    if address.address_line_one:
        score += 35
        reasons.append("Address line one is present.")
    if address.city:
        score += 20
        reasons.append("City is present.")
    if address.postal_code:
        score += 20
        reasons.append("Postal code is present.")
    if address.country_code or address.country_name:
        score += 10
        reasons.append("Country is present.")
    if address.is_standardized:
        score += 10
        reasons.append("Address is marked standardized in the source.")
    if address.is_primary.upper() == "Y":
        score += 5
        reasons.append("Address is flagged primary.")

    return min(100.0, score), " ".join(reasons)


def _score_with_azure(address: AddressVariant, azure_provider) -> tuple[float, str]:
    try:
        response = azure_provider.geocode_address(
            address_line=", ".join(
                part for part in [address.address_line_one, address.address_line_two, address.address_line_three] if part
            ),
            locality=address.city,
            admin_district=address.state_code,
            postal_code=address.postal_code,
            country_region=address.country_code or address.country_name,
        )
    except Exception:
        return _rule_based_score(address)

    feature = None
    if "features" in response:
        features = response.get("features", [])
        feature = features[0] if features else None
        properties = feature.get("properties", {}) if feature else {}
        base_score = CONFIDENCE_TO_SCORE.get(str(properties.get("confidence", "")).upper(), 0.6)
        match_codes = properties.get("matchCodes", []) or []
        formatted_address = properties.get("address", {}).get("formattedAddress", "")
    else:
        results = response.get("results", [])
        feature = results[0] if results else None
        base_score = float(feature.get("score", 0.6)) if feature else 0.6
        match_codes = feature.get("matchCodes", []) if feature else []
        formatted_address = feature.get("address", {}).get("freeformAddress", "") if feature else ""

    adjustments = 0.0
    reasons = [f"Azure Maps returned match codes {match_codes or ['none']}."]
    if "Good" in match_codes:
        adjustments += 0.1
    if "Ambiguous" in match_codes:
        adjustments -= 0.15
    if "UpHierarchy" in match_codes:
        adjustments -= 0.2
    if address.is_primary.upper() == "Y":
        adjustments += 0.03
    if address.is_standardized:
        adjustments += 0.04
    if formatted_address:
        reasons.append(f"Best formatted match: {formatted_address}.")

    score = max(0.0, min(1.0, base_score + adjustments)) * 100
    return round(score, 2), " ".join(reasons)


def score_address_variants(group: PartyGroup, azure_provider=None) -> list[RankedVariant]:
    ranked: list[RankedVariant] = []
    for address in group.addresses:
        if azure_provider is not None:
            score, reasoning = _score_with_azure(address, azure_provider)
        else:
            score, reasoning = _rule_based_score(address)
        ranked.append(
            RankedVariant(
                variant_id=address.address_id,
                score=score,
                rank=0,
                reasoning=reasoning,
                payload=address,
            )
        )

    ranked.sort(key=lambda item: (-item.score, item.variant_id))
    return [
        RankedVariant(
            variant_id=item.variant_id,
            score=item.score,
            rank=index,
            reasoning=item.reasoning,
            payload=item.payload,
        )
        for index, item in enumerate(ranked, start=1)
    ]
