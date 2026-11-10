"""Second reader for set 2a ("conflict named"): a fresh model reads each run's NOTES.md against the answer
key under the strict rule, blind to run, arm and model and to the first reader's readings. Spends model calls
(the owner's subscription, local `claude -p`); approved by the owner 2026-11-09 ("do all A-B-C-D by yourself").

    python3 notes/reader2.py read  [round ...]   # one call per run not yet read -> work/raw/<code>.json
    python3 notes/reader2.py table                # -> notes/reader2.tsv, notes/agreement.json (no model call)

Reader 2: `claude -p --model sonnet --tools ""` in an empty folder (no tools, no project files, no memory).
It sees only: the strict rule (round 21 TRIAL.md, word for word), each item's side A and side B (the round's
ANSWER_KEY.md), and the NOTES.md under a code (N001...). Reader 1 is the assistant in Claude Code (the readings in each
round's notes/detection.tsv; rounds 24-25 read by Claude Opus 5.5), not blind to arm.
"""
import csv
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parents[1]
TR = T.parent
ROUNDS = {
    "r18": "r18-zero2repo-case006-notes-both-sides",
    "r19": "r19-zero2repo-case010-conflicts",
    "r21": "r21-zero2repo-case016-conflicts-gaps",
    "r23": "r23-zero2repo-case016-review-list",
    "r24": "r24-zero2repo-case016-settled-list",
    "r25": "r25-zero2repo-review-list-case006-case010",
}
# r25 has no answer key of its own: case006 runs use round 18's, case010 runs round 19's (same planted spec).
KEY_OF = {"r18": "r18", "r19": "r19", "r21": "r21", "r23": "r21", "r24": "r21"}
RULE = ("*Named*: `NOTES.md`, in one place or in lines that refer to each other, states the content of side A, "
        "the content of side B, and presents them as disagreeing or as a choice. A conflict id or topic alone is "
        "not enough. Which side was built does not matter.")
PROMPT = """You are checking a coding agent's notes file against a list of known disagreements in the specification it built from.

For each item below, decide whether the notes NAME it under this rule:

{rule}

Read side A and side B as meanings, not exact words: the notes may paraphrase, quote other lines that say the same, or describe the two sides in their own words. An item counts as named only if both sides' content is stated and they are presented as disagreeing or as a choice. A line that states only the side the agent built, or only mentions the topic, is not named.

Items (id: side A || side B):
{items}

Answer with one JSON object and nothing else, in this shape:
{{"<item id>": {{"named": "yes" or "no", "quote": "<the notes' words, at most 200 characters, or empty>"}}, ...}}
with exactly one key for each item id listed above, and no other keys.

The notes file ({code}):
<<<NOTES
{notes}
NOTES>>>
"""


def key_rows(rnd):
    """{item: (side A, side B)} for the round's kept conflicts, first table row per id."""
    text = (TR / ROUNDS[rnd] / "ANSWER_KEY.md").read_text()
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not re.fullmatch(r"C\d\d", cells[0]) or cells[0] in out:
            continue
        if rnd == "r21":
            out[cells[0]] = (cells[1], cells[2])
        else:
            out[cells[0]] = (cells[2], cells[3])
    return out


def reader1():
    """[(round, run, item, named)] from each round's detection.tsv (conflicts only)."""
    rows = []
    for rnd, folder in ROUNDS.items():
        f = TR / folder / "notes/detection.tsv"
        if not f.exists():
            continue
        for r in csv.DictReader(open(f), delimiter="\t"):
            if r["item"].startswith("C"):
                rows.append((rnd, r["run"], r["item"], r["named"]))
    return rows


def key_for(rnd, run):
    if rnd == "r25":
        return "r18" if "case006" in run else "r19"
    return KEY_OF[rnd]


def codes():
    """Stable code per run: N001... in a seeded shuffle of every run known so far (codes never change)."""
    f = T / "work/codes.json"
    known = json.loads(f.read_text()) if f.exists() else {}
    runs = sorted({(rnd, run) for rnd, run, _, _ in reader1()})
    new = [f"{rnd}|{run}" for rnd, run in runs if f"{rnd}|{run}" not in known]
    random.Random(len(known) + 2611).shuffle(new)
    for k in new:
        known[k] = f"N{len(known) + 1:03d}"
    f.write_text(json.dumps(known, indent=1))
    return known


def read(rounds):
    raw = T / "work/raw"
    raw.mkdir(parents=True, exist_ok=True)
    cmap = codes()
    items_of = {}
    for rnd, run, item, _ in reader1():
        items_of.setdefault((rnd, run), []).append(item)
    for k, code in sorted(cmap.items(), key=lambda kv: kv[1]):
        rnd, run = k.split("|")
        if rounds and rnd not in rounds or (raw / f"{code}.json").exists():
            continue
        notes = (TR / ROUNDS[rnd] / "runs" / run / "NOTES.md")
        notes = notes.read_text(errors="replace") if notes.exists() else "(no NOTES.md)"
        kr = key_rows(key_for(rnd, run))
        items = "\n".join(f"{i}: {kr[i][0]} || {kr[i][1]}" for i in sorted(items_of[(rnd, run)]))
        prompt = PROMPT.format(rule=RULE, items=items, code=code, notes=notes)
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run(["claude", "-p", "--model", "sonnet", "--tools", "", "--output-format", "json",
                                "--no-session-persistence", "--setting-sources", ""],
                               input=prompt, capture_output=True, text=True, cwd=d, timeout=900,
                               env={k2: v for k2, v in __import__("os").environ.items() if k2 != "ANTHROPIC_API_KEY"})
        if p.returncode:
            sys.exit(f"{code}: claude exit {p.returncode}: {p.stderr[:300]}")
        res = json.loads(p.stdout)
        body = res.get("result", "")
        m = re.search(r"\{.*\}", body, re.S)
        ans = json.loads(m[0])
        missing = set(items_of[(rnd, run)]) - set(ans)
        extra = set(ans) - set(items_of[(rnd, run)])
        if extra:
            print(code, "extra keys ignored:", sorted(extra), flush=True)
        if missing:
            sys.exit(f"{code}: missing items {sorted(missing)}")
        (raw / f"{code}.json").write_text(json.dumps({"answer": ans, "cost_usd": res.get("total_cost_usd"),
                                                     "model": list((res.get("modelUsage") or {}).keys())}, indent=1))
        print(code, rnd, len(ans), "items", res.get("total_cost_usd"), flush=True)
        if __import__("os").environ.get("ONE"):
            return


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "yes" for a, _ in pairs) / n
    pb = sum(b == "yes" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def table():
    cmap = codes()
    out, groups, cost = [], {}, 0.0
    for rnd, run, item, n1 in reader1():
        f = T / "work/raw" / f"{cmap[f'{rnd}|{run}']}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        a = d["answer"][item]
        n2 = "yes" if str(a.get("named", "")).lower().startswith("y") else "no"
        out.append((rnd, run, item, n1, n2, a.get("quote", "")[:200].replace("\t", " ").replace("\n", " ")))
        arm = run.split("-")[2] if rnd != "r25" else "review-" + run.split("-")[2]
        for g in ("all", rnd, f"{rnd}-{arm}"):
            groups.setdefault(g, []).append((n1, n2))
    for f in (T / "work/raw").glob("*.json"):
        cost += json.loads(f.read_text()).get("cost_usd") or 0
    with open(T / "notes/reader2.tsv", "w") as fh:
        fh.write("round\trun\titem\treader1\treader2\treader2_quote\n")
        for r in out:
            fh.write("\t".join(r) + "\n")
    agree = {}
    for g, pairs in sorted(groups.items()):
        po, k = kappa(pairs)
        agree[g] = {"n": len(pairs), "agree": round(po, 3), "kappa": round(k, 3),
                    "r1_yes": sum(a == "yes" for a, _ in pairs), "r2_yes": sum(b == "yes" for _, b in pairs),
                    "r1_yes_r2_no": sum(a == "yes" and b == "no" for a, b in pairs),
                    "r1_no_r2_yes": sum(a == "no" and b == "yes" for a, b in pairs)}
        print(f"{g:22s} n={len(pairs):4d} agree={po:.3f} kappa={k:.3f} r1 yes={agree[g]['r1_yes']} r2 yes={agree[g]['r2_yes']}")
    agree["_cost_usd_est"] = round(cost, 2)
    (T / "notes/agreement.json").write_text(json.dumps(agree, indent=1))
    print("cost $ est.", round(cost, 2))


if __name__ == "__main__":
    {"read": lambda: read(sys.argv[2:]), "table": table}[sys.argv[1]]()
