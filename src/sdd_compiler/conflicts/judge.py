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

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from ..atomize.guards import GuardFailure, anchor_quotes, check_schema
from ..llm import Answer, Backend, Question

SCHEMA_VERSION = "q-pair/1"

RELATIONS = ("none", "refines", "depends_on", "duplicates", "subsumes", "contradicts")
SYMMETRIC_ONLY = ("none", "duplicates", "contradicts")
DIRECTIONS = ("a_to_b", "b_to_a", "symmetric")

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["relation", "direction", "rationale", "quotes", "confidence"],
    "properties": {
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

INSTRUCTIONS = """\
You are judging how two specification claims relate. Answer about these two claims only.

Choose exactly ONE relation:
- none: the two claims are independent; they can both hold and neither is about the other.
- refines: one is a more specific statement of the other.
- depends_on: one presupposes the other.
- duplicates: both state the same claim.
- subsumes: one already implies the other.
- contradicts: both cannot hold at the same time.

Direction: for refines, depends_on and subsumes, say which way it runs — a_to_b means A refines
(or depends on, or subsumes) B. For none, duplicates and contradicts the answer is symmetric.

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


def build_question(a: Mapping[str, Any], b: Mapping[str, Any], note: str | None = None) -> Question:
    parts = [INSTRUCTIONS]
    if note:
        parts.append(f"\nThe previous answer was rejected. {note}\nTry again, carefully.\n")
    for label, node in (("A", a), ("B", b)):
        parts.append(_describe(label, node))
    return Question(kind="q-pair", schema_version=SCHEMA_VERSION, schema=SCHEMA,
                    prompt="".join(parts), payload={"a": a["id"], "b": b["id"]})


def _describe(label: str, node: Mapping[str, Any]) -> str:
    canonical = node["canonical"]
    source = node["source"]
    return (
        f"\n--- CLAIM {label}: {node['id']} ---\n"
        f"layer: {node['layer']} · family: {node['family']}\n"
        f"source: {source['file']}:{source['lines'][0]}\n"
        f"canonical: subject={canonical['subject']} · modality={canonical['modality']} · "
        f"response={canonical['response']}\n"
        f"text:\n{node['text']}\n"
    )


def judge(a: Mapping[str, Any], b: Mapping[str, Any], backend: Backend, *,
          settings: Any, note: str | None = None) -> Verdict:
    """Ask, check, and re-ask once on a failed check (F6 §4.2; F3 §4.3 rule 3)."""
    try:
        return _ask(a, b, backend, settings, note)
    except GuardFailure as failure:
        verdict = _ask(a, b, backend, settings, note=str(failure))
        return replace(verdict, attempts=2)


def _ask(a: Mapping[str, Any], b: Mapping[str, Any], backend: Backend,
         settings: Any, note: str | None) -> Verdict:
    answer = backend.ask(build_question(a, b, note))
    payload = answer.data
    check_schema(payload, SCHEMA)
    if payload["relation"] in SYMMETRIC_ONLY and payload["direction"] != "symmetric":
        raise GuardFailure(
            f"{payload['relation']} is symmetric: direction must be 'symmetric', "
            f"not {payload['direction']!r}")
    for label, node in (("a", a), ("b", b)):
        quote = payload["quotes"][label]
        try:
            anchor_quotes([quote], node["text"], [])
        except GuardFailure as failure:
            raise GuardFailure(
                f"quotes.{label}: {failure} — quote {node['id']} verbatim") from failure
    provisional = "ambiguous" in (a["status"], b["status"])
    return Verdict(relation=payload["relation"], direction=payload["direction"],
                   rationale=payload["rationale"], quotes=dict(payload["quotes"]),
                   confidence=payload["confidence"], provisional=provisional, answer=answer)
