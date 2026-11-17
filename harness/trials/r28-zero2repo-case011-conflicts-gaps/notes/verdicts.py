"""Judge the compile's contradictions on the owner's behalf (round 28 case011, step 3). No model call.

Round 28 (copied from round 21's notes/verdicts.py; one change): there is no earlier case011 compile, so no
earlier verdicts are reused; every contradiction that is not a planted pair is read one by one against
the original case011 spec.

    python3 notes/verdicts.py list  work/compile-full      -> work/verdict_draft.tsv (one row per contradiction)
    python3 notes/verdicts.py apply work/compile-compiler  -> records notes/verdicts.tsv with record_adjudication

Round 21 (copied from ../r20-zero2repo-case010-gaps/notes/verdicts.py; two changes):
  - the earlier verdicts reused are round 13c's case016 ones (`../r13c-…/notes/verdicts-case016.tsv`,
    conflict ids of `../r13c-…/work/compile-case016`; all `false`), matched on the two node texts,
    never on ids;
  - a contradiction between a planted conflict's side-A and side-B nodes (`notes/recall.json`) is
    marked `planted` in the draft and is never judged: it stays open in both exports.
Rows with no match are read one by one against the **original** case016 spec and written into
`notes/verdicts.tsv` by hand: `false` (two statements that do not contradict), or `open` (a real
contradiction, for example a planted sentence against a second original sentence). `apply` records
every `false` row through the compiler's own `record_adjudication`; `open` rows are left open.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE.parent
sys.path.insert(0, str(HERE.parents[3] / "src"))
from sdd_compiler.conflicts.adjudicate import record_adjudication  # noqa: E402
from sdd_compiler.store.graph import load_graph                    # noqa: E402

R13C = T.parent / "r13c-zero2repo-3cases"


def pairs(store):
    g = load_graph(store)
    out = {}
    for cid, c in sorted(g.conflicts.items()):
        if c["kind"] != "contradiction":
            continue
        out[cid] = (c, [g.nodes[m]["text"] for m in c["members"]])
    return out


def main(cmd, root):
    store = Path(root).resolve() / ".sdd"
    if cmd == "list":
        r13 = {}   # round 28: no earlier verdicts for this case
        planted = {}
        rec = json.loads((HERE / "recall.json").read_text())["items"]
        for item, e in rec.items():
            for c in e["conflicts"]:
                if c["kind"] == "contradiction":
                    planted[c["id"]] = item
        rows = []
        for cid, (c, texts) in pairs(store).items():
            hit = r13.get(frozenset(texts))
            rows.append({"conflict": cid, "planted": planted.get(cid, ""), "members": " ".join(c["members"]),
                         "r13c_conflict": hit[0] if hit else "", "r13c_reason": hit[1] if hit else "",
                         "text_a": texts[0].replace("\t", " ").replace("\n", " "),
                         "text_b": texts[1].replace("\t", " ").replace("\n", " "),
                         "rationale": (c.get("rationale") or "").replace("\t", " ").replace("\n", " ")})
        with open(T / "work/verdict_draft.tsv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
            w.writeheader()
            w.writerows(rows)
        print(len(rows), "contradictions;", sum(1 for r in rows if r["planted"]), "planted pairs;",
              sum(1 for r in rows if r["r13c_conflict"] and not r["planted"]), "match a round 13c pair")
    elif cmd == "apply":
        rows = list(csv.DictReader(open(HERE / "verdicts.tsv"), delimiter="\t"))
        reason_key = [k for k in rows[0] if k.startswith("reason")][0]
        n = 0
        for row in rows:
            if row["verdict"] == "false":
                record_adjudication(store, row["conflict"], "false", note=row[reason_key])
                n += 1
        print("judged false:", n, "; left open:", sum(1 for r in rows if r["verdict"] != "false"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
