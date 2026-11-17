"""Make the compiler-export store: the round's measured compile with its verdicts, nothing injected. No model call.

    python3 notes/compiler_store.py case006 work/compile-compiler-case006   (a copy of r17 work/compile-full)
    python3 notes/compiler_store.py case010 work/compile-compiler-case010   (a copy of r19 work/compile-full)
    sddc --root work/compile-compiler-<case> export --allow-open --out work/export-compiler-<case>

Round 27 (step 1 of ../r19-zero2repo-case010-conflicts/notes/oracle_store.py, unchanged; step 2, the
injection of missed planted conflicts, is left out — as round 21's compiler arm). The verdicts are the
round's own `oracle_verdicts.tsv` (round 17 for case006, round 19 for case010), copied into
`notes/<case>/`: every `false` row is recorded with the compiler's `record_adjudication`; `open` rows
stay open. Contradictions between a found planted pair are not in the file, so they stay open.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "src"))
from sdd_compiler.conflicts.adjudicate import record_adjudication  # noqa: E402

case, root = sys.argv[1], Path(sys.argv[2]).resolve()
rows = list(csv.DictReader(open(HERE / case / "oracle_verdicts.tsv"), delimiter="\t"))
REASON = [k for k in rows[0] if k.startswith("reason")][0]
judged = kept = 0
for row in rows:
    if row["verdict"] == "false":
        record_adjudication(root / ".sdd", row["conflict"], "false", note=row[REASON])
        judged += 1
    else:
        kept += 1
print(f"{case}: {judged} judged false, {kept} left {set(r['verdict'] for r in rows if r['verdict'] != 'false')}")
