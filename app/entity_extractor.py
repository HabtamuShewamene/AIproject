"""Lightweight entity extraction (companies, products, people, locations)."""

from __future__ import annotations

import re

_KNOWN_COMPANIES = [
    "OpenAI",
    "Google",
    "Microsoft",
    "Apple",
    "Meta",
    "Amazon",
    "Tesla",
    "Nvidia",
    "Anthropic",
    "Twitter",
    "X",
]

_KNOWN_LOCATIONS = [
    "San Francisco",
    "New York",
    "London",
    "Seattle",
    "Austin",
    "Tokyo",
    "Paris",
    "Berlin",
    "California",
    "Silicon Valley",
]

_PRODUCT_PATTERN = re.compile(
    r"\b(GPT-?\d+(?:\.\d+)?|ChatGPT|Claude|Gemini|Copilot|iPhone\s*\d*|Android)\b",
    re.I,
)

_PERSON_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b",
)


def extract_entities(text: str) -> dict:
    raw = text or ""
    companies: list[str] = []
    products: list[str] = []
    people: list[str] = []
    locations: list[str] = []

    for company in _KNOWN_COMPANIES:
        if re.search(rf"\b{re.escape(company)}\b", raw, re.I):
            companies.append(company)

    for match in _PRODUCT_PATTERN.finditer(raw):
        label = match.group(1)
        if label not in products:
            products.append(label)

    for loc in _KNOWN_LOCATIONS:
        if loc.lower() in raw.lower():
            locations.append(loc)

    skip = set(companies) | {"The", "This", "That", "When", "What", "How", "Why"}
    for match in _PERSON_PATTERN.finditer(raw):
        name = match.group(1).strip()
        if name in skip or len(name) < 4:
            continue
        if name not in people and name not in companies:
            people.append(name)

    return {
        "companies": companies[:8],
        "products": products[:8],
        "people": people[:8],
        "locations": locations[:8],
    }
