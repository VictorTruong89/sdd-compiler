"""F6 §4.1, §4.5 … §4.7 — the check phase: judge every candidate pair, and keep the records true.

The phase runs after atomization, over the finished graph, so every node is visible to every
pair (F6 §4.1). Three rules shape it:

- **It never stops at a conflict** (rel01 D26). A conflict is recorded and checking continues to
  the last pair; a pair whose answer fails its checks twice is counted and skipped, not raised.
- **The budget is shared with atomization** (F6 D5). When it runs out, what was judged is kept,
  the rest stays unjudged, and the result says `incomplete` with how many pairs were left — the
  caller turns that into exit `5`.
- **An edit never closes a conflict** (F6 D4). A re-judgement closes it, or a deleted member does
  (F2 §4.9). An open record whose pair still contradicts keeps its id and takes the new quotes.

Nothing is written here: the result holds the links, conflict records and ambiguity the caller
writes in one transaction (F4 §4.2), which then derives `conflict_ids`, status and the registry.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..atomize.guards import GuardFailure
from ..errors import ExitCode, SddcError
from ..llm import Backend
from ..retrieval.select import propose
from .judge import INSTRUCTIONS, SCHEMA_VERSION, Verdict, judge
from .records import outcome_for


@dataclass
class CheckResult:
    links: list[dict[str, Any]] = field(default_factory=list)
    conflicts: dict[str, dict[str, Any]] = field(default_factory=dict)   # new and updated records
    ambiguity: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    counts: dict[str, Any] = field(default_factory=dict)
    incomplete: bool = False
    unjudged: int = 0
    counter: int = 0                                                     # highest conflict id used
    checked: list[str] = field(default_factory=list)                     # nodes this run looked at


def check(graph: Any, *, backend: Backend, retrieval: Any, settings: Any, run_id: str,
          lock: Any) -> CheckResult:
    nodes = dict(graph.nodes)
    if not settings.judge_ambiguous:                       # CT-6.3: leave vague claims alone
        nodes = {i: n for i, n in nodes.items() if n["status"] != "ambiguous"}

    proposal = propose(nodes, terms=graph.terms, settings=retrieval)
    counts: dict[str, Any] = {
        "candidates": len(proposal.pairs), "pairs_judged": 0, "pairs_replayed": 0,
        "by_relation": dict.fromkeys(
            ("none", "refines", "depends_on", "duplicates", "subsumes", "contradicts"), 0),
        "opened": 0, "closed": {"rejudged": 0, "member_deleted": 0}, "calls": 0,
        "provisional": 0, "unjudged_failed": 0, "incomplete": False,
        "retrieval": dict(proposal.counts),
    }
    result = CheckResult(counts=counts, counter=graph.counters.get("conflict", 0),
                         checked=list(proposal.checked))
    open_records = {frozenset(record["members"]): record
                    for record in graph.conflicts.values() if record["state"] == "open"}
    for position, candidate in enumerate(proposal.pairs):
        a, b = nodes[candidate["a"]], nodes[candidate["b"]]
        input_hash = lock.key("q-pair", SCHEMA_VERSION, INSTRUCTIONS,
                              {"pair_key": candidate["pair_key"]})
        hit = lock.lookup("q-pair", input_hash)
        if hit is not None:
            verdict = _verdict_from(hit["answer"], a, b)
            judgment = hit["id"]
            counts["pairs_replayed"] += 1
            lock.replayed += 1
        else:
            try:
                verdict = judge(a, b, backend, settings=settings)
            except SddcError as error:
                if error.exit_code not in (ExitCode.CALL_CAP, ExitCode.BACKEND):
                    raise
                result.incomplete = True
                counts["incomplete"] = True
                result.unjudged = len(proposal.pairs) - position
                break
            except GuardFailure:
                # Checked twice and still wrong: no verdict, and the phase carries on (§4.2).
                counts["unjudged_failed"] += 1
                counts["calls"] += 2
                continue
            counts["pairs_judged"] += 1
            counts["calls"] += verdict.attempts
            judgment = lock.record("q-pair", SCHEMA_VERSION, input_hash, _answer_of(verdict),
                                   verdict.answer, attempts=verdict.attempts, batch_of=None,
                                   provisional=verdict.provisional)
        counts["by_relation"][verdict.relation] += 1
        counts["provisional"] += 1 if verdict.provisional else 0
        _apply(result, verdict, a, b, settings=settings, run_id=run_id, judgment=judgment,
               open_records=open_records, counts=counts)

    return result


def _apply(result: CheckResult, verdict: Verdict, a, b, *, settings, run_id, judgment,
           open_records, counts) -> None:
    outcome = outcome_for(verdict, a, b, settings=settings, run_id=run_id,
                          conflict_id="CF-%06d" % (result.counter + 1), judgment=judgment)
    result.links += outcome.links
    for node_id, entries in outcome.ambiguity.items():
        result.ambiguity.setdefault(node_id, []).extend(entries)

    members = frozenset((a["id"], b["id"]))
    existing = open_records.pop(members, None)
    if outcome.conflict is None:
        # F6 §4.6 rule 1, AC-6.16: judged again, and no longer a conflict.
        if existing is not None:
            result.conflicts[existing["id"]] = {**existing, "state": "resolved",
                                                "resolved_reason": "fixed", "resolved_run": run_id,
                                                "judgment": judgment}
            counts["closed"]["rejudged"] += 1
        return
    if existing is not None:                       # F6 D4: the same pair keeps its record and id
        result.conflicts[existing["id"]] = {**existing, "kind": outcome.conflict["kind"],
                                            "rationale": outcome.conflict["rationale"],
                                            "quotes": outcome.conflict["quotes"],
                                            "judgment": judgment}
        return
    result.counter += 1
    result.conflicts[outcome.conflict["id"]] = outcome.conflict
    counts["opened"] += 1


def _answer_of(verdict: Verdict) -> dict[str, Any]:
    return {"relation": verdict.relation, "direction": verdict.direction,
            "rationale": verdict.rationale, "quotes": dict(verdict.quotes),
            "confidence": verdict.confidence}


def _verdict_from(payload: Mapping[str, Any], a, b) -> Verdict:
    return Verdict(relation=payload["relation"], direction=payload["direction"],
                   rationale=payload["rationale"], quotes=dict(payload["quotes"]),
                   confidence=payload["confidence"],
                   provisional="ambiguous" in (a["status"], b["status"]), answer=None)
