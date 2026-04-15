"""Record preprocessing for multilingual customer data."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from src.config import NORMALIZATION


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
    language: str
    translated_company_name: str
    translated_address: str
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


def build_structured_text(company: str, address: str, city: str, country: str) -> str:
    return f"company: {company} || address: {address} || city: {city} || country: {country}"


def preprocess_record(record: RawRecord) -> ProcessedRecord:
    detected_language = detect_language(f"{record.company_name} {record.address}")
    translated_company = translate_text(record.company_name)
    translated_address = translate_text(record.address)
    normalized_company = normalize_text(record.company_name)
    normalized_alternate = normalize_text(record.alternate_name)
    normalized_address = normalize_text(record.address)
    normalized_city = normalize_text(record.city)
    normalized_country = normalize_text(record.country)
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
        language=detected_language,
        translated_company_name=translated_company,
        translated_address=translated_address,
        normalized_company_name=normalized_company,
        normalized_alternate_name=normalized_alternate,
        normalized_address=normalized_address,
        normalized_city=normalized_city,
        normalized_country=normalized_country,
        structured_text=structured_text,
    )
