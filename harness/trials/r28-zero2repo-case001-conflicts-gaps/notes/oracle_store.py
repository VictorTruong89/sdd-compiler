"""Round 28 case001 (copied from round 21's notes/oracle_store.py, unchanged in method; RATIONALE written for
this case's misses after its compile).

Round 21 (copied from round 19; changes: verdicts from notes/verdicts.tsv, the same file the compiler
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
RATIONALE = {   # one per item the compiler missed (notes/recall.json), written 2026-11-11 after the compile
    "C14": 'Raw tabs are allowed inside strings in one statement (control characters other than tab are refused); another requires a tab in a one-line string to be written as backslash-t. A one-line string holding a raw tab cannot be both accepted and refused.',
    "C17": 'Hex digits of `\\x`, `\\u` and `\\U` escapes are case-insensitive in one statement; another refuses escape digits written as uppercase letters. `\\u00E9` cannot be both accepted and refused.',
    "C29": 'A converter result that is an instance of a subclass of dict or list is refused in one statement; another refuses only a result whose type is exactly dict or exactly list. A dict subclass result cannot be both refused and accepted.',
    "C35": 'A quoted key may be empty in one statement; another says keys are never empty. `"" = 1` cannot be both accepted and refused.',
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
    if not entry["a_nodes"] or not entry["b_nodes"]:   # a side in no node (round 21 C12; round 28 case011 C24): nothing to inject; unflagged in both exports
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
                      "answer": {"relation": "contradicts", "source": f"harness/trials/r28-zero2repo-case001-conflicts-gaps/ANSWER_KEY.md {item}"},
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
