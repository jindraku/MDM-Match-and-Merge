"""Shared score result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RankedVariant:
    variant_id: str
    score: float
    rank: int
    reasoning: str
    payload: object
