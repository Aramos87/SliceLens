"""Interpretable boolean predicates. No embeddings, no models."""

from __future__ import annotations

import re

NEGATION_RE = re.compile(
    r"\b(?:not|never|no|none|nobody|nothing|neither|nor|without|cannot)\b|n't\b",
    re.IGNORECASE,
)
UNIT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:km|m|cm|mm|kg|g|mg|lb|oz|ml|l|celsius|fahrenheit|°c|°f)\b",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"\d")
UNCOMMON_NOUNS = (
    "axolotl",
    "quark",
    "obsidian",
    "fjord",
    "kudu",
    "narwhal",
    "ptarmigan",
    "qat",
    "xylem",
    "yttrium",
)
UNCOMMON_RE = re.compile(
    r"\b(?:" + "|".join(UNCOMMON_NOUNS) + r")\b",
    re.IGNORECASE,
)

PREDICATES: dict[str, callable] = {}


def has_negation(text: str) -> bool:
    return bool(NEGATION_RE.search(text))


def has_unit(text: str) -> bool:
    return bool(UNIT_RE.search(text))


def has_number(text: str) -> bool:
    return bool(NUMBER_RE.search(text))


def has_uncommon_noun(text: str) -> bool:
    return bool(UNCOMMON_RE.search(text))


PREDICATES = {
    "has_negation": has_negation,
    "has_unit": has_unit,
    "has_number": has_number,
    "has_uncommon_noun": has_uncommon_noun,
}

LABELS = {
    "has_negation": "has negation",
    "has_unit": "has unit",
    "has_number": "has number",
    "has_uncommon_noun": "has uncommon noun",
}

INTERPRETATIONS = {
    "has_negation": "The prompt contains a negation (not, never, no, n't, without, …).",
    "has_unit": "The prompt includes a measurement with an explicit unit (km, kg, °C, …).",
    "has_number": "The prompt contains a numeral.",
    "has_uncommon_noun": "The prompt contains a rare noun (axolotl, fjord, yttrium, …).",
}


def evaluate(text: str) -> dict[str, bool]:
    return {name: fn(text) for name, fn in PREDICATES.items()}
