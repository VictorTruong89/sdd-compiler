"""Judge the compile's contradictions on the owner's behalf (round 20, step 3). No model call.

    python3 notes/verdicts.py list  work/compile-export     -> work/verdict_draft.tsv (one row per contradiction)
    python3 notes/verdicts.py apply work/compile-export     -> records notes/verdicts.tsv with record_adjudication

Round 20 (new; the judging half of round 19's notes/oracle_store.py, without any injection). `list`
writes each open contradiction with its two node texts and, where both texts are identical to a pair
judged in round 19 (`../r19-…/notes/oracle_verdicts.tsv`, conflict ids of `../r19-…/work/compile-full`),
round 19's verdict and reason, matched on the two texts, never on ids. Rows with no match are read one
by one against the **original** case010 spec and written into `notes/verdicts.tsv` by hand. `apply`
records every `false` row through the compiler's own `record_adjudication`; `open` rows are left
open. Nothing is injected.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE.parent
sys.path.insert(0, str(HERE.parents[3] / "src"))
from sdd_compiler.conflicts.adjudicate import record_adjudication  # noqa: E402
from sdd_compiler.store.graph import load_graph                    # noqa: E402

R19 = T.parent / "r19-zero2repo-case010-conflicts"


def pairs(store):
    g = load_graph(store)
    out = {}
    for cid, c in sorted(g.conflicts.items()):
        if c["kind"] != "contradiction":
            continue
        texts = [g.nodes[m]["text"] for m in c["members"]]
        out[cid] = (c, texts)
    return out


def main(cmd, root):
    store = Path(root).resolve() / ".sdd"
    if cmd == "list":
        r19rows = {r["conflict"]: r for r in csv.DictReader(open(R19 / "notes/oracle_verdicts.tsv"), delimiter="\t")}
        reason_key = [k for k in next(iter(r19rows.values())) if k.startswith("reason")][0]
        r19 = {frozenset(t): r19rows[cid] for cid, (_, t) in pairs(R19 / "work/compile-full/.sdd").items() if cid in r19rows}
        rows = []
        for cid, (c, texts) in pairs(store).items():
            hit = r19.get(frozenset(texts))
            rows.append({"conflict": cid, "state": c["state"], "members": " ".join(c["members"]),
                         "r19_verdict": hit["verdict"] if hit else "", "r19_conflict": hit["conflict"] if hit else "",
                         "r19_reason": hit[reason_key] if hit else "",
                         "text_a": texts[0].replace("\t", " ").replace("\n", " "),
                         "text_b": texts[1].replace("\t", " ").replace("\n", " "),
                         "rationale": (c.get("rationale") or "").replace("\t", " ").replace("\n", " ")})
        with open(T / "work/verdict_draft.tsv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
            w.writeheader()
            w.writerows(rows)
        print(len(rows), "contradictions;", sum(1 for r in rows if r["r19_verdict"]), "match a round 19 pair")
    elif cmd == "apply":
        rows = list(csv.DictReader(open(HERE / "verdicts.tsv"), delimiter="\t"))
        reason_key = [k for k in rows[0] if k.startswith("reason")][0]
        n = 0
        for row in rows:
            if row["verdict"] == "false":
                record_adjudication(store, row["conflict"], "false", note=row[reason_key])
                n += 1
        print("judged false:", n, "; left open:", sum(1 for r in rows if r["verdict"] == "open"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
