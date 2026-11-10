"""Score this trial's runs beyond Zero2Repo's judge. No model call.

    python3 notes/score.py runs/<run_id> [...]          -> notes/scores.json (merged by run id)

Round 21: round 19's scorer (conflicts: exposure phrases, sides) and round 20's (gaps: built value) in one,
for case016's 388 tests. Items are the kept conflicts and gaps (`KEPT_C`, `KEPT_G` in notes/plant.py).
Per run:
  - tests: the judge's passed / total; core: the tests outside this round's footprint union (conflicts
    and gaps together; notes/footprint.json, ANSWER_KEY.md); footprint tests failed, by name;
  - built: notes/probe.sh on the agent's saved code (`app.tgz`), in a container with no network:
    upstream (side A of a conflict; the removed fact of a gap) / alternative (side B; the gap's
    alternative) / other / not built;
  - exposure (conflicts): per side, whether any tool result in the transcript contains that side's phrase;
  - notes: the agent's NOTES.md (saved as runs/<id>/NOTES.md) and a keyword triage per item. The triage
    only points the reader; named / flagged is the reading recorded in notes/detection.tsv;
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
from plant import KEPT_C, KEPT_G, PHRASES                          # noqa: E402
ITEMS = list(KEPT_C) + list(KEPT_G)
_FP = json.loads((T / "notes/footprint.json").read_text())
FOOT = {t for i in ITEMS for t in _FP[i]["newly_failed"] + _FP[i]["newly_passed"]}
TOTAL = 388
CORE_TOTAL = TOTAL - len(FOOT)
PHRASES = {i: PHRASES[i] for i in KEPT_C}
# Keyword triage only points the reader to lines of NOTES.md; the reading is notes/detection.tsv.
KEYWORDS = {
    "C01": r"hedg", "C02": r"opener", "C03": r"trailing|stray whitespace|\b68\b", "C04": r"confidence|250|300 words",
    "C05": r"interval|--ci|score_ci|sentences", "C06": r"decisive|\b45\b", "C07": r"unknown option|exit (status|code)",
    "C08": r"operand|first file|last file|several files|multiple files", "C09": r"usage|--help|stderr|error stream",
    "C10": r"blockquote", "C11": r"transition", "C12": r"false range|from 9 to 5|numeric span",
    "C13": r"utm", "C14": r"tailing|no .{0,10}tail|\bno\b.{0,20}phrase", "C15": r"no-break|nbsp|u\+00a0",
    "C16": r"hard break|trailing spaces", "C17": r"apply_patch|16|ten paths|\b10\b", "C18": r"ledger.*(20|50)|newest|records",
    "C19": r"seven days|one day|7 days|1 day|ledger age|older than", "C20": r"PROSECHECK_DEFAULT_MODE|environment|precedence",
    "C21": r"stop prosecheck|stop phrase|prosecheck off", "C22": r"200|500|session prose|prose score",
    "C23": r"transcript", "C25": r"tailing|negation|catalogue 17|\b17\b", "C26": r"em.?dash|\b58\b",
    "G01": r"dialect|two (or more )?hits|single.*hit", "G02": r"zero.?width|split", "G03": r"homoglyph|lookalike|mixed.?script",
    "G04": r"\bnul\b|null byte|binary|\\x00", "G05": r"indent", "G06": r"indent|leading", "G07": r"crlf|line ending|newline|\\r\\n",
    "G08": r"epub|chapter|order", "G09": r"confidence.*(none|nudge)|none.*nudge|zero.?confidence",
    "G10": r"claude\.md|instruction|case", "G11": r"memory", "G12": r"permission|0o?600|chmod|owner",
    "G13": r"message (id|identifier)|same id|duplicate|turns", "G14": r"apply_patch|\*\*\*|asterisk",
    "G19": r"decisive|\b65\b", "G21": r"no-break|nbsp|invisible", "G25": r"sample", "G30": r"doctor|detector check|python",
    "G33": r"welcome|cannot be written|unwritable|read-only", "G60": r"\.docx|\.pdf|empty ledger|nothing scored",
    "G67": r"\.py|source.?code|extension|plain text",
}


def transcript(tmp: Path):
    session = next(tmp.rglob("agent/sessions/projects/-app/*.jsonl"))
    # split on "\n" only: str.splitlines() also splits on U+2028, U+0085 ..., which case016's prose holds
    # inside JSON strings (round 21 check run)
    lines = [json.loads(x) for x in next(tmp.rglob("agent/claude-code.txt")).read_text().split("\n")
             if '"type":"result"' in x]
    # a background task can wake the agent after its final answer: one more result line, whose num_turns
    # counts only that wake-up (round 21, r21-haiku-compiler-5: 63 + 1). Turns are summed; the cost is
    # cumulative, so the last line's is kept.
    result = dict(lines[-1], num_turns=sum(x.get("num_turns") or 0 for x in lines), result_lines=len(lines))
    outputs = []
    for line in session.read_text().split("\n"):
        if not line.strip():
            continue
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
           "core": (CORE_TOTAL - len(failed - FOOT)) if total == TOTAL else None, "core_total": CORE_TOTAL,
           "footprint_failed": {i: sorted(failed & set(_FP[i]["newly_failed"] + _FP[i]["newly_passed"])) for i in ITEMS
                                if failed & set(_FP[i]["newly_failed"] + _FP[i]["newly_passed"])}}
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
            outputs, result = transcript(tmp / "agent")
            row["exposure"] = {i: {"A": a in outputs, "B": b in outputs} for i, (a, b) in PHRASES.items()}
            row["turns"], row["cost"] = result.get("num_turns"), result.get("total_cost_usd")
        else:
            row["exposure"], row["turns"], row["cost"] = {}, None, None
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
