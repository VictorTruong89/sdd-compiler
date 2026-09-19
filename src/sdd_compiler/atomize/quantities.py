"""Quantities in a claim, parsed and normalized by code (F3 §4.4, P-4).

The model never normalizes a number. "5 GB", "5GB" and "5000 MB" must compare
equal when conflicts are checked (F6), and "30 days" must compare with
"2,592,000 s"; a model asked to do that arithmetic will sometimes get it wrong
and never say so.

Normalized units: time → seconds (`s`), size → bytes (`byte`; KB = 1000,
KiB = 1024, F3 D7), percent → `percent`, counts unchanged.

Deliberately conservative — a missed quantity costs a weaker check, an invented
one costs a false conflict:

- a number glued to letters, hyphens or dots is an identifier, a date or a
  version, not an amount (`AC-3.13`, `AES-256`, `2026-09-30`, `3.11`);
- a bare count needs a bounding word before it ("at most 3 times", "up to
  10,000 files"); otherwise "section 4 applies" would be a count of "applies";
- months and years are recognized but **not normalized**: neither has a fixed
  length, and choosing one would invent a number.

A vague amount of a measurable unit ("a few minutes") is reported as
`unbounded`, which the atomizer records as ambiguity `unbounded_quantity`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

_TIME = {  # canonical unit, seconds per unit
    **dict.fromkeys(("ms", "msec", "millisecond", "milliseconds"), ("ms", Decimal("0.001"))),
    **dict.fromkeys(("s", "sec", "secs", "second", "seconds"), ("s", Decimal(1))),
    **dict.fromkeys(("min", "mins", "minute", "minutes"), ("min", Decimal(60))),
    **dict.fromkeys(("h", "hr", "hrs", "hour", "hours"), ("hour", Decimal(3600))),
    **dict.fromkeys(("day", "days"), ("day", Decimal(86400))),
    **dict.fromkeys(("week", "weeks"), ("week", Decimal(604800))),
}
_CALENDAR = {**dict.fromkeys(("month", "months"), "month"), **dict.fromkeys(("year", "years"), "year")}
_SIZE = {  # matched case-insensitively, except the bare "B"
    "b": ("byte", 1), "byte": ("byte", 1), "bytes": ("byte", 1),
    "kb": ("KB", 1000), "mb": ("MB", 1000**2), "gb": ("GB", 1000**3), "tb": ("TB", 1000**4),
    "kib": ("KiB", 1024), "mib": ("MiB", 1024**2), "gib": ("GiB", 1024**3), "tib": ("TiB", 1024**4),
}
_PERCENT = ("%", "percent")

_BOUNDING = (
    "at most", "at least", "up to", "no more than", "no fewer than", "more than", "fewer than",
    "less than", "maximum of", "minimum of", "max", "min", "exactly", "within", "every", "only",
)
_NOT_A_COUNT_NOUN = frozenset(("and", "or", "the", "of", "per", "to", "for", "in", "on", "at", "is", "are"))

_NUMBER = r"(?<![\w.\-/])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\d_]|[.\-/]\d)"
_QUANTITY = re.compile(_NUMBER + r"(\s*%|\s?[A-Za-z]+)?")
_BOUND_BEFORE = re.compile(r"(?:" + "|".join(re.escape(w) for w in _BOUNDING) + r")\s+$", re.IGNORECASE)

_MEASURE_WORDS = sorted(
    {w for w in (*_TIME, *_CALENDAR) if len(w) > 3} | {"bytes", "kilobytes", "megabytes", "gigabytes"},
    key=len, reverse=True,
)
_UNBOUNDED = re.compile(
    r"\b(?:a few|several|a couple of|a number of|many|numerous|some)\s+(?:"
    + "|".join(_MEASURE_WORDS) + r")\b",
    re.IGNORECASE,
)


@dataclass
class Quantity:
    """CT-2.1 `canonical.quantities[]`: the raw value and unit, plus the normalized pair."""

    value: int | float
    unit: str
    normalized: dict[str, Any] | None
    quote: str

    def as_record(self) -> dict[str, Any]:
        return {"value": self.value, "unit": self.unit,
                "normalized": self.normalized, "quote": self.quote}


@dataclass
class Found:
    quantities: list[Quantity] = field(default_factory=list)
    unbounded: list[str] = field(default_factory=list)


def find_quantities(text: str) -> Found:
    found = Found(unbounded=[match.group(0) for match in _UNBOUNDED.finditer(text)])
    for match in _QUANTITY.finditer(text):
        quantity = _read(match, text)
        if quantity is not None:
            found.quantities.append(quantity)
    return found


def _read(match: re.Match[str], text: str) -> Quantity | None:
    number = Decimal(match.group(1).replace(",", ""))
    raw_unit = (match.group(2) or "").strip()
    if not raw_unit:
        return None
    quote = match.group(0).rstrip()
    key = raw_unit.lower()

    if raw_unit == "%" or key == "percent":
        return Quantity(_plain(number), "percent", {"value": _plain(number), "unit": "percent"}, quote)
    if key in _TIME and not (raw_unit == "S" or raw_unit == "H"):
        unit, seconds = _TIME[key]
        return Quantity(_plain(number), unit, {"value": _plain(number * seconds), "unit": "s"}, quote)
    if key in _CALENDAR:
        return Quantity(_plain(number), _CALENDAR[key], None, quote)
    if key in _SIZE and (key != "b" or raw_unit == "B"):
        unit, factor = _SIZE[key]
        return Quantity(_plain(number), unit, {"value": _plain(number * factor), "unit": "byte"}, quote)

    # A count: only with a bounding word before it, and a real noun after it.
    if key.isalpha() and key == raw_unit and len(key) >= 3 and key not in _NOT_A_COUNT_NOUN:
        if _BOUND_BEFORE.search(text[: match.start()]):
            return Quantity(_plain(number), key, {"value": _plain(number), "unit": key}, quote)
    return None


def _plain(number: Decimal) -> int | float:
    return int(number) if number == number.to_integral_value() else float(number)
