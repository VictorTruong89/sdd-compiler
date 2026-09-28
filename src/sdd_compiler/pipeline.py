"""`sddc compile` — the one rel01 command (build plan B1; governed by F3 §4.8, §4.10).

1. **Ingest** (F1): spec files into blocks; its own transaction.
2. **Atomize** (F3): every pending block — derived, F1 D13 — through the model
   steps, into a draft. No store lock is held while the model works.
3. **Write** (F4), under the store lock, in **one** transaction: delete the nodes
   of removed and re-atomized blocks (F2 §4.9), add the draft, set each completed
   block's `atomized_hash`, then derive, validate, check and rename everything.

⚠ Until T12 aligns identities, a re-atomized block's nodes get new ids; the old
ones are deleted with the usual cascade. Ids are never reused.

The check phase (F5, F6) joins here in M4. Exit `5` when the call cap stopped the
run, `6` when the model backend failed mid-run (I-43): in both, what finished is
written, the rest stays pending.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .atomize.definitions import DefinitionOutcome, attach_definitions
from .atomize.lock import JudgmentLock
from .atomize.pipeline import GraphDraft, atomize_pending
from .errors import ExitCode
from .ingest.identity import BLOCK_KEY_ORDER, atomizable, is_live, pending_status
from .ingest.pipeline import BLOCKS_FILE, RUNS_FILE, SOURCES_FILE, IngestResult, ingest, lock_wait_seconds
from .llm import Backend, CallBudget, get_backend
from .profile import STORE_DIR, load_profile
from .conflicts.pipeline import check
from .retrieval.select import needs_checking
from .model.status import derive_status
from .store.graph import delete_node, load_graph, write_graph
from .store.jsonl import read_jsonl
from .store.lock import StoreLock
from .store.transaction import Transaction


@dataclass
class CompileResult:
    ingest: IngestResult
    pending: int = 0
    draft: GraphDraft | None = None
    deleted: list[str] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=lambda: {"calls": 0, "cost_usd": 0.0})
    replayed: int = 0
    check: Any | None = None                       # the F6 check phase's result (T17)
    open_conflicts: int = 0
    definitions: DefinitionOutcome = field(default_factory=DefinitionOutcome)
    exit_code: ExitCode = ExitCode.OK

    def summary(self) -> dict[str, Any]:
        draft = self.draft or GraphDraft()
        return {
            "run": self.ingest.run_id, "files": self.ingest.files, "counts": self.ingest.counts,
            "pending": self.pending, "completed": len(draft.completed), "failed": len(draft.failed),
            "nodes_formed": len(draft.nodes), "nodes_deleted": len(self.deleted),
            "empty_blocks": len(draft.empty), "empty": [draft.empty[b] for b in sorted(draft.empty)],
            "annotations_dropped": draft.annotations_dropped,
            "definitions": {"attached": self.definitions.attached,
                            "unattached": [*draft.definitions_dropped, *self.definitions.unattached]},
            "attention_items": len(draft.reviews), "stopped": draft.stopped,
            "model_calls": self.usage["calls"], "cost_usd": round(self.usage["cost_usd"], 4),
            "replayed": self.replayed, "alignments": draft.alignments,
            "stop_reason": draft.stop_reason,
            "conflicts": {**(self.check.counts if self.check else {}),
                          "unjudged": self.check.unjudged if self.check else 0,
                          "stopped": self.check.stopped if self.check else None,
                          "stop_reason": self.check.stop_reason if self.check else None,
                          "open": self.open_conflicts},
        }


def compile_graph(root: Path, paths: list[str] | None = None, backend: Backend | None = None,
                  replay: bool = True, block_batch: int | None = None) -> CompileResult:
    root = Path(root).resolve()
    result = CompileResult(ingest=ingest(root, paths=paths, command="compile"))
    store = root / STORE_DIR
    profile = load_profile(root)
    blocks = read_jsonl(store / BLOCKS_FILE)
    pending = [b for b in blocks if pending_status(b, profile.include_code_blocks, profile.skip_headings)]
    result.pending = len(pending)

    graph = load_graph(store)
    removed = {b["id"] for b in blocks if not is_live(b)}
    # F3 §4.6: live blocks the profile no longer lets the atomizer see (F1 D14, code blocks).
    skipped = {b["id"] for b in blocks
               if is_live(b) and not atomizable(b, profile.include_code_blocks, profile.skip_headings)}
    gone = removed | skipped
    redo = {b["id"] for b in pending}
    # Nothing to atomize is not nothing to do: the check phase still judges the nodes that need
    # it (F6 §4.1) — replayed from the lock at no cost, or picked up after an earlier stop.
    if (not pending
            and not any(n["source"]["block_id"] in gone for n in graph.nodes.values())
            and not any(b["id"] in skipped and b.get("atomized_hash") for b in blocks)
            and not any(t.get("defined_by") in gone for t in graph.terms.values())
            and not any(needs_checking(n) for n in graph.nodes.values())):
        return result

    run_id = result.ingest.run_id
    draft = GraphDraft()
    lock = JudgmentLock(store, start=graph.counters["judgment"], replay=replay, run_id=run_id)
    # One backend and one budget for the whole run: atomizing and judging share the cap (F6 D5).
    backend = _Meter(backend or get_backend(
        profile.atomizer, root, budget=CallBudget(profile.atomizer.max_calls_per_run)), result.usage)
    if pending:
        draft = atomize_pending(
            pending, backend, run_id=run_id, weak_words=profile.weak_words,
            layer_hints=profile.layers, registry=graph.terms,
            existing_nodes={i: n for i, n in graph.nodes.items()
                            if n["source"]["block_id"] not in gone | redo},
            counters={"N": graph.counters["node"], "RV": graph.counters["review"]},
            previous={block_id: [n for n in graph.nodes.values() if n["source"]["block_id"] == block_id]
                      for block_id in redo},
            lock=lock,
            **({"block_batch": block_batch} if block_batch else {}),
        )
    result.draft = draft
    result.replayed = lock.replayed

    with StoreLock(store, wait_seconds=lock_wait_seconds()):
        graph = load_graph(store)
        blocks = read_jsonl(store / BLOCKS_FILE)
        # Old nodes of re-atomized blocks that no new atom kept, and nodes of removed or skipped blocks.
        doomed = sorted(i for i, n in graph.nodes.items()
                        if n["source"]["block_id"] in gone | set(draft.completed)
                        and i not in draft.nodes)
        for node_id in doomed:
            delete_node(graph, node_id, run_id)
        result.deleted = doomed

        # A re-formed node's code links are regenerated by the draft; judged links stay,
        # and an edited node's judged neighbours must be re-checked (F3 §4.6).
        graph.links = [l for l in graph.links
                       if not (l["provenance"] == "code" and l["from"] in draft.nodes)]
        edited = {a["node"] for a in draft.alignments if a["kind"] == "edited"}
        for link in graph.links:
            if link["provenance"] != "judgment":
                continue
            for node_id, other in ((link["from"], link["to"]), (link["to"], link["from"])):
                if node_id in edited and other in graph.nodes:
                    reason = {"link": [link["from"], link["type"], link["to"]], "since_run": run_id}
                    graph.nodes[other] = {**graph.nodes[other],
                                          "stale_reasons": [*graph.nodes[other]["stale_reasons"], reason]}

        graph.nodes.update(draft.nodes)
        graph.terms.update(draft.terms)
        # F3 §4.5 step 9 (D38): what a changed, removed or skipped block defined is re-derived.
        result.definitions = attach_definitions(graph.terms, draft.definitions,
                                                invalidated=gone | set(draft.completed))
        graph.terms.update(result.definitions.changed)
        graph.links += draft.links
        _merge_reviews(graph, draft, removed, doomed, run_id)
        graph.counters["node"] = max(graph.counters["node"], draft.counters.get("N", 0))
        graph.counters["review"] = max(graph.counters["review"], draft.counters.get("RV", 0))
        graph.counters["judgment"] = max(graph.counters["judgment"], lock.counter)
        for block in blocks:
            if block["id"] in draft.completed:
                block["atomized_hash"] = draft.completed[block["id"]]
            elif block["id"] in skipped:
                block["atomized_hash"] = None      # so that naming the section again re-atomizes it

        # The check phase (F6 §4.1): after every node exists, before anything is written.
        if draft.stopped is None:
            result.check = check(graph, backend=backend, retrieval=profile.retrieval,
                                 settings=profile.conflicts, run_id=run_id, lock=lock)
            _apply_check(graph, result.check, run_id)
        # Again after the check phase: its Q-PAIR records are judgments too (I-83).
        graph.counters["judgment"] = max(graph.counters["judgment"], lock.counter)
        result.open_conflicts = sum(1 for c in graph.conflicts.values() if c["state"] == "open")
        if result.check is not None:            # closed by F2 §4.9's cascade, before the phase ran
            result.check.counts["closed"]["member_deleted"] = sum(
                1 for c in graph.conflicts.values()
                if c["resolved_reason"] == "member_deleted" and c["resolved_run"] == run_id)

        # Before every write, not only after a check phase: a store written before the I-89 fix
        # must heal even on a run the cap stops during atomization.
        graph.links = list({_link_key(l): l for l in graph.links}.values())
        sources = {s["path"]: s["file_hash"] for s in read_jsonl(store / SOURCES_FILE)}
        others = {"block": _highest(b["id"] for b in blocks),
                  "run": _highest(r["id"] for r in read_jsonl(store / RUNS_FILE))}
        with Transaction(store) as transaction:
            transaction.write_jsonl(BLOCKS_FILE, blocks, BLOCK_KEY_ORDER)
            lock.stage(transaction)
            write_graph(store, graph, transaction=transaction, sources=sources, other_counters=others,
                        staged_judgments=lock.records)

    stopped = draft.stopped or (result.check.stopped if result.check is not None else None)
    if stopped == "call_cap":
        result.exit_code = ExitCode.CALL_CAP
    elif stopped == "backend":
        result.exit_code = ExitCode.BACKEND          # a 429 is not a cap: I-72
    elif result.open_conflicts:
        result.exit_code = ExitCode.CONFLICTS          # F6 §4.8, AC-6.10
    return result


def _apply_check(graph: Any, result: Any, run_id: str) -> None:
    """Put what the check phase found on the graph; F4 derives the rest (`conflict_ids`, status,
    the registry). A node checked in this run records the run and loses the stale reasons that
    scheduled it (F6 §4.5)."""
    # F6 D20 (I-91): a pair that received a verdict keeps only that verdict's links — whatever it was
    # judged before, in either direction, goes. Then one link per `(from, type, to)` (F2 §4.8, I-89).
    rejudged = {frozenset(pair) for pair in result.judged_pairs}
    kept = [l for l in graph.links
            if not (l["provenance"] == "judgment" and frozenset((l["from"], l["to"])) in rejudged)]
    graph.links = list({_link_key(l): l for l in [*kept, *result.links]}.values())
    graph.conflicts.update(result.conflicts)
    graph.counters["conflict"] = max(graph.counters["conflict"], result.counter)
    for node_id in result.checked:
        node = graph.nodes.get(node_id)
        if node is None:
            continue
        node = {**node, "ambiguity": [*node["ambiguity"], *result.ambiguity.get(node_id, [])],
                "last_checked_run": run_id, "stale_reasons": []}
        graph.nodes[node_id] = {**node, "status": derive_status(node)}


def _link_key(link: Any) -> tuple[str, str, str]:
    return (link["from"], link["type"], link["to"])


class _Meter:
    """Counts what the model's work cost, for the run report (F3 §4.8)."""

    def __init__(self, backend: Backend, usage: dict[str, Any]) -> None:
        self._backend, self._usage = backend, usage
        self.name = backend.name

    def ask(self, question: Any) -> Any:
        answer = self._backend.ask(question)
        self._usage["calls"] += 1
        self._usage["cost_usd"] += answer.cost_usd or 0.0
        return answer


def _merge_reviews(graph: Any, draft: GraphDraft, removed: set[str], doomed: list[str],
                   run_id: str) -> None:
    """F3 §4.9 — an item whose cause is gone closes itself; a cause that persists keeps one item.

    - `atomize_failed` closes when its block completed or was removed; a block that
      fails again updates its open item instead of opening another;
    - an item about a node closes when the node was deleted.
    """
    gone = set(draft.completed) | removed | set(doomed)
    for item_id, item in list(graph.reviews.items()):
        if item["state"] == "open" and item["subject"] in gone:
            graph.reviews[item_id] = {**item, "state": "resolved", "closed_run": run_id}

    open_failed = {item["subject"]: item_id for item_id, item in graph.reviews.items()
                   if item["state"] == "open" and item["type"] == "atomize_failed"}
    for item in draft.reviews:
        if item["type"] == "atomize_failed" and item["subject"] in open_failed:
            existing = open_failed[item["subject"]]
            graph.reviews[existing] = {**graph.reviews[existing], "detail": item["detail"]}
            continue
        graph.reviews[item["id"]] = item


def _highest(ids: Any) -> int:
    return max((int(m.group(1)) for i in ids if (m := re.search(r"(\d+)$", i))), default=0)
