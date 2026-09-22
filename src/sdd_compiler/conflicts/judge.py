"""F6 §4.2 — Q-PAIR: one call judges one pair (AC-6.1 … AC-6.8).

The judge is the only place in rel01 where the model is asked about two nodes at once, and it
is asked a closed question: one relation from a fixed list, a direction, a rationale and a
verbatim quote from each node. Everything the answer claims is checked before it is believed:

- **G5 schema** — including the direction rule (CT-6.1): `none`, `duplicates` and `contradicts`
  are symmetric, so a direction on them is a rejected answer, not a detail to ignore (AC-6.7);
- **G2 quotes** — each quote must appear in its own node's text, up to layout (F3 D9, AC-6.6).

A failure re-asks the pair once with the reason, as F3 §4.3 does for atomization. A second
failure raises, and the caller (T17) leaves both nodes unchecked for this pair.

⚑ `provisional` (F6 §4.4, D3): a verdict touching an `ambiguous` node is still recorded, marked
provisional, because a vague claim can still contradict a precise one. T17 stores the mark with
the judgment and re-judges when the ambiguity is resolved.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..atomize.guards import GuardFailure, anchor_quotes
from ..atomize.batch import ask_each
from ..llm import Answer, Backend, Question

SCHEMA_VERSION = "q-pair/2"      # /2 asks about a batch of pairs (R21, rel01 D30's lever)

RELATIONS = ("none", "refines", "depends_on", "duplicates", "subsumes", "contradicts")
SYMMETRIC_ONLY = ("none", "duplicates", "contradicts")
DIRECTIONS = ("a_to_b", "b_to_a", "symmetric")

VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["pair_id", "relation", "direction", "rationale", "quotes", "confidence"],
    "properties": {
        "pair_id": {"type": "string"},
        "relation": {"type": "string", "enum": list(RELATIONS)},
        "direction": {"type": "string", "enum": list(DIRECTIONS)},
        "rationale": {"type": "string", "minLength": 1},
        "quotes": {
            "type": "object", "additionalProperties": False,
            "required": ["a", "b"],
            "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        },
        "confidence": {"type": "string", "enum": ["high", "low"]},
    },
    # CT-6.1: a symmetric relation may not carry a direction.
    "if": {"properties": {"relation": {"enum": list(SYMMETRIC_ONLY)}}},
    "then": {"properties": {"direction": {"const": "symmetric"}}},
}

SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["pairs"],
    "properties": {"pairs": {"type": "array", "items": VERDICT_SCHEMA}},
}

INSTRUCTIONS = """\
You are judging how two specification claims relate. Answer about these two claims only.

Choose exactly ONE relation:
- none: the two claims are independent; they can both hold and neither is about the other.
- refines: one is a more specific statement of the other.
- depends_on: one presupposes the other.
- duplicates: both state the same claim.
- subsumes: one already implies the other.
- contradicts: both cannot hold at the same time.

Different numbers are NOT automatically a contradiction (R16). Two claims contradict only if
both must hold for the SAME thing at the SAME time. These are consistent — answer none:
- a shorter limit inside a longer one: a link valid for 24 hours inside an archive kept 30 days;
- a window and what happens after it: restoring on day 13 inside a 14-day recovery window;
- a rule and a clarification of it: "kept 30 days" and "a download on day 29 does not extend it".
Do not calculate: if deciding needs arithmetic the text does not do, answer none.

An acceptance criterion that restates its requirement in Given/Then form is the specification's
design, not a duplication: answer none unless the two say different things.

One thing often has several names in a specification ("export archive", "workspace export").
Judge what the two claims say, not what they call it: if the terms listed under each claim are
the same thing or kinds of one thing, treat them as one thing unless the text itself
distinguishes them. A different name is not a different object.

Direction: for refines, depends_on and subsumes, say which way it runs — a_to_b means A refines
(or depends on, or subsumes) B. For none, duplicates and contradicts the answer is symmetric.

Answer for EVERY pair you are given, using its exact pair_id.

Quote VERBATIM: quotes.a must appear in A's text and quotes.b in B's text, word for word.
Quote the words that decide your answer, not the whole claim.

Say confidence: low when the claims are too vague to be sure, and judge them anyway.
The rationale is one sentence, naming what the two claims disagree or agree about.
"""


@dataclass(frozen=True)
class Verdict:
    relation: str
    direction: str
    rationale: str
    quotes: dict[str, str]
    confidence: str
    provisional: bool = False
    attempts: int = 1                 # 2 when the first answer failed a check (§4.2)
    answer: Answer | None = None


@dataclass
class PairItem:
    """One pair to judge: both nodes, and what the graph knows about their terms (F6 D17)."""

    a: Mapping[str, Any]
    b: Mapping[str, Any]
    related_terms: list[str] = field(default_factory=list)
    key: str = ""                     # F5's `pair_key`: what the judgment lock is keyed by

    @property
    def pair_id(self) -> str:
        return pair_id(self.a, self.b)


@dataclass
class BatchOutcome:
    verdicts: dict[str, Verdict] = field(default_factory=dict)      # pair id -> verdict
    judgments: dict[str, str] = field(default_factory=dict)         # pair id -> J id (with a lock)
    failures: dict[str, str] = field(default_factory=dict)          # checked twice, still wrong


def pair_id(a: Mapping[str, Any], b: Mapping[str, Any]) -> str:
    return f"{a['id']}|{b['id']}"


def build_question(a: Mapping[str, Any], b: Mapping[str, Any], note: str | None = None,
                   related_terms: Sequence[str] = ()) -> Question:
    """One pair, as its own question — the shape a re-ask uses."""
    return build_batch_question([PairItem(a, b, list(related_terms))], note)


def build_batch_question(items: Sequence["PairItem"], note: str | None = None) -> Question:
    """⚑ R21 (rel01 D30's lever, applied to F6): one call, many pairs.

    A headless call carries ≈ 22k tokens of harness prompt whatever it asks, so judging one pair
    per call made the check phase the most expensive part of a compile (M4 gate, I-75). Each pair's
    answer is still validated on its own, and a failure re-asks **that pair alone** — the condition
    F3 §4.3 rule 4 puts on any batching.
    """
    parts = [INSTRUCTIONS]
    if note:
        parts.append(f"\nThe previous answer was rejected. {note}\nTry again, carefully.\n")
    for item in items:
        parts.append(f"\n=== PAIR {item.pair_id} ===\n")
        for label, node in (("A", item.a), ("B", item.b)):
            parts.append(_describe(label, node))
        if item.related_terms:
            parts.append("HOW THEIR TERMS RELATE:\n"
                         + "".join(f"- {line}\n" for line in item.related_terms))
    return Question(kind="q-pair", schema_version=SCHEMA_VERSION, schema=SCHEMA,
                    prompt="".join(parts), payload={"pair_ids": [i.pair_id for i in items]})


def _describe(label: str, node: Mapping[str, Any]) -> str:
    canonical = node["canonical"]
    source = node["source"]
    return (
        f"\n--- CLAIM {label}: {node['id']} ---\n"
        f"layer: {node['layer']} · family: {node['family']}\n"
        f"source: {source['file']}:{source['lines'][0]}\n"
        f"canonical: subject={canonical['subject']} · modality={canonical['modality']} · "
        f"response={canonical['response']}\n"
        f"terms: {', '.join(t['term'] for t in node.get('terms') or []) or '(none)'}\n"
        f"text:\n{node['text']}\n"
    )


def judge(a: Mapping[str, Any], b: Mapping[str, Any], backend: Backend, *,
          settings: Any, note: str | None = None, related_terms: Sequence[str] = ()) -> Verdict:
    """One pair — the shape the tests and a re-ask use. `judge_batch` is what a run calls."""
    item = PairItem(a, b, list(related_terms))
    outcome = judge_batch([item], backend, settings=settings, note=note)
    if item.pair_id in outcome.failures:
        raise GuardFailure(outcome.failures[item.pair_id])
    return outcome.verdicts[item.pair_id]


def judge_batch(items: Sequence[PairItem], backend: Backend, *, settings: Any,
                note: str | None = None, lock: Any | None = None) -> BatchOutcome:
    """Judge a batch; each answer is checked alone and a failure re-asks that pair (R21)."""
    outcome = BatchOutcome()

    def accept(item: PairItem, payload: dict[str, Any]) -> None:
        outcome.verdicts[item.pair_id] = _verdict(payload, item)

    result = ask_each(
        list(items),
        item_id=lambda item: item.pair_id,
        backend=backend,
        build_question=lambda batch, note: build_batch_question(batch, note),
        list_key="pairs",
        id_key="pair_id",
        accept=accept,
        note=note,
        lock=lock,
        lock_input=lambda item: {"pair_key": item.key or item.pair_id},
    )
    outcome.failures, outcome.judgments = result.failures, result.judgments
    return outcome


def _verdict(payload: Mapping[str, Any], item: PairItem) -> Verdict:
    """Everything the answer claims, checked before it is believed (G5, the direction rule, G2)."""
    if payload["relation"] in SYMMETRIC_ONLY and payload["direction"] != "symmetric":
        raise GuardFailure(
            f"{payload['relation']} is symmetric: direction must be 'symmetric', "
            f"not {payload['direction']!r}")
    for label, node in (("a", item.a), ("b", item.b)):
        quote = payload["quotes"][label]
        try:
            anchor_quotes([quote], node["text"], [])
        except GuardFailure as failure:
            raise GuardFailure(
                f"quotes.{label}: {failure} — quote {node['id']} verbatim") from failure
    return Verdict(relation=payload["relation"], direction=payload["direction"],
                   rationale=payload["rationale"], quotes=dict(payload["quotes"]),
                   confidence=payload["confidence"],
                   provisional="ambiguous" in (item.a["status"], item.b["status"]))
