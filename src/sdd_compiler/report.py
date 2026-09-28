"""F6 §4.8 — the end-of-run report: what the run did, and every conflict it found.

This is what a person actually reads after `sddc compile`, so it states plainly what happened
rather than what succeeded:

- what was **not** done — blocks that failed, blocks that formed no node (F3 D33), annotations
  that could not be placed (F3 D35), pairs left unjudged by the budget;
- every open conflict, grouped so that interlinked records are read together (F4 AC-4.16, rel01
  D13) and sorted with contradictions first (F6 D9), because 40 duplications must never bury
  3 contradictions;
- the exit code, spelled out: `0` clean, `3` open conflicts, `5` the budget stopped the run.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

KIND_ORDER = ("contradiction", "duplication", "subsumption", "ambiguity")


def conflict_groups(graph: Any) -> list[list[dict[str, Any]]]:
    """Open records, grouped by shared members (F4 AC-4.16) and sorted by kind (F6 D9).

    Groups are ordered by their worst kind, then by their first record's id, so the reader meets
    contradictions first whichever group they are in.
    """
    records = sorted((r for r in graph.conflicts.values() if r["state"] == "open"),
                     key=lambda r: r["id"])
    parent: dict[str, str] = {r["id"]: r["id"] for r in records}

    def root(record_id: str) -> str:
        while parent[record_id] != record_id:
            parent[record_id] = parent[parent[record_id]]
            record_id = parent[record_id]
        return record_id

    holder: dict[str, str] = {}
    for record in records:
        for member in record["members"]:
            if member in holder:
                parent[root(record["id"])] = root(holder[member])
            else:
                holder[member] = record["id"]

    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(root(record["id"]), []).append(record)
    groups = [sorted(group, key=lambda r: (_rank(r), r["id"])) for group in grouped.values()]
    return sorted(groups, key=lambda group: (_rank(group[0]), group[0]["id"]))


def _rank(record: Mapping[str, Any]) -> int:
    return KIND_ORDER.index(record["kind"]) if record["kind"] in KIND_ORDER else len(KIND_ORDER)


def render_report(summary: Mapping[str, Any], graph: Any, exit_code: int) -> str:
    """The text `sddc compile` prints. `--json` prints the same summary as one object."""
    counts, conflicts = summary["counts"], summary["conflicts"]
    lines = [
        f"{summary['run']}: compiled {len(summary['files'])} file(s) · "
        f"{counts['new']} new · {counts['changed']} changed · {counts['removed']} removed",
        f"atomized {summary['completed']} of {summary['pending']} pending block(s) · "
        f"{summary['failed']} failed · {summary['empty_blocks']} formed no node · "
        f"{summary['nodes_formed']} node(s) formed, {summary['nodes_deleted']} deleted",
        f"checked {conflicts.get('candidates', 0)} pair(s) "
        f"({conflicts.get('pairs_judged', 0)} judged, {conflicts.get('pairs_replayed', 0)} replayed) · "
        f"{summary['model_calls']} model call(s) · ${summary['cost_usd']:.4f} · "
        f"{summary['replayed']} answer(s) replayed from the lock",
    ]
    if summary.get("annotations_dropped"):
        lines.append(f"{len(summary['annotations_dropped'])} annotation(s) dropped: "
                     "a quote that is not in its block (F3 D35)")
    definitions = summary.get("definitions") or {}
    if definitions.get("attached") or definitions.get("unattached"):
        lines.append(f"{len(definitions['attached'])} definition(s) attached to terms · "
                     f"{len(definitions['unattached'])} not attached (F3 D38)")
        lines += [f"  {item['file']}:{item['lines'][0]}  {item['reason']}  {item['text'][:80]}"
                  for item in definitions["unattached"]]
    if conflicts.get("incomplete"):
        why = {"call_cap": "the call cap", "backend": "the model backend"}.get(
            conflicts.get("stopped"), "the run")
        lines.append(f"⚠ CHECKING INCOMPLETE: {why} stopped the check phase and "
                     f"{conflicts.get('unjudged', 0)} pair(s) were not judged; "
                     f"what was judged is written"
                     + (f" — {conflicts['stop_reason']}" if conflicts.get("stop_reason") else ""))
    if conflicts.get("unjudged_failed"):
        lines.append(f"⚠ {conflicts['unjudged_failed']} pair(s) could not be judged: "
                     f"the answer failed its checks twice")

    groups = conflict_groups(graph)
    if not groups:
        lines.append("CONFLICTS: none open — the graph has no conflicts this run")
    else:
        kinds = {}
        for group in groups:
            for record in group:
                kinds[record["kind"]] = kinds.get(record["kind"], 0) + 1
        summary_line = ", ".join(f"{n} {kind}" for kind, n in
                                 sorted(kinds.items(), key=lambda kv: _rank({"kind": kv[0]})))
        lines.append(f"CONFLICTS: {sum(kinds.values())} open ({summary_line}) "
                     f"in {len(groups)} group(s)")
        for group in groups:
            lines += _render_group(group, graph)
    if conflicts.get("closed", {}).get("rejudged") or conflicts.get("closed", {}).get("member_deleted"):
        closed = conflicts["closed"]
        lines.append(f"closed this run: {closed.get('rejudged', 0)} re-judged, "
                     f"{closed.get('member_deleted', 0)} by a deleted member")
    if summary["attention_items"]:
        lines.append(f"ATTENTION: {summary['attention_items']} item(s) — see .sdd/review.jsonl")
    lines.append(f"exit {int(exit_code)}")
    return "\n".join(lines) + "\n"


def _render_group(group: Sequence[Mapping[str, Any]], graph: Any) -> list[str]:
    lines = []
    for record in group:
        members = " ↔ ".join(f"{m} {_where(graph, m)}" for m in record["members"])
        lines.append(f"  {record['id']} {record['kind']}  {members}")
        quotes = " ↔ ".join(f'"{record["quotes"][m]}"' for m in record["members"]
                            if m in record["quotes"])
        if quotes:
            lines.append(f"    {quotes}")
        lines.append(f"    rationale: {record['rationale']}")
    return lines


def _where(graph: Any, node_id: str) -> str:
    node = graph.nodes.get(node_id)
    if node is None:
        return "(deleted)"
    return f"{node['source']['file']}:{node['source']['lines'][0]}"
