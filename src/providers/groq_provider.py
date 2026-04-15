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
