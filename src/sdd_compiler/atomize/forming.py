"""F3 §4.5 — one described, placed atom becomes one F2 node record (CT-2.1).

Everything here is deterministic: the model's part ended with Q-DESC. A
`NodeDraft` keeps the pieces a record is built from, so the parts that depend
on *other* nodes — a verification's family depends on what it verifies (F2 D13)
— can be settled after every node of the run exists, and the record built once.

⚑ `source.spans` are offsets into the **block's** text (F3 D15). The block's
verbatim text is stored with the block (F1 CT-1.1), so block id plus span is a
complete address, and a node never needs the whole file to be located.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..model.family import derive_family
from ..model.keywords import keywords
from ..model.layers import LAYERS, QUESTIONS
from ..model.schema import FLAGS
from ..model.status import derive_status
from .describe import Description
from .guards import GuardFailure, locate_quote
from .placement_types import PlacedAtom

_CITATION = re.compile(r"(?<![\w.-])((?:AC|CT)-\d+\.\d+|N-\d{6,})(?!\w|\.\d)")
_LOCAL_CITATION = re.compile(r"(?<![\w.-])([A-Z]{1,2}\d{1,3})(?![\w.-]\w)")    # F2 D20


@dataclass
class NodeDraft:
    node_id: str
    placed: PlacedAtom
    block: Mapping[str, Any]
    terms: list[dict[str, Any]]              # resolved: {term, kind, role, quote}
    label: str | None
    layer_hint: str | None
    annotations: list[dict[str, Any]] = field(default_factory=list)
    pending_terms: list[str] = field(default_factory=list)
    verifies: list[str] | None = None
    verified_families: list[str] = field(default_factory=list)
    alignment: str = "new"                               # F3 §4.6
    old: Mapping[str, Any] | None = None                 # the node it keeps the id of

    @property
    def description(self) -> Description:
        return self.placed.description

    @property
    def layer(self) -> str | None:
        return self.placed.placement.layer

    @property
    def text(self) -> str:
        block_text = self.block["text"]
        return " … ".join(block_text[start:end] for start, end in self.placed.atom.spans)

    def record(self, run_id: str) -> dict[str, Any]:
        if self.alignment == "unchanged" and self.old is not None:
            # Same text: the record is kept — judgments, check state and all —
            # except where the claim now sits (F3 §4.6).
            return {**self.old, "label": self.label, "source": self._source()}
        description = self.description
        placement = self.placed.placement
        selector = (scope_selector(self.terms, description.scope_layers)
                    if self.layer == "C" else None)
        family = derive_family(
            self.layer, description.canonical["subject"], self.terms,
            verified_families=self.verified_families,
            scope_families=selector["families"] if selector else (),
        )
        ambiguity = [*description.ambiguity, *placement.ambiguity, *family.ambiguity]
        ambiguity += [
            {"kind": "pending_review", "quote": None, "detail": f"term {term} awaits review"}
            for term in self.pending_terms
        ]
        flags = [flag for flag in FLAGS if flag in {*description.flags, *family.flags}]
        text = self.text
        node: dict[str, Any] = {
            "id": self.node_id,
            "kind": description.kind,
            "source": self._source(),
            "text": text,
            "canonical": description.canonical,
            "terms": [{"term": t["term"], "role": t["role"], "quote": t["quote"]} for t in self.terms],
            "label": self.label,
            "primary_term": family.family if (family.family or "").startswith("term:") else None,
            "layer": self.layer,
            "layer_answers": {
                q: {"answer": description.layer_answers[q]["answer"],
                    "quote": description.layer_answers[q]["quote"]}
                for q in QUESTIONS
            },
            "layer_hint": self.layer_hint,
            "family": family.family,
            "family_rule": family.rule,
            "components": [],
            "scope_selector": selector,
            "verifies": (list(self.verifies or []) if self.layer == "V" else None),
            "decision": ({**description.decision, "affects": []}
                         if description.kind == "decision" and description.decision else None),
            "annotations": self.annotations,
            "keywords": keywords(text),
            "ambiguity": ambiguity,
            "conflict_ids": [],
            "related_conflict_nodes": [],
            "stale_reasons": [],
            "last_checked_run": None,
            "flags": flags,
            "status": "unchecked",
            "judgments": sorted(self.placed.judgments),
        }
        node["status"] = derive_status(node)
        return node

    def _source(self) -> dict[str, Any]:
        return {
            "file": self.block["source"],
            "block_id": self.block["id"],
            "heading_path": list(self.block.get("heading_path") or []),
            "lines": _lines(self.block, self.placed.atom.spans),
            "spans": [list(span) for span in self.placed.atom.spans],
        }


def scope_selector(terms: Sequence[Mapping[str, Any]], scope_layers: Sequence[str]) -> dict[str, list[str]]:
    """F2 D13, AC-2.24 — a constraint's scope, from its scope-role terms and `scope_layers`."""
    scoped = [t for t in terms if t["role"] == "scope"]
    return {
        "families": sorted({t["term"] for t in scoped if t["kind"] in ("entity", "data", "event")}),
        "layers": [layer for layer in LAYERS if layer in set(scope_layers)],
        "terms": sorted({t["term"] for t in scoped}),
        "categories": sorted({t["term"] for t in scoped if t["kind"] == "category"}),
    }


def resolve_verifies(
    nodes: Mapping[str, Mapping[str, Any]], verifies_texts: Mapping[str, str | None]
) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    """F2 D13, AC-2.25 — each id or `AC-`/`CT-` label a `V` node cites → the nodes carrying it.

    F2 D20: a local label (`S4`) resolves only to nodes of the citing node's own file, and only
    when one block carries it there; a label on two blocks of a file is ambiguous and resolves
    to nothing."""
    by_label: dict[str, list[str]] = {}
    local: dict[tuple[str, str], list[str]] = {}
    for node_id, node in nodes.items():
        label = node.get("label")
        if label and "-" in label:
            by_label.setdefault(label, []).append(node_id)
        elif label:
            local.setdefault((_file(node), label), []).append(node_id)

    verifies: dict[str, list[str]] = {}
    links: list[dict[str, Any]] = []
    for node_id in sorted(verifies_texts):
        cited_text = f"{nodes[node_id]['text']} {verifies_texts[node_id] or ''}"
        targets: set[str] = set()
        for citation in _CITATION.findall(cited_text):
            if citation in nodes:
                targets.add(citation)
            targets.update(by_label.get(citation, []))
        for citation in _LOCAL_CITATION.findall(cited_text):
            carriers = local.get((_file(nodes[node_id]), citation), [])
            if len({(nodes[c].get("source") or {}).get("block_id") for c in carriers}) == 1:
                targets.update(carriers)
        targets.discard(node_id)
        verifies[node_id] = sorted(targets)
        links += [{"from": node_id, "type": "verifies", "to": target, "provenance": "code",
                   "judgment": None, "rationale": None, "quotes": []} for target in verifies[node_id]]
    return verifies, links


def _file(node: Mapping[str, Any]) -> str | None:
    return (node.get("source") or {}).get("file")


def block_annotations(
    block: Mapping[str, Any], pairs: Sequence[tuple[str, str]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The block's rationale and example spans, and the ones that could not be located.

    ⚑ F3 D35 (R16, I-67): an annotation is context, never a claim, so a quote that is not in the
    block is **dropped and reported**, not raised. It used to raise here, after every model call
    of the run had been paid for, and one merged rationale sentence lost a whole compile.
    """
    kept, dropped = [], []
    for role, quote in pairs:
        try:
            span = locate_quote(quote, block["text"])
        except GuardFailure:
            dropped.append({"block": block["id"], "file": block["source"],
                            "lines": list(block["lines"]), "role": role, "quote": quote})
            continue
        kept.append({"role": role, "text": quote, "spans": [list(span)]})
    return kept, dropped


def layer_hint(heading_path: Sequence[str], hints: Mapping[str, Mapping[str, Any]] | None) -> str | None:
    """A profile hint whose heading matches the node's heading path — recorded, never obeyed (P-12)."""
    headings = {heading.strip().lower() for heading in heading_path}
    for layer in LAYERS:
        for hint in (hints or {}).get(layer, {}).get("hints", []):
            if hint.lstrip("#").strip().lower() in headings:
                return layer
    return None


def _lines(block: Mapping[str, Any], spans: Sequence[tuple[int, int]]) -> list[int]:
    text, first = block["text"], block["lines"][0]
    start = min(span[0] for span in spans)
    end = max(span[1] for span in spans)
    return [first + text[:start].count("\n"), first + text[:max(start, end - 1)].count("\n")]
