"""Deterministic guards around a non-deterministic atomizer (F3 §4.4, P-5).

The model's split cannot be proven right, but most ways of being wrong are
mechanically detectable, and each guard here is one of them:

- **G2 span anchoring** — every quote must appear verbatim in the block, and the
  offsets are computed here, never taken from the model;
- **G3 coverage** — a sentence carrying a normative word must be covered by an
  atom or explicitly labelled non-normative;
- **G5 schema** — the answer must match its JSON Schema.

G4 (no injection) and G6 (weak words) work on the described atom, so they live
with Q-DESC in `describe.py`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator

#: A sentence containing one of these is a claim someone must have covered.
NORMATIVE_WORDS = (
    "must", "shall", "should", "may", "never", "only", "required", "not allowed",
)

_SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]+|\n|$)")
_WORD = re.compile(r"[a-z][a-z'-]*")


class GuardFailure(Exception):
    """One block's answer failed a check. The message is fed back on the re-ask."""


@dataclass
class Anchor:
    quote: str
    span: tuple[int, int]


def check_schema(answer: dict[str, Any], schema: dict[str, Any]) -> None:
    """G5 — validate the whole answer before any block is trusted."""
    errors = sorted(Draft202012Validator(schema).iter_errors(answer), key=lambda e: e.path)
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise GuardFailure(f"schema check failed at {location}: {first.message}")


def anchor_quotes(quotes: list[str], text: str, claimed: list[tuple[int, int]]) -> list[Anchor]:
    """G2 — find each quote in the block, taking the first occurrence not already used.

    Offsets are computed here so that a paraphrase cannot pass as a quote, and so
    that no model-supplied offset is ever trusted.

    **Layout-tolerant** (F3 D9). Spec prose is hard
    wrapped and often sits inside a `>` blockquote, so a claim that spans a line
    break carries a newline — and maybe a `>` marker — in the source where the
    model's answer has a space; and models drop `**` bold marks when quoting. Rejecting that is a false alarm: the words, their
    order, their case and their punctuation are all still checked, and the
    returned span is the true source range. Only layout may differ.
    """
    anchors: list[Anchor] = []
    for quote in quotes:
        needle = quote.strip()
        if not needle:
            raise GuardFailure("an atom carried an empty quote")
        span = _first_free_occurrence(needle, text, claimed)
        if span is None:
            if needle in text:
                raise GuardFailure(
                    f"the quote {needle[:160]!r} was already claimed by another atom in this block"
                )
            raise GuardFailure(
                f"the quote {needle[:160]!r} is not verbatim in the block; quote the source exactly"
            )
        claimed.append(span)
        anchors.append(Anchor(quote=needle, span=span))
    return anchors


def locate_quote(quote: str, text: str, prefer: list[tuple[int, int]] | None = None) -> tuple[int, int]:
    """G2 for one quote that may overlap other quotes (Q-DESC answers do).

    An occurrence inside the `prefer` spans (the atom's own) wins over an earlier
    one elsewhere in the block, so a word the atom shares with its neighbours
    anchors to the atom.
    """
    needle = quote.strip()
    if not needle:
        raise GuardFailure("an answer carried an empty quote")
    for start, end in prefer or []:
        span = _first_free_occurrence(needle, text[start:end], [])
        if span is not None:
            return (span[0] + start, span[1] + start)
    span = _first_free_occurrence(needle, text, [])
    if span is None:
        raise GuardFailure(
            f"the quote {needle[:160]!r} is not verbatim in the block; quote the source exactly"
        )
    return span


def check_coverage(text: str, covered: list[tuple[int, int]], labelled: list[str]) -> None:
    """G3 — every normative sentence is covered by an atom, or labelled otherwise."""
    for sentence, span in _sentences(text):
        if not _is_normative(sentence):
            continue
        if _overlaps(span, covered) or _labelled(sentence, labelled):
            continue
        raise GuardFailure(
            f"coverage check failed: the sentence {sentence.strip()[:70]!r} carries a normative "
            f"word but no atom covers it and no sentence role explains it"
        )


# -- helpers ----------------------------------------------------------------

def _first_free_occurrence(
    needle: str, text: str, claimed: list[tuple[int, int]]
) -> tuple[int, int] | None:
    flat_text, offsets = _flatten(text)
    flat_needle, _ = _flatten(needle)
    if not flat_needle:
        return None

    # A quote lifted from the start of a sentence may change the case of its first
    # letter ("a Q-TERM" for "A Q-TERM"); case anywhere else still counts (R10).
    variants = [flat_needle]
    if flat_needle[0].isalpha() and flat_needle[0].swapcase() != flat_needle[0]:
        variants.append(flat_needle[0].swapcase() + flat_needle[1:])
    for variant in variants:
        start = flat_text.find(variant)
        while start != -1:
            end = start + len(variant)
            span = (offsets[start], offsets[end - 1] + 1)
            if not _overlaps(span, claimed):
                return span
            start = flat_text.find(variant, start + 1)
    return None


def _flatten(text: str) -> tuple[str, list[int]]:
    """Collapse layout to one space, keeping a map back to real offsets.

    Layout is a run of whitespace, the blockquote markers that Markdown repeats
    at the start of every wrapped line inside a `>` block, `*` emphasis marks and
    backticks. All are how the file is formatted, not what it says, so a quote
    may differ there.
    """
    flattened: list[str] = []
    offsets: list[int] = []
    index = 0
    length = len(text)
    while index < length:
        if text[index] in "*`":
            # Emphasis and inline-code marks: `**Given**` and `Given`, `` `x` `` and `x`,
            # are the same words (F3 D9, extended by rel01 D32 R5).
            index += 1
            continue
        if not text[index].isspace():
            flattened.append(text[index])
            offsets.append(index)
            index += 1
            continue

        cursor = index
        crossed_line = False
        while cursor < length and text[cursor].isspace():
            crossed_line = crossed_line or text[cursor] == "\n"
            cursor += 1
        if crossed_line:
            cursor = _skip_blockquote_markers(text, cursor)
        if flattened:
            flattened.append(" ")
            offsets.append(index)
        index = cursor

    while flattened and flattened[-1] == " ":
        flattened.pop()
        offsets.pop()
    return "".join(flattened), offsets


def _skip_blockquote_markers(text: str, start: int) -> int:
    """Step over `>`, `> >`, … at the start of a continuation line."""
    cursor = start
    while cursor < len(text) and text[cursor] == ">":
        cursor += 1
        while cursor < len(text) and text[cursor] in " \t":
            cursor += 1
    return cursor


def _sentences(text: str) -> list[tuple[str, tuple[int, int]]]:
    return [(match.group(0), match.span()) for match in _SENTENCE.finditer(text) if match.group(0).strip()]


def _is_normative(sentence: str) -> bool:
    words = set(_WORD.findall(sentence.lower()))
    lowered = sentence.lower()
    return any(
        (word in words) if " " not in word else (word in lowered) for word in NORMATIVE_WORDS
    )


def _overlaps(span: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    return any(span[0] < other[1] and other[0] < span[1] for other in spans)


def _labelled(sentence: str, labelled: list[str]) -> bool:
    stripped = sentence.strip()
    return any(stripped in quote or quote in stripped for quote in labelled if quote.strip())
