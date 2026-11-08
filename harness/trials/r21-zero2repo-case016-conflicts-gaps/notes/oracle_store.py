"""Round 21 (copied from round 19; changes: verdicts from notes/verdicts.tsv, the same file the compiler
export uses; conflicts only (KEPT_C); RATIONALE written for this round's misses after the compile).

Make the oracle store: step 2's compiled store with every planted conflict flagged. No model call.

    python3 notes/oracle_store.py work/compile-oracle        (a copy of work/compile-full)

Round 19 (copied from ../r17-zero2repo-case006-conflicts-24/notes/oracle_store.py; method unchanged).
Owner, 2026-11-02: "if using sdd-compiler/ cannot generate and export that highlight all conflicts,
claude opus to appended all missing conflicts to the spec-graph export."

1. **Verdicts** from `notes/verdicts.tsv`, judged on the owner's behalf as in round 13c: the
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
from plant import FIND, KEPT_C as KEPT, PHRASES                                   # noqa: E402
from sdd_compiler.conflicts.adjudicate import record_adjudication  # noqa: E402
from sdd_compiler.store.graph import load_graph, write_graph       # noqa: E402

root = Path(sys.argv[1]).resolve()
store = root / ".sdd"

# One rationale per injected item, in a judge's voice (printed in the export's packs).
RATIONALE = {   # one per item the compiler missed (notes/recall.json), written 2026-11-06
    "C01": "Hedge stacking (54) is listed among the writing-advice families, reported with weight zero, yet "
           "another statement says each sentence with stacked hedges adds to the score. A family cannot both "
           "carry no weight and raise the score.",
    "C13": "One statement fires the AI tracking parameter (65) only when the whole host name is one of the "
           "listed AI domains; another fires it for any `utm_source` parameter left in a link. A `utm_source` "
           "with another value cannot both fire and stay quiet.",
    "C17": "An apply_patch payload is scored at most 16 distinct paths in one statement and at most ten paths "
           "in another. A payload naming twelve paths cannot be scored in full and cut at ten at once.",
    "C19": "A ledger is gone once its last modification is more than seven days old in one statement, and is "
           "deleted once untouched for more than one day in another. A three-day-old ledger cannot be both "
           "kept and deleted.",
    "C20": "With a valid level stored, one statement uses the stored level and lets the environment supply a "
           "level only when nothing valid is stored; another says the environment level, when set, takes "
           "precedence over the stored level.",
    "C22": "The session-prose score is printed when the trimmed slice is longer than 200 characters in one "
           "statement and longer than 500 characters in another. A 300-character slice cannot both print "
           "and not print the score.",
    "C25": "The tailing-negation form of catalogue 17 is score-moving in one statement, while another makes "
           "both forms of catalogue 17 writing advice with no weight.",
}

# 1. verdicts
judged = 0
rows = list(csv.DictReader(open(HERE / "verdicts.tsv"), delimiter="\t"))
REASON = [k for k in rows[0] if k.startswith("reason")][0]
for row in rows:
    if row["verdict"] == "false":
        record_adjudication(store, row["conflict"], "false", note=row[REASON])
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
    a_phrase = FIND.get(item, (None, None))[0] or PHRASES[item][0]
    if not entry["a_nodes"]:   # round 21: side A in no node (C12): nothing to inject against; unflagged in both exports
        added.append((item, None, None, entry["b_nodes"][0] if entry["b_nodes"] else None))
        continue
    a = next(n for n in entry["a_nodes"] if a_phrase in graph.nodes[n]["text"])
    b = entry["b_nodes"][0]
    j_id, cf_id = f"J-{next_j:06d}", f"CF-{next_cf:06d}"
    next_j += 1
    next_cf += 1
    b_phrase = FIND.get(item, (None, None))[1] or PHRASES[item][1]
    quote_b = b_phrase if b_phrase in graph.nodes[b]["text"] else graph.nodes[b]["text"]
    judgments.append({"id": j_id, "kind": "answer-key", "schema_version": "answer-key/1",
                      "input_hash": f"answer-key:{item}", "backend": "answer-key", "model": "none",
                      "cli_version": None, "provisional": None,
                      "answer": {"relation": "contradicts", "source": f"harness/trials/r21-zero2repo-case016-conflicts-gaps/ANSWER_KEY.md {item}"},
                      "attempts": 0, "usage": None, "batch_of": None, "duration_ms": 0, "confirmed": "manual",
                      "run": runs[-1]["id"]})
    graph.conflicts[cf_id] = {
        "id": cf_id, "kind": "contradiction", "members": sorted([a, b]),
        # The rationale is printed in the export's packs, which the agent reads: worded like a judge's
        # rationale, with nothing about planting. Provenance is in the judgment record and oracle.json.
        "rationale": RATIONALE[item],
        "quotes": {a: a_phrase, b: quote_b},
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
