"""T8 — F3 §4.4 quantities: parsed and normalized by code, never by the model (P-4).

Tier: unit.
"""
from __future__ import annotations

import pytest

from sdd_compiler.atomize.quantities import find_quantities


def only(text):
    found = find_quantities(text)
    assert len(found.quantities) == 1, found
    return found.quantities[0]


# -- AC-3.13 ------------------------------------------------------------------

@pytest.mark.parametrize(
    ("text", "value", "unit"),
    [
        ("expires 30 days after creation", 2_592_000, "s"),
        ("uploads up to 5 GB", 5_000_000_000, "byte"),
        ("uploads up to 5 GiB", 5_368_709_120, "byte"),
        ("at most 15% of requests", 15, "percent"),
    ],
)
def test_ac_3_13_quantities_are_normalized(text, value, unit):
    quantity = only(text)
    assert quantity.normalized == {"value": value, "unit": unit}


def test_ac_3_13_a_vague_amount_is_an_unbounded_quantity():
    found = find_quantities("the link refreshes after a few minutes")
    assert found.quantities == []
    assert found.unbounded == ["a few minutes"]


# -- the parser's reach -------------------------------------------------------

def test_the_quote_is_the_source_text_and_the_raw_value_is_kept():
    quantity = only("retain logs for 30 days")
    assert quantity.quote == "30 days"
    assert (quantity.value, quantity.unit) == (30, "day")


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("5GB", 5_000_000_000),
        ("1.5 KB", 1_500),
        ("2 MiB", 2_097_152),
        ("512 bytes", 512),
    ],
)
def test_size_spellings(text, value):
    assert only(text).normalized == {"value": value, "unit": "byte"}


@pytest.mark.parametrize(
    ("text", "seconds"),
    [
        ("within 200 ms", 0.2),
        ("after 90 seconds", 90),
        ("every 15 min", 900),
        ("for 2 hours", 7_200),
        ("within 1 week", 604_800),
    ],
)
def test_time_spellings(text, seconds):
    assert only(text).normalized == {"value": seconds, "unit": "s"}


def test_percent_in_words():
    assert only("at least 99.9 percent uptime").normalized == {"value": 99.9, "unit": "percent"}


def test_thousands_separators():
    assert only("up to 10,000 files").normalized == {"value": 10_000, "unit": "files"}


def test_a_count_keeps_its_noun_unchanged():
    quantity = only("retry at most 3 times")
    assert quantity.normalized == {"value": 3, "unit": "times"}


def test_calendar_units_are_kept_but_not_normalized():
    """A month or a year has no fixed length; converting one would invent a number."""
    quantity = only("keep invoices for 7 years")
    assert (quantity.value, quantity.unit) == (7, "year")
    assert quantity.normalized is None


@pytest.mark.parametrize(
    "text",
    [
        "see AC-3.13 and G2",            # identifiers
        "rel01 closes on 2026-09-30",    # dates and ids
        "AES-256 encryption",            # a name, not an amount
        "Python 3.11 or later",          # a version
        "section 4 applies",             # a number with no unit after it
    ],
)
def test_identifiers_versions_and_bare_numbers_are_not_quantities(text):
    assert find_quantities(text).quantities == []


def test_several_quantities_in_order():
    found = find_quantities("5 GB per file and 30 days of retention")
    assert [q.quote for q in found.quantities] == ["5 GB", "30 days"]
