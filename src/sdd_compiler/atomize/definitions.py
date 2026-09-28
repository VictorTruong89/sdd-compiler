"""F3 §4.5 step 9, D38 — `definition` sentences become term definitions, attached by code.

Q-ATOM labels a sentence `definition` when it says what a word means. Code then
decides which registered term it defines: the one the sentence **opens with**,
followed by a definitional boundary (`is`, `are`, `means`, `=`, `:`, `—`, `(`, or
the end). The match is strict on purpose: on R18, a looser one attached 38 of 68
sentences and many to the wrong term; this one attached 17, all correct. A wrong
definition misleads more than a missing one, so everything else is reported.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .guards import GuardFailure, locate_quote
from .terms import MAX_TERM_WORDS, normalize_name


@dataclass(frozen=True)
class Definition:
    block_id: str
    file: str
    lines: tuple[int, int]
    start: int                  # offset in the block, for reading order within it
    text: str                   # the block's own text for the sentence


@dataclass
class DefinitionOutcome:
    changed: dict[str, dict[str, Any]] = field(default_factory=dict)    # term id -> new record
    attached: list[dict[str, Any]] = field(default_factory=list)
    unattached: list[dict[str, Any]] = field(default_factory=list)


_MARKUP = re.compile(r"[*`\"“”]")
_ARTICLE = re.compile(r"^(a|an|the)\s+", re.IGNORECASE)
_NAME = re.compile(r"[A-Za-z0-9_-]+(?: [A-Za-z0-9_-]+)*")
_BOUNDARY = re.compile(r"^\s*(is|are|means|=|:|—|–|\(|$)", re.IGNORECASE)


def block_definitions(block: Mapping[str, Any], quotes: Sequence[str]
                      ) -> tuple[list[Definition], list[dict[str, Any]]]:
    """Locate each quote in the block (G2, layout-tolerant); keep the block's own text for it."""
    found, dropped = [], []
    for quote in quotes:
        try:
            start, end = locate_quote(quote, block["text"])
        except GuardFailure:
            dropped.append({"block": block["id"], "file": block["source"], "lines": list(block["lines"]),
                            "text": quote, "reason": "not_in_block"})
            continue
        # G2 skips layout (`*`, backticks) at the edges; keep the quote's own opening marks.
        lead = len(quote) - len(quote.lstrip("*`_"))
        while lead and start and block["text"][start - 1] in "*`_":
            start, lead = start - 1, lead - 1
        found.append(Definition(block_id=block["id"], file=block["source"],
                                lines=tuple(block["lines"]), start=start, text=block["text"][start:end]))
    return found, dropped


def defined_term(text: str, names: Mapping[str, str]) -> str | None:
    """The term id whose name (or alias) the sentence opens with, then a boundary — or None."""
    sentence = _MARKUP.sub("", text).strip()
    if sentence.startswith("|"):
        return None
    sentence = _ARTICLE.sub("", sentence)
    words = _NAME.match(sentence)
    if not words:
        return None
    ends = [m.end() for m in re.finditer(r"[A-Za-z0-9_-]+", words.group())][:MAX_TERM_WORDS]
    for end in reversed(ends):                                    # the longest name first
        term = names.get(normalize_name(sentence[:end].replace("_", " ")))
        if term and _BOUNDARY.match(sentence[end:]):
            return term
    return None


def attach_definitions(terms: Mapping[str, Mapping[str, Any]], definitions: Iterable[Definition],
                       invalidated: set[str]) -> DefinitionOutcome:
    """Clear what `invalidated` blocks defined, then attach each definition in reading order."""
    outcome = DefinitionOutcome()
    current = {term_id: dict(term) for term_id, term in terms.items()}
    for term_id, term in current.items():
        if term.get("defined_by") in invalidated:
            term["definition"] = term["defined_by"] = None
            outcome.changed[term_id] = term

    names: dict[str, str] = {}
    for term_id in sorted(current):
        for name in [current[term_id]["canonical"], *current[term_id].get("aliases", [])]:
            names.setdefault(normalize_name(name), term_id)

    for item in sorted(definitions, key=lambda d: (d.file, d.lines[0], d.start)):
        where = {"block": item.block_id, "file": item.file, "lines": list(item.lines), "text": item.text}
        term_id = defined_term(item.text, names)
        if term_id is None:
            outcome.unattached.append({**where, "reason": "no_term"})
        elif current[term_id].get("definition") is not None:
            outcome.unattached.append({**where, "reason": "already_defined", "term": term_id})
        else:
            current[term_id].update(definition=item.text, defined_by=item.block_id)
            outcome.changed[term_id] = current[term_id]
            outcome.attached.append({**where, "term": term_id})
    return outcome
