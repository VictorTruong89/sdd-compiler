"""Builders for F7 tests: a small valid store, written with the real writers, no model call."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from sdd_compiler.commands import init
from sdd_compiler.ingest.pipeline import _read_text
from sdd_compiler.model.status import derive_status
from sdd_compiler.store.graph import Graph, write_graph
from sdd_compiler.store.jsonl import write_jsonl
from sdd_compiler.ingest.identity import BLOCK_KEY_ORDER

SPEC = "sdd/specs/a.md"


def b(bid, source=SPEC, heads=("T", "S"), line=1, text=None, kind="paragraph", **extra):
    record = {"id": bid, "source": source, "kind": kind, "heading_path": list(heads),
              "lines": [line, line + text.count("\n") if text else line],
              "text": text if text is not None else f"Text of {bid}.",
              "text_hash": "sha256:x", "parent_block": None, "parent_relation": None,
              "table_header": None, "in_blockquote": False, "first_seen_run": "R-000001",
              "last_changed_run": "R-000001", "removed_run": None, "atomized_hash": "sha256:x"}
    record.update(extra)
    return record


def n(nid, block, kind="requirement", text=None, modality="MUST", layer="L3", label=None,
      family="term:a", **extra):
    record = {
        "id": nid, "kind": kind, "_block": block,
        "text": text or f"Claim {nid}.",
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "thing",
                      "modality": modality, "response": "do", "quantities": []},
        "terms": [], "label": label, "primary_term": family,
        "layer": layer, "layer_answers": {}, "layer_hint": None,
        "family": family, "family_rule": "subject", "components": [], "scope_selector": None,
        "verifies": None, "decision": None, "annotations": [], "keywords": ["thing"],
        "ambiguity": [], "conflict_ids": [], "related_conflict_nodes": [], "stale_reasons": [],
        "last_checked_run": "R-000001", "flags": [], "status": "validated", "judgments": [],
    }
    if modality is None:
        record["ambiguity"] = [{"kind": "missing_modality", "quote": None, "detail": "no modal verb"}]
    record.update(extra)
    return record


def link(a, kind, to):
    return {"from": a, "type": kind, "to": to, "provenance": "code", "judgment": None,
            "rationale": None, "quotes": []}


def conflict(cid, kind, members, state="open", rationale="the rationale"):
    return {"id": cid, "kind": kind, "members": sorted(members), "rationale": rationale,
            "quotes": {m: f"quote of {m}" for m in members}, "state": state,
            "resolved_reason": None, "detected_run": "R-000001", "resolved_run": None,
            "judgment": "J-000001"}


def term(tid, definition=None, aliases=()):
    return {"id": tid, "canonical": tid[5:].replace("_", " "), "aliases": list(aliases),
            "kind": "entity", "definition": definition, "defined_by": None,
            "status": "proposed", "broader": None}


def make_store(root: Path, blocks, nodes=(), links=(), conflicts=(), terms=(), verdicts=(),
               profile: str | None = None) -> Path:
    """Write `root` as a compiled repository: spec files from the blocks' texts, `.sdd/`, verdicts.

    `verdicts` is (conflict id, "real" | "false", note). A conflict's record is written first, so
    the adjudication names its judgment and members exactly (F6 D14: current, not stale).
    """
    root = Path(root)
    init(root)
    if profile:
        (root / ".sdd" / "profile.yaml").write_text(profile, encoding="utf-8")
    store = root / ".sdd"
    by_id = {blk["id"]: blk for blk in blocks}
    sources: dict[str, list[dict[str, Any]]] = {}
    for blk in blocks:
        sources.setdefault(blk["source"], []).append(blk)
    records = []
    for path, group in sorted(sources.items()):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("\n\n".join(x["text"] for x in group) + "\n", encoding="utf-8")
        records.append({"path": path, "file_hash": "sha256:" + hashlib.sha256(
            _read_text(file).encode("utf-8")).hexdigest(), "last_ingest_run": "R-000001"})
    write_jsonl(store / "blocks.jsonl", blocks, BLOCK_KEY_ORDER, sort_key=lambda r: r["id"])
    write_jsonl(store / "sources.jsonl", records, ("path", "file_hash", "last_ingest_run"),
                sort_key=lambda r: r["path"])
    (store / "lock").mkdir(exist_ok=True)
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')

    full = []
    for node in nodes:
        node = dict(node)
        blk = by_id[node.pop("_block")]
        node["source"] = {"file": blk["source"], "block_id": blk["id"],
                          "heading_path": blk["heading_path"], "lines": blk["lines"],
                          "spans": [[0, max(len(blk["text"]), 1)]]}
        node["status"] = derive_status(node)
        full.append(node)
    graph = Graph(nodes={x["id"]: x for x in full}, terms={t["id"]: t for t in terms},
                  links=list(links), conflicts={c["id"]: c for c in conflicts}, reviews={},
                  counters={"node": 999, "conflict": 999, "judgment": 999, "review": 0})
    write_graph(store, graph)
    if verdicts:
        from sdd_compiler.conflicts.adjudicate import record_adjudication
        for cid, verdict, note in verdicts:
            record_adjudication(store, cid, verdict, note=note, date="2026-09-30")
    return root


def fixture(tmp_path: Path) -> Path:
    """A store with a foundation, a dependency between specs, a table, a contract, acceptance
    criteria, a Traceability section, a real duplicate, one settled and one unsettled contradiction."""
    V, F1, F2 = "sdd/specs/vision.md", "sdd/specs/F1_share/spec.md", "sdd/specs/F2_keep/spec.md"
    head = "| ID | Rule |"
    blocks = [
        b("B-01", V, ("Vision", "Why"), 1, "The product shares exports."),
        b("B-02", F1, ("F1 — Share", "1. Goal"), 1, "A share link MUST expire after 30 days."),
        b("B-03", F1, ("F1 — Share", "2. Rules"), 5, "| R1 | one |", kind="table_row", table_header=head),
        b("B-04", F1, ("F1 — Share", "2. Rules"), 6, "| R2 | two |", kind="table_row", table_header=head),
        b("B-05", F1, ("F1 — Share", "3. Contracts"), 9, "**CT-1.1 — Link record** (the record)"),
        b("B-06", F1, ("F1 — Share", "3. Contracts"), 11, '```json\n{"id": "L-1"}\n```', kind="code"),
        b("B-07", F1, ("F1 — Share", "4. Acceptance"), 15, "AC-1.1: Given a link, then it expires."),
        b("B-08", F1, ("F1 — Share", "9. Traceability"), 20, "| AC-1.1 | test_share.py |"),
        b("B-09", F2, ("F2 — Keep", "1. Goal"), 1, "An archive MUST be kept 30 days."),
        b("B-10", F2, ("F2 — Keep", "1. Goal"), 3, "A share link MUST expire after 30 days, always."),
        b("B-11", F2, ("F2 — Keep", "2. Rules"), 6, "A deleted archive MUST NOT be served."),
        b("B-12", F2, ("F2 — Keep", "2. Rules"), 8, "Backups SHOULD be encrypted."),
    ]
    C = {"families": [], "layers": [], "terms": [], "categories": []}
    nodes = [
        n("N-000001", "B-01", text="The product shares exports.", layer="L0", modality=None),
        n("N-000002", "B-02", text="A share link MUST expire after 30 days.", layer="L1",
          family="term:share_link", terms=[{"term": "term:share_link", "role": "subject", "quote": "share link"}]),
        n("N-000003", "B-04", text="R2: two.", layer="L5"),
        n("CT-1.1", "B-06", text='{"id": "L-1"}', layer="C", label="CT-1.1",
          scope_selector={**C, "families": ["term:share_link"]}),
        n("AC-1.1", "B-07", kind="verification", layer="V", label="AC-1.1",
          text="Given a link, then it expires."),
        n("N-000009", "B-09", text="An archive MUST be kept 30 days.", layer="L1"),
        n("N-000010", "B-10", text="A share link MUST expire after 30 days, always.", layer="L1",
          family="term:share_link", terms=[{"term": "term:share_link", "role": "subject", "quote": "share link"}]),
        n("N-000011", "B-11", text="A deleted archive MUST NOT be served.", layer="C", modality="MUST NOT",
          scope_selector=C),
        n("N-000012", "B-12", text="Backups SHOULD be encrypted.", layer="L5", modality="SHOULD"),
    ]
    links = [link("N-000009", "depends_on", "N-000002"), link("AC-1.1", "verifies", "N-000002")]
    conflicts = [conflict("CF-000001", "duplication", ["N-000002", "N-000010"]),
                 conflict("CF-000002", "contradiction", ["N-000002", "N-000009"]),
                 conflict("CF-000003", "contradiction", ["N-000011", "N-000012"])]
    return make_store(tmp_path, blocks, nodes, links, conflicts,
                      terms=[term("term:share_link", "A share link is a URL.", ["url"])],
                      verdicts=[("CF-000001", "real", "same rule"), ("CF-000002", "real", "F1 holds")])
