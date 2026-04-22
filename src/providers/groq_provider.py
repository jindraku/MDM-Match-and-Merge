"""Groq adapter for LLM-assisted translation and reasoning tasks."""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class GroqProviderConfig:
    api_key: str
    translation_model: str
    reasoning_model: str
    abbreviation_model: str


class GroqProvider:
    """Thin adapter around the Groq SDK for translation and reasoning."""

    def __init__(self, config: GroqProviderConfig) -> None:
        self.config = config

    def _build_client(self):
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Install the `groq` package to use Groq integrations.") from exc

        return Groq(api_key=self.config.api_key)

    def _single_turn(self, model: str, system_prompt: str, user_prompt: str) -> str:
        client = self._build_client()
        completion = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content.strip()

    def translate_text(self, text: str, target_language: str = "English") -> str:
        return self._single_turn(
            model=self.config.translation_model,
            system_prompt=(
                "You normalize enterprise master data. Translate the user's text into the target language. "
                "Return only the translated text with no explanation."
            ),
            user_prompt=f"Target language: {target_language}\nText:\n{text}",
        )

    def expand_abbreviations(self, text: str) -> dict[str, str]:
        response = self._single_turn(
            model=self.config.abbreviation_model,
            system_prompt=(
                "You expand business and address abbreviations in company master data. "
                "Return strict JSON with keys `expanded_text` and `reason`."
            ),
            user_prompt=f"Expand abbreviations in this text:\n{text}",
        )
        parsed = json.loads(response)
        return {
            "expanded_text": parsed.get("expanded_text", text),
            "reason": parsed.get("reason", ""),
        }

    def verify_name_equivalence(self, left_name: str, right_name: str) -> str:
        return self._single_turn(
            model=self.config.reasoning_model,
            system_prompt=(
                "You compare company names in an MDM match workflow. "
                "State whether they likely refer to the same business entity and explain briefly."
            ),
            user_prompt=f"Name A: {left_name}\nName B: {right_name}",
        )

    def verify_name_equivalence_structured(self, left_name: str, right_name: str) -> dict:
        response = self._single_turn(
            model=self.config.reasoning_model,
            system_prompt=(
                "You compare company names for enterprise MDM duplicate detection. "
                "Return strict JSON only with keys: status, relationship, score, reason. "
                "Allowed status values are: "
                "exact_business_match, likely_match, parent_subsidiary_related, "
                "trade_name_related, no_name_match. "
                "The score must be an integer from 0 to 40."
            ),
            user_prompt=f"Name A: {left_name}\nName B: {right_name}",
        )
        parsed = json.loads(response)
        return {
            "status": parsed.get("status", "no_name_match"),
            "relationship": parsed.get("relationship", "unknown"),
            "score": int(parsed.get("score", 0)),
            "reason": parsed.get("reason", ""),
        }

    def analyze_address_pair_structured(self, left_address: str, right_address: str) -> dict:
        response = self._single_turn(
            model=self.config.reasoning_model,
            system_prompt=(
                "You compare addresses for enterprise MDM duplicate detection. "
                "Return strict JSON only with keys: status, issues, score, reason. "
                "Allowed status values are: "
                "same_address, near_equivalent_address, same_building_different_unit, "
                "conflicting_address, insufficient_address_data. "
                "The issues field must be a JSON array of strings. "
                "The score must be an integer from 0 to 25."
            ),
            user_prompt=f"Address A: {left_address}\nAddress B: {right_address}",
        )
        parsed = json.loads(response)
        return {
            "status": parsed.get("status", "insufficient_address_data"),
            "issues": parsed.get("issues", []),
            "score": int(parsed.get("score", 0)),
            "reason": parsed.get("reason", ""),
        }
