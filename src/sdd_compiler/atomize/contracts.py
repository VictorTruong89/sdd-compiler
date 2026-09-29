"""F3 §4.5a, D39 — a fenced contract block is one node, formed whole; F2 D21 — it takes its title's id.

A contract is a record shape, file format or output stated by its form (F1 D15).
Q-ATOM is not asked: code forms the one atom from the text between the fences.
Its **lead** — the paragraph directly before it in the same file and section,
normally `**CT-1.1 — Block record** (…)` — names what it describes, so Q-DESC
reads it, and the lead's `CT-` id becomes the node's.

`annotate` returns **copies** of the pending blocks carrying two transient keys,
never written to `blocks.jsonl`:

- a contract block: `contract = {"lead": text | None, "id": "CT-1.1" | None}`;
- a lead whose `CT-` id went to its contract: `id_given_to = <contract block id>`,
  so its own nodes keep the id as `label` only (F2 D21).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..ingest.identity import fence_language
from ..model.ids import find_human_id
from .qatom import Atom


def contract_atom(block: Mapping[str, Any]) -> Atom:
    """One `requirement` atom: the block's text between its opening and closing fence lines."""
    text = block["text"]
    start = text.index("\n") + 1 if "\n" in text else len(text)
    end = len(text.rstrip())
    last = text.rfind("\n", start, end)
    if last >= start and text[last + 1:end].lstrip().startswith(("```", "~~~")):
        end = last                                        # a closing fence; an open one runs to the end
    while end > start and text[end - 1] in " \n":
        end -= 1
    return Atom(block_id=block["id"], kind="requirement", quotes=[text[start:end]], spans=[(start, end)])


def annotate(pending: Sequence[Mapping[str, Any]], all_blocks: Sequence[Mapping[str, Any]],
             languages: Sequence[str]) -> list[dict[str, Any]]:
    """Copies of `pending`, with each contract's lead and id, and each lead that gave its id away."""
    wanted = {language.lower() for language in languages}
    ordered = sorted(all_blocks, key=lambda b: (b["source"], b["lines"][0]))
    contracts: dict[str, dict[str, Any]] = {}
    given: dict[str, str] = {}
    for previous, block in zip([None, *ordered], ordered):
        if block["kind"] != "code" or fence_language(dict(block)) not in wanted:
            continue
        lead = previous if (previous is not None and previous["kind"] == "paragraph"
                            and previous["source"] == block["source"]
                            and previous["heading_path"] == block["heading_path"]) else None
        human = find_human_id(lead) if lead is not None else None
        human = human if human and human.startswith("CT-") else None
        contracts[block["id"]] = {"lead": lead["text"] if lead else None, "id": human}
        if human:
            given[lead["id"]] = block["id"]

    result = []
    for block in pending:
        copy = dict(block)
        if block["id"] in contracts:
            copy["contract"] = contracts[block["id"]]
        if block["id"] in given:
            copy["id_given_to"] = given[block["id"]]
        result.append(copy)
    return result
