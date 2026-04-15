"""Record preprocessing for multilingual customer data."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from src.config import NORMALIZATION
from src.runtime import DEFAULT_RUNTIME_SETTINGS, RuntimeSettings


NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")
PUNCTUATION_RE = re.compile(r"[^\w\s]")
WHITESPACE_RE = re.compile(r"\s+")


TRANSLATION_HINTS = {
    "sociedad": "company",
    "internacional": "international",
    "compagnie": "company",
    "industrie": "industries",
    "gesellschaft": "company",
    "tecnologia": "technology",
    "tecnologias": "technologies",
    "direccion": "address",
    "calle": "street",
}


@dataclass(frozen=True)
class RawRecord:
    record_id: str
    company_name: str
    address: str
    city: str
    country: str
    alternate_name: str = ""


@dataclass(frozen=True)
class ProcessedRecord:
    record_id: str
    raw_company_name: str
    raw_address: str
    raw_city: str
    raw_country: str
    alternate_name: str
    company_language: str
    address_language: str
    city_language: str
    country_language: str
    language: str
    translated_company_name: str
    translated_address: str
    translated_city: str
    translated_country: str
    normalized_company_name: str
    normalized_alternate_name: str
    normalized_address: str
    normalized_city: str
    normalized_country: str
    structured_text: str


def detect_language(text: str) -> str:
    """Return a lightweight language indicator for Week 1."""
    if not text.strip():
        return "unknown"
    if NON_ASCII_RE.search(text):
        return "non_english_or_mixed"

    lowered = text.lower()
    for token in TRANSLATION_HINTS:
        if token in lowered:
            return "possible_non_english"
    return "english"


def transliterate_text(text: str) -> str:
    """Fold accents and non-ASCII characters into a Latin approximation."""
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def translate_text(text: str) -> str:
    """Small deterministic placeholder for future LLM translation."""
    translated = transliterate_text(text)
    for source, target in TRANSLATION_HINTS.items():
        translated = re.sub(rf"\b{re.escape(source)}\b", target, translated, flags=re.IGNORECASE)
    return translated


def normalize_text(text: str) -> str:
    text = translate_text(text).lower().strip()
    text = PUNCTUATION_RE.sub(" ", text)
    tokens = [token for token in WHITESPACE_RE.split(text) if token]

    expanded_tokens: list[str] = []
    for token in tokens:
        if token in NORMALIZATION.articles:
            continue
        expanded_tokens.append(NORMALIZATION.abbreviations.get(token, token))

    return " ".join(expanded_tokens)


def llm_expand_text(text: str, settings: RuntimeSettings, provider=None) -> str:
    if not text or not settings.enable_llm_abbreviation_expansion or not settings.groq_api_key:
        return text
    if provider is None:
        return text
    try:
        return provider.expand_abbreviations(text)["expanded_text"]
    except Exception:
        return text


def translate_input_text(text: str, settings: RuntimeSettings, provider=None) -> str:
    if not text:
        return text
    detected_language = detect_language(text)
    if detected_language == "english":
        return transliterate_text(text)
    if settings.enable_llm_translation and settings.groq_api_key and provider is not None:
        try:
            return provider.translate_text(text)
        except Exception:
            return translate_text(text)
    return translate_text(text)


def build_structured_text(company: str, address: str, city: str, country: str) -> str:
    return f"company: {company} || address: {address} || city: {city} || country: {country}"


def preprocess_record(record: RawRecord, settings: RuntimeSettings | None = None, provider=None) -> ProcessedRecord:
    if settings is None:
        settings = DEFAULT_RUNTIME_SETTINGS

    company_language = detect_language(record.company_name)
    address_language = detect_language(record.address)
    city_language = detect_language(record.city)
    country_language = detect_language(record.country)
    detected_language = "english"
    if any(
        language != "english" for language in (company_language, address_language, city_language, country_language)
    ):
        detected_language = "mixed_or_non_english"

    llm_company = llm_expand_text(record.company_name, settings, provider)
    llm_alternate = llm_expand_text(record.alternate_name, settings, provider)
    llm_address = llm_expand_text(record.address, settings, provider)
    translated_company = translate_input_text(llm_company, settings, provider)
    translated_address = translate_input_text(llm_address, settings, provider)
    translated_city = translate_input_text(record.city, settings, provider)
    translated_country = translate_input_text(record.country, settings, provider)
    normalized_company = normalize_text(translated_company)
    normalized_alternate = normalize_text(translate_input_text(llm_alternate, settings, provider))
    normalized_address = normalize_text(translated_address)
    normalized_city = normalize_text(translated_city)
    normalized_country = normalize_text(translated_country)
    structured_text = build_structured_text(
        normalized_company or translated_company.lower(),
        normalized_address or translated_address.lower(),
        normalized_city,
        normalized_country,
    )

    return ProcessedRecord(
        record_id=record.record_id,
        raw_company_name=record.company_name,
        raw_address=record.address,
        raw_city=record.city,
        raw_country=record.country,
        alternate_name=record.alternate_name,
        company_language=company_language,
        address_language=address_language,
        city_language=city_language,
        country_language=country_language,
        language=detected_language,
        translated_company_name=translated_company,
        translated_address=translated_address,
        translated_city=translated_city,
        translated_country=translated_country,
        normalized_company_name=normalized_company,
        normalized_alternate_name=normalized_alternate,
        normalized_address=normalized_address,
        normalized_city=normalized_city,
        normalized_country=normalized_country,
        structured_text=structured_text,
    )
