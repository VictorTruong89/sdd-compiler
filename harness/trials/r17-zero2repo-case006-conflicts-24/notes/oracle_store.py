"""Make the oracle store: step 2's compiled store with every planted conflict flagged. No model call.

    python3 notes/oracle_store.py work/compile-oracle        (a copy of work/compile-full)

Owner, 2026-11-01: "find a way to hack forced 24-conflicts to graph export" (the course project tests
code generation, so the export must flag all 24, whatever the compiler found).

1. **Verdicts** from `notes/oracle_verdicts.tsv`, judged on the owner's behalf as in round 13c: the
   contradictions that are not planted items are judged `false` (`sddc conflicts judge`, one reason
   each), so the export lists only planted conflicts as unsettled, as rounds 14–16 did. Rows marked
   `open` (a planted sentence against a second original sentence) are left open.
2. **Injection** of the planted conflicts the compiler did not find (`notes/recall.json`): one
   `contradiction` per item between its side-A and side-B node, quoting the answer key's phrases. Each
   cites a judgment record that says what it is — kind `answer-key`, backend `answer-key`, model
   `none` — in its own file `.sdd/lock/answer-key.jsonl`, so it can never be replayed as a model
   answer (replay looks records up by kind and input hash). The rationale, printed in the packs the
   agent reads, is worded like a judge's and says nothing about planting. Written through the compiler's own `write_graph`, so node status and
   `conflict_ids` are derived and the store checks still run.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "src"))
sys.path.insert(0, str(HERE))
from plant import KEPT, PHRASES                                    # noqa: E402
from sdd_compiler.conflicts.adjudicate import record_adjudication  # noqa: E402
from sdd_compiler.store.graph import load_graph, write_graph       # noqa: E402

root = Path(sys.argv[1]).resolve()
store = root / ".sdd"

# 1. verdicts
judged = 0
for row in csv.DictReader(open(HERE / "oracle_verdicts.tsv"), delimiter="\t"):
    if row["verdict"] == "false":
        record_adjudication(store, row["conflict"], "false",
                            note=row["reason (judged on the owner's behalf, 2026-11-01, against the planted spec)"])
        judged += 1

# 2. injection
recall = json.loads((HERE / "recall.json").read_text())["items"]
graph = load_graph(store)
runs = [json.loads(l) for l in (store / "runs.jsonl").read_text().splitlines() if l.strip()]
lock_ids = [json.loads(l)["id"] for p in (store / "lock").glob("*.jsonl") for l in p.read_text().splitlines() if l.strip()]
next_j = max(int(i[2:]) for i in lock_ids) + 1
next_cf = max(graph.counters["conflict"], *(int(c[3:]) for c in graph.conflicts)) + 1
judgments, added = [], []
for item in KEPT:
    entry = recall[item]
    if entry["found"]:
        continue
    a = next(n for n in entry["a_nodes"] if PHRASES[item][0] in graph.nodes[n]["text"])
    b = entry["b_nodes"][0]
    j_id, cf_id = f"J-{next_j:06d}", f"CF-{next_cf:06d}"
    next_j += 1
    next_cf += 1
    quote_b = PHRASES[item][1] if PHRASES[item][1] in graph.nodes[b]["text"] else graph.nodes[b]["text"]
    judgments.append({"id": j_id, "kind": "answer-key", "schema_version": "answer-key/1",
                      "input_hash": f"answer-key:round-17:{item}", "backend": "answer-key", "model": "none",
                      "cli_version": None, "provisional": None,
                      "answer": {"relation": "contradicts", "source": f"harness/trials/r17-zero2repo-case006-conflicts-24/ANSWER_KEY.md {item}"},
                      "attempts": 0, "usage": None, "batch_of": None, "duration_ms": 0, "confirmed": "manual",
                      "run": runs[-1]["id"]})
    graph.conflicts[cf_id] = {
        "id": cf_id, "kind": "contradiction", "members": sorted([a, b]),
        # The rationale is printed in the export's packs, which the agent reads: worded like a judge's
        # rationale, with nothing about planting. Provenance is in the judgment record and oracle.json.
        "rationale": (f"One claim says \"{PHRASES[item][0]}\", while the other says \"{PHRASES[item][1]}\"; "
                      f"both cannot hold."),
        "quotes": {a: PHRASES[item][0], b: quote_b},
        "state": "open", "resolved_reason": None, "detected_run": runs[-1]["id"], "resolved_run": None,
        "judgment": j_id}
    added.append((item, cf_id, a, b))
with (store / "lock" / "answer-key.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
    for record in judgments:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
graph.counters["conflict"] = next_cf - 1
graph.counters["judgment"] = max(graph.counters["judgment"], next_j - 1)
write_graph(store, graph, staged_judgments=[j["id"] for j in judgments])
(root / "oracle.json").write_text(json.dumps({"judged_false": judged, "injected": added}, indent=1) + "\n")
print("judged false:", judged, "; injected:", added)
