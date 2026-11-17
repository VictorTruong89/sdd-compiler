"""Round 27: notes/readings.txt + score/<case>/notes/scores.json -> notes/detection.tsv (rounds 18/19/25's columns:
run item named stated flagged built note; flagged = the compiler export flags the item). No model call."""
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
ITEMS = {"case006": "C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C12 C13 C14 C15 C17 C18 C20 C21 C22 C23 C25 C26 C27 C29".split(),
         "case010": "C01 C03 C04 C05 C08 C09 C11 C13 C14 C15 C16 C17 C18 C21 C22".split()}
UNFLAGGED = {"case006": set("C01 C03 C06 C12 C18 C20 C23 C25 C29".split()),
             "case010": set("C04 C05 C08 C13 C14 C17".split())}
scores = {c: json.loads((T / f"score/{c}/notes/scores.json").read_text()) for c in ITEMS}
out = ["run\titem\tnamed\tstated\tflagged\tbuilt\tnote"]
runs = 0
for line in (T / "notes/readings.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip():
        continue
    run, named, remark = [x.strip() for x in line.split("|")]
    run = "r27-" + run
    case = "case006" if "case006" in run else "case010"
    named = set(named.split())
    assert named <= set(ITEMS[case]), (run, named - set(ITEMS[case]))
    sides = scores[case][run]["sides"]
    runs += 1
    for i in ITEMS[case]:
        out.append("\t".join([run, i, "yes" if i in named else "no", "AB" if i in named else "-",
                              "no" if i in UNFLAGGED[case] else "yes", sides.get(i, "?"), ""]))
(T / "notes/detection.tsv").write_text("\n".join(out) + "\n")
print(runs, "runs,", len(out) - 1, "rows")
