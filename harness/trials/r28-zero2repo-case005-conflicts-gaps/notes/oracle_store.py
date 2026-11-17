"""Round 28 case005 (copied from round 21's notes/oracle_store.py, unchanged in method; RATIONALE written for
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
    "C01": 'One statement accepts every Content-Length value of up to 18 digits; another refuses a value longer than 16 digits. A 17-digit value cannot be both accepted and refused.',
    "C02": 'The chunk-size line is limited to a maximum of 16 to 32 hexadecimal digits in one statement, while another accepts size lines of up to 64 digits. A 40-digit size line cannot be both accepted and refused.',
    "C04": "One statement accepts obsolete line folding and joins each continuation line to the previous header's value; another refuses any header line that begins with a space or tab. A folded header cannot be both joined and refused.",
    "C09": 'The chunk-size line may be followed by spaces or tabs before the line ending in one statement; another refuses whitespace after the chunk size. A size line with a trailing space cannot be both accepted and refused.',
    "C11": 'One statement keeps the Content-Length header on the wire including when its value is 0; another sends a Content-Length: 0 response without that header. The same response cannot both carry and omit it.',
    "C12": 'The keep-alive switch is turned off only when `close` is a whole element of the comma-separated Connection value in one statement; another turns it off for any Connection value that contains `close`. A value such as `closed-later` cannot both keep and end the connection.',
    "C14": 'The Expect token `100-continue` is matched case-insensitively in one statement; another requires exactly the lowercase token. `Expect: 100-Continue` cannot both set and not set the waiting flag.',
    "C15": 'The waiting-for-100-continue flags turn off when the client sends a data event or end-of-message in one statement; another keeps the client waiting until the server answers, whatever body events it sends.',
    "C16": 'CONNECT is accepted by any final response in the 2xx range in one statement; another accepts it only with status 200 and treats other 2xx statuses as denials. A 201 answer cannot both accept and deny.',
    "C18": 'A second Transfer-Encoding header is refused with suggested status 501 even when both values are chunked in one statement; another collapses repeated `Transfer-Encoding: chunked` headers to one. Two chunked headers cannot be both refused and accepted.',
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
                      "answer": {"relation": "contradicts", "source": f"harness/trials/r28-zero2repo-case005-conflicts-gaps/ANSWER_KEY.md {item}"},
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
