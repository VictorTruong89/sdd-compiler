"""Score this trial's runs beyond Zero2Repo's judge. No model call. Round 19: round 18's scorer, constants
adapted to case010 (15 items, 197 tests, core 173, keywords); method unchanged.

    python3 notes/score.py runs/<run_id> [...]          -> notes/scores.json (merged by run id)

Per run:
  - tests: the judge's passed / total; core: the 173 tests outside round 19's footprint union (ANSWER_KEY.md);
  - sides: notes/probe.sh on the agent's saved code (`app.tgz`), in a container with no network;
  - exposure: per item and side, whether any tool result in the transcript contains that side's phrase;
  - notes: the agent's NOTES.md (saved as runs/<id>/NOTES.md) and a keyword triage per item. The
    triage only points the reader; detection is the reading recorded in notes/detection.tsv;
  - turns and $ est. (Claude Code's result line).
"""
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from plant import KEPT, PHRASES                                    # noqa: E402  (round 19: the 15 kept items)
ITEMS = list(KEPT)
_FP = json.loads((T / "notes/footprint.json").read_text())
FOOT = {t for i in ITEMS for t in _FP[i]["newly_failed"] + _FP[i]["newly_passed"]}
CORE_TOTAL = 197 - len(FOOT)                                       # 173 (ANSWER_KEY.md)
PHRASES = {i: PHRASES[i] for i in ITEMS}
# Keyword triage only points the reader to lines of NOTES.md; detection is read into notes/detection.tsv.
KEYWORDS = {
    "C01": r"transpos|damerau|edit.?distance", "C03": r"f.?measure|f1|share no element|disjoint",
    "C04": r"precision|recall|non.?set|list or tuple", "C05": r"bleu|weights?|4.?gram|bigram",
    "C08": r"tree.*(string|str)|child list|single leaf", "C09": r"discard.?empty|empty piece|gap",
    "C11": r"touch|adjacent.*chunk|joined|separate chunks", "C13": r"generat|empty.?string|empty terminal",
    "C14": r"chart|uncovered|no production|not cover", "C15": r"accuracy|different length",
    "C16": r"porter.*(ies|ties)|\bties\b|step 1a|-ie\b", "C17": r"to_lowercase|lowercas",
    "C18": r"tweet|preserve.?case", "C21": r"cannot|can \+ not|fused",
    "C22": r"straight.*quote|backtick|``|opening.?quote|closing.?quote",
}
assert set(KEYWORDS) == set(ITEMS)


def transcript(tmp: Path):
    session = next(tmp.rglob("agent/sessions/projects/-app/*.jsonl"))
    result = [json.loads(x) for x in next(tmp.rglob("agent/claude-code.txt")).read_text().splitlines()
              if '"type":"result"' in x][-1]
    outputs = []
    for line in session.read_text().splitlines():
        d = json.loads(line)
        if d.get("type") == "user" and isinstance(d["message"]["content"], list):
            for x in d["message"]["content"]:
                if x.get("type") == "tool_result":
                    c = x.get("content")
                    if isinstance(c, list):
                        c = "".join(y.get("text", "") for y in c if isinstance(y, dict))
                    outputs.append(c or "")
    return "\n".join(outputs), result


def score(run: Path) -> dict:
    detail = json.loads((run / "reward_detail.json").read_text())
    reward = json.loads((run / "reward.json").read_text())
    failed = {t.split("/")[-1] for t in detail.get("failed_tests") or []}
    total = reward.get("tests_total") or 0
    row = {"tests": reward.get("tests_passed"), "total": total,
           "core": (CORE_TOTAL - len(failed - FOOT)) if total == 197 else None, "core_total": CORE_TOTAL}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "app").mkdir()
        with tarfile.open(run / "app.tgz") as tar:
            tar.extractall(tmp / "app", filter="data")
        probe = subprocess.run(["bash", str(T / "notes/probe.sh"), str(tmp / "app")], capture_output=True, text=True)
        sides = json.loads(probe.stdout) if probe.returncode == 0 else {}
        row["sides"] = {i: (sides.get(i) or {}).get("side", "error") for i in ITEMS}
        row["probe_evidence"] = {i: (sides.get(i) or {}).get("evidence") for i in ITEMS}
        notes = next((p for p in [tmp / "app/NOTES.md"] + sorted((tmp / "app").glob("**/NOTES.md")) if p.exists()), None)
        text = notes.read_text(errors="replace") if notes else ""
        (run / "NOTES.md").write_text(text) if notes else None
        row["notes_md"] = bool(notes)
        row["notes_mentions"] = {i: bool(re.search(KEYWORDS[i], text, re.I)) for i in ITEMS}
        (tmp / "agent").mkdir()
        with tarfile.open(run / "agent.tgz") as tar:
            tar.extractall(tmp / "agent", filter="data")
        outputs, result = transcript(tmp / "agent")
        row["exposure"] = {i: {"A": a in outputs, "B": b in outputs} for i, (a, b) in PHRASES.items()}
        row["turns"], row["cost"] = result.get("num_turns"), result.get("total_cost_usd")
    return row


if __name__ == "__main__":
    out = T / "notes/scores.json"
    scores = json.loads(out.read_text()) if out.exists() else {}
    for arg in sys.argv[1:]:
        run = Path(arg)
        scores[run.name] = score(run)
        s = scores[run.name]
        print(run.name, f"tests {s['tests']}/{s['total']} core {s['core']}/{s['core_total']}",
              " ".join(f"{i}={v}" for i, v in s["sides"].items()), "notes" if s["notes_md"] else "no-notes",
              f"turns {s['turns']} $ {s['cost']}")
    out.write_text(json.dumps(scores, indent=1, sort_keys=True) + "\n")
