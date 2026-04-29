"""Score phone variants using phonenumbers when available."""

from __future__ import annotations

from src.mdm_loader import PartyGroup, PhoneVariant
from src.scoring.common import RankedVariant


COUNTRY_HINTS = {
    "US": "US",
    "USA": "US",
    "UNITED STATES": "US",
    "FR": "FR",
    "FRANCE": "FR",
    "PL": "PL",
    "POLAND": "PL",
    "CN": "CN",
    "CHINA": "CN",
    "IN": "IN",
    "INDIA": "IN",
    "GB": "GB",
    "UK": "GB",
    "UNITED KINGDOM": "GB",
}


def _region_hint(group: PartyGroup) -> str | None:
    for address in group.addresses:
        for candidate in (address.country_code, address.country_name):
            normalized = candidate.strip().upper()
            if normalized in COUNTRY_HINTS:
                return COUNTRY_HINTS[normalized]
    return None


def _fallback_score(phone: PhoneVariant) -> tuple[float, str]:
    digits = "".join(char for char in phone.phone_text if char.isdigit())
    score = 0.0
    reasons: list[str] = []

    if phone.phone_text.startswith("+"):
        score += 20
        reasons.append("Includes international prefix.")
    if 10 <= len(digits) <= 15:
        score += 45
        reasons.append("Digit count is plausible.")
    elif 7 <= len(digits) < 10:
        score += 25
        reasons.append("Digit count is partial but still usable.")
    else:
        reasons.append("Digit count is weak for a production phone number.")
    if phone.active_flag.upper() == "Y":
        score += 15
        reasons.append("Phone is marked active.")
    if phone.phone_type_code:
        score += 10
        reasons.append("Phone type code is populated.")

    return min(100.0, score), " ".join(reasons)


def _score_with_library(phone: PhoneVariant, region_hint: str | None) -> tuple[float, str]:
    try:
        import phonenumbers
    except ImportError:
        return _fallback_score(phone)

    reasons: list[str] = []
    try:
        parsed = phonenumbers.parse(phone.phone_text, region_hint)
    except Exception:
        return _fallback_score(phone)

    score = 0.0
    if phonenumbers.is_possible_number(parsed):
        score += 30
        reasons.append("Phone parses to a possible number.")
    if phonenumbers.is_valid_number(parsed):
        score += 35
        reasons.append("Phone parses to a valid number.")
    if parsed.country_code:
        score += 15
        reasons.append("Country code is available.")

    national_number = str(parsed.national_number or "")
    if 7 <= len(national_number) <= 12:
        score += 10
        reasons.append("National number length is plausible.")

    if phone.active_flag.upper() == "Y":
        score += 10
        reasons.append("Phone is marked active.")

    return min(100.0, score), " ".join(reasons) or "Parsed by phonenumbers."


def score_phone_variants(group: PartyGroup) -> list[RankedVariant]:
    hint = _region_hint(group)
    ranked = []
    for phone in group.phones:
        score, reasoning = _score_with_library(phone, hint)
        ranked.append(
            RankedVariant(
                variant_id=phone.phone_id,
                score=score,
                rank=0,
                reasoning=reasoning,
                payload=phone,
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
