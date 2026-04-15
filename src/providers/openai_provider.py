"""OpenAI adapter scaffolding for future LLM-assisted matching levels."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenAIProviderConfig:
    api_key: str
    responses_model: str
    reasoning_model: str
    embedding_model: str


class OpenAIProvider:
    """Thin adapter around OpenAI for future translation and reasoning tasks."""

    def __init__(self, config: OpenAIProviderConfig) -> None:
        self.config = config

    def _build_client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the `openai` package to use OpenAI integrations.") from exc

        return OpenAI(api_key=self.config.api_key)

    def translate_text(self, text: str, target_language: str = "English") -> str:
        client = self._build_client()
        response = client.responses.create(
            model=self.config.responses_model,
            input=(
                f"Translate the following business master data text into {target_language}. "
                f"Return only the translated text.\n\n{text}"
            ),
        )
        return response.output_text.strip()

    def verify_name_equivalence(self, left_name: str, right_name: str) -> str:
        client = self._build_client()
        response = client.responses.create(
            model=self.config.reasoning_model,
            input=(
                "Determine whether these company names refer to the same business entity. "
                "Return a concise explanation.\n\n"
                f"Name A: {left_name}\n"
                f"Name B: {right_name}"
            ),
        )
        return response.output_text.strip()
