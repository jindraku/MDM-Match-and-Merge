"""Score name variants against the party name."""

from __future__ import annotations

from difflib import SequenceMatcher

from src.mdm_loader import IndividualVariant, PartyGroup
from src.preprocessing import normalize_text
from src.scoring.common import RankedVariant


def _token_overlap(left: str, right: str) -> float:
    left_tokens = {token for token in left.split() if token}
    right_tokens = {token for token in right.split() if token}
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))


def _rule_based_score(party_name: str, variant: IndividualVariant) -> tuple[float, str]:
    candidate = variant.display_name or variant.full_name or variant.account_name
    normalized_party = normalize_text(party_name)
    normalized_candidate = normalize_text(candidate)
    if not normalized_candidate:
        return 0.0, "Variant is missing a usable person name."

    ratio = SequenceMatcher(None, normalized_party, normalized_candidate).ratio()
    overlap = _token_overlap(normalized_party, normalized_candidate)
    score = (ratio * 0.6 + overlap * 0.4) * 100

    reasons: list[str] = []
    if normalized_party == normalized_candidate:
        score += 15
        reasons.append("Normalized individual name exactly matches PARTY_NAME.")
    elif overlap >= 0.75:
        reasons.append("Strong token overlap with PARTY_NAME.")
    else:
        reasons.append("Fallback rule-based similarity used.")

    if variant.last_name and variant.last_name.lower() in party_name.lower():
        score += 5
        reasons.append("Last name aligns with PARTY_NAME.")

    if variant.middle_name and variant.middle_name[:1].lower() in party_name.lower():
        score += 3
        reasons.append("Middle initial is represented in PARTY_NAME.")

    return min(100.0, round(score, 2)), " ".join(reasons)


def score_name_variants(group: PartyGroup, groq_provider=None) -> list[RankedVariant]:
    ranked: list[RankedVariant] = []
    party_name = group.party.party_name

    for variant in group.individuals:
        score: float
        reasoning: str
        if groq_provider is not None:
            try:
                result = groq_provider.score_individual_name_against_party_name_structured(
                    variant.display_name or variant.full_name or variant.account_name,
                    party_name,
                )
                score = float(result["score"])
                reasoning = result["reason"]
            except Exception:
                score, reasoning = _rule_based_score(party_name, variant)
        else:
            score, reasoning = _rule_based_score(party_name, variant)

        ranked.append(
            RankedVariant(
                variant_id=variant.individual_id,
                score=score,
                rank=0,
                reasoning=reasoning,
                payload=variant,
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
