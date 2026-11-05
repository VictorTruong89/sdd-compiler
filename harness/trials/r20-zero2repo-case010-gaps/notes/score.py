"""Score this trial's runs beyond Zero2Repo's judge. No model call. Round 20: round 19's scorer adapted to gaps.

    python3 notes/score.py runs/<run_id> [...]          -> notes/scores.json (merged by run id)

Changes from round 19 (../r19-zero2repo-case010-conflicts/notes/score.py): the items are the kept
gaps (`KEPT` in notes/remove.py) instead of planted conflicts; the probe reads each gap as
upstream / alternative / other / not built (notes/probe.py) instead of side A / B; no exposure
phrases (nothing is planted, so there is no phrase to look for); the triage keywords are per gap.
Per run:
  - tests: the judge's passed / total; core: the tests outside this round's footprint union
    (notes/footprint.json, kept gaps only; ANSWER_KEY.md);
  - built: notes/probe.sh on the agent's saved code (`app.tgz`), in a container with no network;
  - notes: the agent's NOTES.md (saved as runs/<id>/NOTES.md) and a keyword triage per gap. The
    triage only points the reader; flagged / silent is the reading recorded in notes/detection.tsv;
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
from remove import KEPT                                            # noqa: E402  (round 20: the kept gaps)
ITEMS = list(KEPT)
_FP = json.loads((T / "notes/footprint.json").read_text())
FOOT = {t for i in ITEMS for t in _FP[i]["newly_failed"] + _FP[i]["newly_passed"]}
CORE_TOTAL = 197 - len(FOOT)
# Keyword triage only points the reader to lines of NOTES.md; the reading is notes/detection.tsv.
KEYWORDS = {
    "G01": r"substitution.?cost", "G02": r"jaccard", "G03": r"recall|empty reference",
    "G04": r"brevity|\bbp\b", "G05": r"brevity|closest|tie|equally", "G06": r"clip|modified precision|bleu.*count",
    "G07": r"whole (input|string)|spaces?|one token|multi.?word|split.*word", "G08": r"unsupported|klingon|language name|message",
    "G09": r"snowball.*porter|porter.*snowball|['\"]porter['\"]|original porter", "G10": r"single.?letter|one.?letter|\boed\b|refus",
    "G11": r"prefix|lancaster", "G12": r"regexp.?stemmer|regular.expression stemmer|every match|first match|count",
    "G13": r"span|offset|exclusive|inclusive", "G14": r"comma|colon|thousand|1,000",
    "G15": r"point|period|full stop|decimal|\bdot\b", "G16": r"whitespace.*pattern|pattern.*whitespace|spaces? in",
    "G17": r"empty (tagged|token|input|list)|no children", "G18": r"grammar.*(type|not a str|non.?str|invalid)|typeerror",
    "G19": r"len\(|length", "G20": r"equal|__eq__|==", "G21": r"start symbol|first production|start",
    "G22": r"smooth|laplace|lidstone|zero probab|ele\b|expected.likelihood", "G23": r"unseen|never seen|unknown feature",
    "G24": r"no (shared|common|known) feature|empty featureset|shares no|prior",
}


def transcript(tmp: Path):
    result = [json.loads(x) for x in next(tmp.rglob("agent/claude-code.txt")).read_text().splitlines()
              if '"type":"result"' in x][-1]
    return result


def score(run: Path) -> dict:
    detail = json.loads((run / "reward_detail.json").read_text())
    reward = json.loads((run / "reward.json").read_text())
    failed = {t.split("/")[-1] for t in detail.get("failed_tests") or []}
    total = reward.get("tests_total") or 0
    row = {"tests": reward.get("tests_passed"), "total": total,
           "core": (CORE_TOTAL - len(failed - FOOT)) if total == 197 else None, "core_total": CORE_TOTAL,
           "footprint_failed": sorted(failed & FOOT)}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "app").mkdir()
        with tarfile.open(run / "app.tgz") as tar:
            tar.extractall(tmp / "app", filter="data")
        probe = subprocess.run(["bash", str(T / "notes/probe.sh"), str(tmp / "app")] + ITEMS, capture_output=True, text=True)
        built = json.loads(probe.stdout) if probe.returncode == 0 else {}
        row["built"] = {i: (built.get(i) or {}).get("built", "probe-error") for i in ITEMS}
        row["probe_evidence"] = {i: (built.get(i) or {}).get("evidence") for i in ITEMS}
        notes = next((p for p in [tmp / "app/NOTES.md"] + sorted((tmp / "app").glob("**/NOTES.md")) if p.exists()), None)
        text = notes.read_text(errors="replace") if notes else ""
        (run / "NOTES.md").write_text(text) if notes else None
        row["notes_md"] = bool(notes)
        row["notes_mentions"] = {i: bool(re.search(KEYWORDS[i], text, re.I)) for i in ITEMS}
        (tmp / "agent").mkdir()
        if (run / "agent.tgz").exists():
            with tarfile.open(run / "agent.tgz") as tar:
                tar.extractall(tmp / "agent", filter="data")
            result = transcript(tmp / "agent")
            row["turns"], row["cost"] = result.get("num_turns"), result.get("total_cost_usd")
        else:
            row["turns"] = row["cost"] = None
    return row


if __name__ == "__main__":
    out = T / "notes/scores.json"
    scores = json.loads(out.read_text()) if out.exists() else {}
    for arg in sys.argv[1:]:
        run = Path(arg)
        scores[run.name] = score(run)
        s = scores[run.name]
        print(run.name, f"tests {s['tests']}/{s['total']} core {s['core']}/{s['core_total']}",
              " ".join(f"{i}={v}" for i, v in s["built"].items()), "notes" if s["notes_md"] else "no-notes",
              f"turns {s['turns']} $ {s['cost']}")
    out.write_text(json.dumps(scores, indent=1, sort_keys=True) + "\n")
