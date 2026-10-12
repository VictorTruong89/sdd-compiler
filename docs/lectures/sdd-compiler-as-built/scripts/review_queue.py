"""Build a sorted, working CSV of every open conflict, for a person adjudicating by hand.

Usage:  PYTHONPATH=<repo>/src python review_queue.py <.sdd dir> <out.csv>

Joins each conflict record with the Q-PAIR judgment that produced it (confidence, provisional —
neither is in `sddc conflicts` or `views/conflicts.md`) and with each member node's status and
source location. Adds two triage aids no view computes:

- `cluster` / `cluster_size`: the same connected-component grouping `sddc conflicts` shows
  (`report.conflict_groups`), so records worth reading together stay together.
- `degree_a` / `degree_b`: how many other OPEN records each member is in. A high degree marks a
  "hub" node — reading its source once, or fixing it, can settle several records at once (a
  pattern found reviewing this repository's own R18 store, e.g. one rationale sentence turned
  into a constraint node that then argued with six unrelated claims).

Sort: cluster size (desc, most leverage first) → kind (contradiction, then subsumption, then
duplication — F6 D9) → confidence (low first: usually the fastest to dismiss) → max degree (desc)
→ id. This is a suggested order, not a rule — every column needed to re-sort by another strategy
in a spreadsheet is in the file. `verdict` and `note` are left blank for you to fill in; `note`'s
text is what you would pass to `sddc conflicts judge ... --note`.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from sdd_compiler.report import conflict_groups
from sdd_compiler.store.graph import load_graph

KIND_RANK = {"contradiction": 0, "subsumption": 1, "duplication": 2}
COLUMNS = ["cluster", "cluster_size", "cf_id", "kind", "confidence", "provisional",
           "degree_a", "member_a", "status_a", "loc_a", "degree_b", "member_b", "status_b", "loc_b",
           "rationale", "verdict", "note"]


def _loc(node: dict) -> str:
    s = node["source"]
    return f"{s['file']}:{s['lines'][0]}"


def build_rows(store: Path) -> list[dict]:
    g = load_graph(store)
    lock = {}
    for path in (store / "lock").glob("*.jsonl"):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            lock[record["id"]] = record

    degree = Counter()
    for record in g.conflicts.values():
        if record["state"] == "open":
            for member in record["members"]:
                degree[member] += 1

    rows = []
    for cluster_index, group in enumerate(conflict_groups(g), start=1):
        for record in group:
            a_id, b_id = record["members"]
            a, b = g.nodes[a_id], g.nodes[b_id]
            answer = lock[record["judgment"]]
            rows.append({
                "cluster": f"Group {cluster_index}", "cluster_size": len(group),
                "cf_id": record["id"], "kind": record["kind"],
                "confidence": answer["answer"]["confidence"], "provisional": answer["provisional"],
                "degree_a": degree[a_id], "member_a": a_id, "status_a": a["status"], "loc_a": _loc(a),
                "degree_b": degree[b_id], "member_b": b_id, "status_b": b["status"], "loc_b": _loc(b),
                "rationale": record["rationale"], "verdict": "", "note": "",
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("store", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    if not (args.store / "graph.meta.json").exists():
        parser.error(f"{args.store} is not a compiled .sdd store (no graph.meta.json)")

    rows = build_rows(args.store)
    rows.sort(key=lambda r: (
        -r["cluster_size"], KIND_RANK[r["kind"]], r["confidence"] != "low",
        -max(r["degree_a"], r["degree_b"]), r["cf_id"],
    ))
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    low = sum(1 for r in rows if r["confidence"] == "low")
    prov = sum(1 for r in rows if r["provisional"])
    print(f"{args.out}: {len(rows)} open conflicts, {low} low-confidence, {prov} provisional")


if __name__ == "__main__":
    main()
