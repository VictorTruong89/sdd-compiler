"""The worked example of core-working-principle.md §9 as a graph — the M3 golden fixture.

14 nodes in three families (share_link, file, (global)). N-000003 and N-000005 are in one
open conflict, so the share_link row carries a conflict (F4 AC-4.14).
"""
from __future__ import annotations

from sdd_compiler.model.status import derive_status
from sdd_compiler.store.graph import Graph

SPEC = "specs/sharing.md"
NODES = [  # id, line, layer, family, text
    ("N-000001", 4, "L1", "term:share_link", "Owners can create a share link for a file they own."),
    ("N-000002", 5, "L1", "term:share_link", "A share link expires 30 days after it is created."),
    ("N-000003", 6, "L1", "term:share_link", 'Visitors who open an expired share link see a "link expired" page.'),
    ("N-000004", 7, "C", "term:share_link", "Share links must never reveal the owner's email address."),
    ("N-000005", 8, "L1", "term:share_link", "When a file is deleted, its share links must stop working."),
    ("N-000006", 11, "L1", "term:file", "Owners can delete a file they own."),
    ("N-000007", 14, "L2", "term:share_link", "LinkService owns share links."),
    ("N-000008", 14, "L2", "term:file", "FileService owns files."),
    ("N-000009", 15, "L3", "term:share_link", "GET /s/{token} returns 200 with the file stream when the token is valid"),
    ("N-000010", 15, "L3", "term:share_link", "and 404 when it is expired or unknown."),
    ("N-000011", 16, "L4", "term:share_link", "A share link record stores token, file_id, created_at and expires_at."),
    ("N-000012", 17, "L5", "term:share_link", "expires_at is set to created_at plus 30 days when the link is created."),
    ("N-000013", 20, "V", "term:share_link", "Test: a link created 31 days ago returns 404."),
    ("N-000014", 23, "C", "(global)", "Every public endpoint must respond within 300 ms."),
]
USES = {"N-000001": ["term:file", "term:owner"], "N-000005": ["term:file"], "N-000006": ["term:owner"],
        "N-000009": ["term:endpoint"], "N-000010": ["term:endpoint"], "N-000014": ["term:endpoint"]}


def term(term_id, kind, aliases=()):
    return {"id": term_id, "canonical": term_id[5:].replace("_", " "), "aliases": list(aliases),
            "kind": kind, "definition": None, "defined_by": None, "status": "confirmed", "broader": None}


def node(node_id, line, layer, family, text):
    terms = [{"term": family, "role": "subject", "quote": "x"}] if family.startswith("term:") else []
    terms += [{"term": t, "role": "scope" if layer == "C" else "response", "quote": "x"}
              for t in USES.get(node_id, [])]
    record = {
        "id": node_id, "kind": "verification" if layer == "V" else "constraint" if layer == "C" else "requirement",
        "source": {"file": SPEC, "block_id": f"B-{line:06d}", "heading_path": ["Sharing"], "lines": [line, line],
                   "spans": [[0, len(text)]]},
        "text": text,
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "x", "modality": "MUST",
                      "response": "x", "quantities": []},
        "terms": terms, "label": None, "primary_term": family if family.startswith("term:") else None,
        "layer": layer, "layer_answers": {}, "layer_hint": None, "family": family,
        "family_rule": "constraint" if layer == "C" and not family.startswith("term:") else "subject",
        "components": [], "verifies": [] if layer == "V" else None,
        "scope_selector": ({"families": ["term:share_link"], "layers": [], "terms": [], "categories": []}
                           if node_id == "N-000004" else
                           {"families": [], "layers": ["L3"], "terms": ["term:endpoint"],
                            "categories": ["term:endpoint"]}
                           if node_id == "N-000014" else None),
        "decision": None, "annotations": [], "keywords": [], "ambiguity": [], "conflict_ids": [],
        "related_conflict_nodes": [], "stale_reasons": [], "last_checked_run": "R-000001", "flags": [],
        "status": "validated", "judgments": [],
    }
    record["status"] = derive_status(record)
    return record


def graph() -> Graph:
    g = Graph(nodes={n[0]: node(*n) for n in NODES},
              terms={t["id"]: t for t in [term("term:share_link", "entity", ["shared link"]),
                                          term("term:file", "entity"), term("term:owner", "actor"),
                                          term("term:endpoint", "category")]},
              links=[{"from": "N-000010", "type": "refines", "to": "N-000003", "provenance": "code",
                      "judgment": None, "rationale": None, "quotes": []}],
              conflicts={"CF-000001": {"id": "CF-000001", "kind": "contradiction",
                                       "members": ["N-000003", "N-000005"], "rationale": "r", "quotes": {},
                                       "state": "open", "resolved_reason": None, "detected_run": "R-000001",
                                       "resolved_run": None, "judgment": "J-000001"}},
              reviews={}, counters={"node": 14, "conflict": 1, "judgment": 1, "review": 0})
    for member in ("N-000003", "N-000005"):
        g.nodes[member] = {**g.nodes[member], "conflict_ids": ["CF-000001"],
                           "related_conflict_nodes": [m for m in ("N-000003", "N-000005") if m != member]}
        g.nodes[member]["status"] = derive_status(g.nodes[member])
    return g
