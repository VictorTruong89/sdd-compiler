"""Q-ATOM — prose blocks in, atomic claims out (F3 §4.2).

**Batched by default (rel01 D30).** A headless Claude Code call carries ~22k
tokens of harness prompt whatever it is asked, so one call per block would cost
about $13 and an hour for this repository alone. One call per *batch* of blocks
costs roughly the same as one call, and F3 §4.3 rule 4 already allows batching —
on one condition, which this module enforces: **each block's answer is validated
on its own, and a failure re-asks only that block.**

The atom tests (P-2) and the role list (P-3) are stated in the prompt; the guards
that check the answer are in `guards.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..llm import Backend, Question
from .batch import ask_each
from .guards import anchor_quotes, check_coverage

SCHEMA_VERSION = "q-atom/1"

ATOM_KINDS = ("requirement", "constraint", "assumption", "verification", "decision")
SENTENCE_ROLES = ATOM_KINDS + ("definition", "rationale", "example", "context", "open_question")

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["blocks"],
    "properties": {
        "blocks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["block_id", "sentences", "atoms"],
                "properties": {
                    "block_id": {"type": "string"},
                    "sentences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["quote", "role"],
                            "properties": {
                                "quote": {"type": "string"},
                                "role": {"type": "string", "enum": list(SENTENCE_ROLES)},
                            },
                        },
                    },
                    "atoms": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["kind", "quotes"],
                            "properties": {
                                "kind": {"type": "string", "enum": list(ATOM_KINDS)},
                                "quotes": {"type": "array", "items": {"type": "string"},
                                           "minItems": 1},
                            },
                        },
                    },
                },
            },
        }
    },
}

_INSTRUCTIONS = """\
You are splitting specification prose into atomic claims.

An atom is ONE claim that can be judged true or false on its own. Use these tests:
- single verdict: one observation or one test could decide the whole statement;
- independent change: someone could dispute or change one part and keep the other;
- single layer: the statement belongs to one layer of description, not two;
- stands alone: after resolving pronouns, each piece still means something.
Split on distinct obligations, not on list members that share one obligation.

Label EVERY sentence with a role: requirement, constraint, assumption, verification,
decision, definition, rationale, example, context, open_question. Only the first five
become atoms.

Quote VERBATIM from the block: every quote must appear in the block character for
character. Do not paraphrase, do not fix typos, do not add anything the block does
not say. Answer for each block you are given, using its exact block_id.
"""


@dataclass
class Atom:
    """One claim found in one block, with the offsets code computed for it."""

    block_id: str
    kind: str
    quotes: list[str]
    spans: list[tuple[int, int]]

    @property
    def text(self) -> str:
        return " ".join(self.quotes)


@dataclass
class AtomizeOutcome:
    atoms: list[Atom] = field(default_factory=list)
    annotations: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    failures: dict[str, str] = field(default_factory=dict)
    judgments: dict[str, str] = field(default_factory=dict)       # block id -> J id (with a lock)


def build_question(blocks: list[dict[str, Any]], note: str | None = None) -> Question:
    """One question for a batch of blocks (or one block, on a re-ask)."""
    parts = [_INSTRUCTIONS]
    if note:
        parts.append(f"\nThe previous answer was rejected. {note}\nTry again, carefully.\n")
    for block in blocks:
        heading = " > ".join(block.get("heading_path") or []) or "(no heading)"
        header = block.get("table_header")
        parts.append(
            f"\n--- BLOCK {block['id']} ---\n"
            f"section: {heading}\n"
            + (f"table header: {header}\n" if header else "")
            + f"kind: {block.get('kind', 'paragraph')}\n"
            f"text:\n{block['text']}\n"
        )
    return Question(
        kind="q-atom",
        schema_version=SCHEMA_VERSION,
        schema=SCHEMA,
        prompt="".join(parts),
        payload={"block_ids": [block["id"] for block in blocks]},
    )


def atomize_blocks(
    blocks: list[dict[str, Any]], backend: Backend, note: str | None = None, lock: Any | None = None
) -> AtomizeOutcome:
    """Atomize a batch, re-asking once for each block whose answer failed a guard."""
    outcome = AtomizeOutcome()
    result = ask_each(
        blocks,
        item_id=lambda block: block["id"],
        backend=backend,
        build_question=build_question,
        list_key="blocks",
        id_key="block_id",
        accept=lambda block, payload: _accept(block, payload, outcome),
        note=note,
        lock=lock,
        lock_input=lock_input,
    )
    outcome.failures, outcome.judgments = result.failures, result.judgments
    return outcome


def lock_input(block: dict[str, Any]) -> dict[str, Any]:
    """What the answer depends on — not the block id, so a moved block keeps its answer."""
    return {"text": block["text"], "kind": block.get("kind"),
            "heading_path": list(block.get("heading_path") or []),
            "table_header": block.get("table_header")}


# -- pieces -----------------------------------------------------------------

def _accept(block: dict[str, Any], payload: dict[str, Any], outcome: AtomizeOutcome) -> None:
    """Apply G2 and G3 to one block's answer, then keep its atoms."""
    text = block["text"]
    claimed: list[tuple[int, int]] = []
    atoms: list[Atom] = []

    for atom in payload["atoms"]:
        anchors = anchor_quotes(list(atom["quotes"]), text, claimed)
        atoms.append(
            Atom(
                block_id=block["id"],
                kind=atom["kind"],
                quotes=[anchor.quote for anchor in anchors],
                spans=[anchor.span for anchor in anchors],
            )
        )

    labelled = [
        sentence["quote"] for sentence in payload["sentences"]
        if sentence["role"] not in ATOM_KINDS
    ]
    check_coverage(text, claimed, labelled)

    outcome.atoms.extend(atoms)
    annotations = [
        (sentence["role"], sentence["quote"])
        for sentence in payload["sentences"]
        if sentence["role"] in ("rationale", "example")
    ]
    if annotations:
        outcome.annotations[block["id"]] = annotations
