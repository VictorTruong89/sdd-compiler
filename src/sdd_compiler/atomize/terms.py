"""F3 §4.5 steps 1–2 — term tags to registry terms, asking Q-TERM only when it could matter.

1. A tag whose name is a registered term's canonical name or alias — or whose
   `term:` id is already taken — resolves to that term. No question.
2. Otherwise the tag becomes a new `proposed` term. If the registry holds terms
   with **similar** names, Q-TERM asks whether it is one of them:
   - `different` → nothing more;
   - `same` → **merged at once** (F3 D20): the new name becomes an alias of the
     existing term, every tag with that name resolves to it, and a `term_same`
     attention item lets a person reject the merge (undo). No node turns
     ambiguous: on live data nearly every `same` was right (I-29);
   - `unsure` → the new term stays separate, a `term_unsure` item is opened, and
     its nodes carry `pending_review` until a person decides (F3 D16).

⚑ No similar name, no question (F3 D17): on a first run the registry is empty,
and a question with no candidates can only be answered `different`. "Similar"
is cheap and deterministic: a shared word (ignoring a plural `s`), or a
`difflib` ratio of at least 0.8.

Tags are processed in a fixed order, and terms created earlier in the run are
candidates for later tags, so "share link" then "sharing link" is asked about.

⚑ Term hygiene (F3 D19). A family *is* a term, so a term must name a thing. On 32
real blocks Haiku tagged 142 terms for 49 nodes, 119 used once — ids (`AC-1.9`,
`D9`), values (`120 s timeout`), whole clauses — and families became one per
node (rel01 S23). Code therefore drops a tag that contains a digit or runs past
four words, and folds names to the singular ("blocks" → "block") before
matching, so a plural never needs a question.
"""
from __future__ import annotations

import difflib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..llm import Backend, Question
from ..model.ids import term_id
from .batch import ask_each
from .guards import GuardFailure

SCHEMA_VERSION = "q-term/1"
MAX_CANDIDATES = 10          # F3 Q3 default
SIMILARITY = 0.8

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["terms"],
    "properties": {"terms": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["term_key", "verdict", "same_as", "reason"],
        "properties": {
            "term_key": {"type": "string"},
            "verdict": {"type": "string", "enum": ["same", "different", "unsure"]},
            "same_as": {"type": ["string", "null"]},
            "reason": {"type": "string"},
        },
    }}},
}

_INSTRUCTIONS = """\
You are deciding whether newly found specification terms name something already in the
term registry. For each new term, answer:
- same: it names exactly the same thing as one listed candidate; give that candidate's id
  in same_as;
- different: it names something else;
- unsure: you cannot tell from what is given.
Give a one-sentence reason. Answer for each term, using its exact term_key.
"""


@dataclass
class TermResolution:
    by_tag: dict[str, str] = field(default_factory=dict)          # normalized tag name -> term id
    new_terms: dict[str, dict[str, Any]] = field(default_factory=dict)
    changed_terms: dict[str, dict[str, Any]] = field(default_factory=dict)  # existing, new alias
    merged_into: dict[str, str] = field(default_factory=dict)       # merged-away id -> its target
    reviews: list[dict[str, Any]] = field(default_factory=list)   # {type, subject, detail}
    pending_review: set[str] = field(default_factory=set)         # term ids awaiting a person
    failures: dict[str, str] = field(default_factory=dict)        # term id -> failed check
    judgments: dict[str, str] = field(default_factory=dict)       # term key -> J id (with a lock)


@dataclass(frozen=True)
class _Ask:
    key: str
    name: str
    kind: str
    candidates: tuple[dict[str, Any], ...]


MAX_TERM_WORDS = 4
_NOT_PLURAL = ("ss", "us", "is", "ous")


def normalize_name(name: str) -> str:
    """Lower case, no inline Markdown, single spaces, singular last word."""
    return fold_name(name)


def fold_name(name: str) -> str:
    words = name.replace("`", "").replace("*", "").lower().split()
    if words:
        words[-1] = _singular_word(words[-1])
    return " ".join(words)


def is_term_name(name: str) -> bool:
    """A thing's name: no digits (ids, values), no `:`/`=` (a setting with its value),
    at most four words, not empty."""
    words = name.replace("`", "").replace("*", "").split()
    return (bool(words) and len(words) <= MAX_TERM_WORDS
            and not any(c.isdigit() or c in ":=" for c in name))


def _singular_word(word: str) -> str:
    if len(word) <= 3 or word.endswith(_NOT_PLURAL) or not word.endswith("s"):
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    return word[:-1]


def similar_terms(name: str, registry: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    wanted = normalize_name(name)
    words = {_singular(word) for word in wanted.split()}
    scored = []
    for term in registry.values():
        names = [term["canonical"], *term.get("aliases", [])]
        best = max(difflib.SequenceMatcher(None, wanted, normalize_name(n)).ratio() for n in names)
        shared = any(words & {_singular(w) for w in normalize_name(n).split()} for n in names)
        if shared or best >= SIMILARITY:
            scored.append((-best, term["id"], term))
    return [term for _, _, term in sorted(scored)][:MAX_CANDIDATES]


def resolve_terms(
    tags: Sequence[Mapping[str, Any]],
    registry: Mapping[str, Mapping[str, Any]],
    backend: Backend,
    lock: Any | None = None,
) -> TermResolution:
    """`tags` in processing order: `{name, kind}`. The registry is not modified."""
    result = TermResolution()
    known = dict(registry)
    index = _index(known)
    asks: list[_Ask] = []

    for tag in tags:
        if not is_term_name(tag["name"]):
            continue
        name = normalize_name(tag["name"])
        if not name or name in result.by_tag:
            continue
        existing = index.get(name) or (term_id(name) if term_id(name) in known else None)
        if existing:
            result.by_tag[name] = existing
            continue
        candidates = similar_terms(name, known)
        new_id = term_id(name)
        record = {"id": new_id, "canonical": name, "aliases": [], "kind": tag["kind"],
                  "defined_by": None, "status": "proposed"}
        result.new_terms[new_id] = record
        result.by_tag[name] = new_id
        known[new_id] = record
        index[name] = new_id
        if candidates:
            asks.append(_Ask(new_id, name, tag["kind"], tuple(candidates)))

    if asks:
        _ask_q_term(asks, backend, result, known, lock)
    return result


def _ask_q_term(asks: list[_Ask], backend: Backend, result: TermResolution,
                known: dict[str, Mapping[str, Any]], lock: Any | None = None) -> None:
    def accept(ask: _Ask, payload: dict[str, Any]) -> None:
        verdict = payload["verdict"]
        allowed = {candidate["id"] for candidate in ask.candidates}
        if verdict == "same" and payload["same_as"] not in allowed:
            raise GuardFailure(
                f"same_as must be one of the listed candidates ({', '.join(sorted(allowed))}); "
                f"got {payload['same_as']!r}"
            )
        if verdict == "different":
            return
        if verdict == "same":
            _merge(ask, payload["same_as"], payload["reason"], result, known)
            return
        result.reviews.append({"type": "term_unsure", "subject": ask.key,
                               "detail": f"Q-TERM: unsure — {payload['reason']}"})
        result.pending_review.add(ask.key)

    batch = ask_each(
        asks, item_id=lambda ask: ask.key, backend=backend, build_question=build_question,
        list_key="terms", id_key="term_key", accept=accept, lock=lock,
        lock_input=lambda ask: {"name": ask.name, "kind": ask.kind, "candidates": [
            {"id": c["id"], "canonical": c["canonical"], "kind": c["kind"],
             "aliases": list(c.get("aliases", []))} for c in ask.candidates]},
    )
    result.failures.update(batch.failures)
    result.judgments.update(batch.judgments)
    # A term Q-TERM could not settle is still unreviewed: say so on its nodes.
    for key, problem in result.failures.items():
        result.reviews.append({"type": "term_unsure", "subject": key,
                               "detail": f"Q-TERM failed its checks twice: {problem}"})
        result.pending_review.add(key)


def _merge(ask: _Ask, target: str, reason: str, result: TermResolution,
           known: dict[str, Mapping[str, Any]]) -> None:
    """F3 D20 — the new name becomes an alias of `target`; its tags resolve there.

    The target may itself have merged away earlier in the same batch (live M2 gate):
    follow the chain to the term that still exists.
    """
    while target in result.merged_into:
        target = result.merged_into[target]
    result.merged_into[ask.key] = target
    result.new_terms.pop(ask.key, None)
    known.pop(ask.key, None)
    for name, term in list(result.by_tag.items()):
        if term == ask.key:
            result.by_tag[name] = target
    record = dict(result.new_terms.get(target) or known[target])
    record["aliases"] = sorted({*record.get("aliases", []), ask.name})
    known[target] = record
    if target in result.new_terms:
        result.new_terms[target] = record
    else:
        result.changed_terms[target] = record
    result.reviews.append({
        "type": "term_same", "subject": target,
        "detail": f"Q-TERM merged \"{ask.name}\" into {target} as an alias — {reason}. "
                  f"Reject to undo: \"{ask.name}\" becomes its own term.",
    })


def build_question(asks: Sequence[_Ask], note: str | None = None) -> Question:
    parts = [_INSTRUCTIONS]
    if note:
        parts.append(f"\nThe previous answer was rejected. {note}\nTry again, carefully.\n")
    for ask in asks:
        listed = "".join(
            f"  - {c['id']}: \"{c['canonical']}\" ({c['kind']})"
            + (f", also called {', '.join(repr(a) for a in c['aliases'])}" if c.get("aliases") else "")
            + "\n"
            for c in ask.candidates
        )
        parts.append(f"\n--- TERM {ask.key} ---\nname: \"{ask.name}\" ({ask.kind})\ncandidates:\n{listed}")
    return Question(kind="q-term", schema_version=SCHEMA_VERSION, schema=SCHEMA,
                    prompt="".join(parts), payload={"term_keys": [ask.key for ask in asks]})


def _index(registry: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for term in registry.values():
        for name in [term["canonical"], *term.get("aliases", [])]:
            index.setdefault(normalize_name(name), term["id"])
    return index


def _singular(word: str) -> str:
    return _singular_word(word)
