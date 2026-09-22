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

from ..errors import ExitCode, SddcError
from ..llm import Backend
from ..retrieval.select import propose
from .judge import PairItem, Verdict, judge_batch
from .records import outcome_for

#: Pairs per Q-PAIR call (R21). Eight is what Q-DESC settled on (rel01 S21): enough to amortise the
#: harness prompt, small enough that a batch stays inside the call timeout.
PAIR_BATCH = 8


class _Counting:
    """Counts the calls the phase makes, for CT-6.2."""

    def __init__(self, backend, counts):
        self._backend, self._counts = backend, counts
        self.name = getattr(backend, "name", "backend")

    def ask(self, question):
        self._counts["calls"] += 1
        return self._backend.ask(question)


@dataclass
class CheckResult:
    links: list[dict[str, Any]] = field(default_factory=list)
    conflicts: dict[str, dict[str, Any]] = field(default_factory=dict)   # new and updated records
    ambiguity: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    counts: dict[str, Any] = field(default_factory=dict)
    incomplete: bool = False
    stopped: str | None = None          # "call_cap" | "backend" — which limit ended the phase
    stop_reason: str | None = None
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
        "provisional": 0, "unjudged_failed": 0, "suppressed": 0, "incomplete": False,
        "retrieval": dict(proposal.counts),
    }
    result = CheckResult(counts=counts, counter=graph.counters.get("conflict", 0),
                         checked=list(proposal.checked))
    open_records = {frozenset(record["members"]): record
                    for record in graph.conflicts.values() if record["state"] == "open"}
    items = [PairItem(a=nodes[c["a"]], b=nodes[c["b"]], key=c["pair_key"],
                      related_terms=_term_relations(nodes[c["a"]], nodes[c["b"]], graph.terms))
             for c in proposal.pairs]
    counted = _Counting(backend, counts)

    for start in range(0, len(items), PAIR_BATCH):
        chunk = items[start:start + PAIR_BATCH]
        replayed_before = lock.replayed
        try:
            outcome = judge_batch(chunk, counted, settings=settings, lock=lock)
        except SddcError as error:
            if error.exit_code not in (ExitCode.CALL_CAP, ExitCode.BACKEND):
                raise
            # What earlier batches judged is kept; this one and the rest stay unjudged (F6 §4.7).
            result.incomplete = True
            counts["incomplete"] = True
            result.stopped = "call_cap" if error.exit_code == ExitCode.CALL_CAP else "backend"
            result.stop_reason = str(error)
            counts["stopped"] = result.stopped
            result.unjudged = len(items) - start
            break

        replayed = lock.replayed - replayed_before
        counts["pairs_replayed"] += replayed
        counts["pairs_judged"] += len(outcome.verdicts) - replayed
        counts["unjudged_failed"] += len(outcome.failures)
        for item in chunk:
            verdict = outcome.verdicts.get(item.pair_id)
            if verdict is None:
                continue                  # checked twice and still wrong (§4.2); the phase goes on
            counts["by_relation"][verdict.relation] += 1
            if verdict.provisional:
                counts["provisional"] += 1
                lock.mark_provisional(outcome.judgments.get(item.pair_id, ""))
            _apply(result, verdict, item.a, item.b, settings=settings, run_id=run_id,
                   judgment=outcome.judgments.get(item.pair_id, ""),
                   open_records=open_records, counts=counts)

    return result


def _term_relations(a, b, registry: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """What the graph already knows about the two namings (F6 D17, I-76): the same term on both
    sides, one that is a kind of the other, or two that are kinds of one thing."""
    def named(node):
        return {t["term"] for t in node["terms"] if t["term"] in registry}

    def parents(term):
        chain, seen = [], {term}
        current = (registry.get(term) or {}).get("broader")
        while current and current not in seen:
            chain.append(current)
            seen.add(current)
            current = (registry.get(current) or {}).get("broader")
        return chain

    mine, theirs = named(a), named(b)
    lines = [f"{term} is used by both claims" for term in sorted(mine & theirs)]
    for x in sorted(mine - theirs):
        for y in sorted(theirs - mine):
            if y in parents(x):
                lines.append(f"{x} is a kind of {y}")
            elif x in parents(y):
                lines.append(f"{y} is a kind of {x}")
            else:
                common = set(parents(x)) & set(parents(y))
                if common:
                    lines.append(f"{x} and {y} are both kinds of {sorted(common)[0]}")
    return lines


def _apply(result: CheckResult, verdict: Verdict, a, b, *, settings, run_id, judgment,
           open_records, counts) -> None:
    outcome = outcome_for(verdict, a, b, settings=settings, run_id=run_id,
                          conflict_id="CF-%06d" % (result.counter + 1), judgment=judgment)
    if outcome.suppressed:
        counts["suppressed"] += 1
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
