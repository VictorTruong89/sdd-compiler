"""Score one build of `lend` beyond pass/fail tests. Standard library only, no model, no network.

    python lend_score.py --cmd /tmp/venv/bin/lend --app /app --junit junit.xml --out-dir /logs/verifier
    python lend_score.py --not-installable --app /app --out-dir /logs/verifier

Writes two files in --out-dir:
  reward.json  numbers only (what Harbor shows as named rewards)
  score.json   the detail behind them: per requirement, per contradiction, per audit item

What each number is, and what it is not:
  requirements_met / omissions   R1-R24 of ../requirements.md. A requirement is met when every hidden
                                 test named `test_r<N>_*` passed. omissions = 24 - requirements_met.
  contradictions_*               The five planted contradictions (P1-P4, P10 of ../ANSWER_KEY.md), probed
                                 through the command. Each build takes statement A, statement B, or
                                 neither. "neither" is behaviour that no statement in the spec supports:
                                 the automatic part of the invention count. Which side is taken is
                                 recorded, never judged.
  noticed_auto                   Of the six audit items A1-A6, how many the agent's OPEN_QUESTIONS.md or
                                 IMPLEMENTATION_NOTES.md mention, by keyword. A triage for the human
                                 audit (scale 0/1/2 in requirements.md), NOT the audit.
  extra_commands                 Commands in `lend --help` beyond the eight in the spec; -1 when the help
                                 text could not be parsed. A second automatic invention signal.
  settled_followed / settled_total
                                 With `--settled P2=A,P3=B`: the owner settled those contradictions, and
                                 the build is checked against the settled side with the same probes.
                                 Without the option both are 0.
Inventions inside the code that no probe reaches still need the human audit.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shlex
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIREMENTS = [f"R{n}" for n in range(1, 25)]
SPEC_COMMANDS = {"init", "member", "item", "checkout", "renew", "return", "status", "report"}
DOCS = ("OPEN_QUESTIONS.md", "IMPLEMENTATION_NOTES.md")
# audit item -> every pattern must be found in the agent's notes (lower-cased)
NOTICED = {
    "A1": [r"\$\s?15\b|\b15 dollars|1500 cents", r"cap|fee|owe"],   # not a bare 15: "15 June", "pack 15"
    "A2": [r"18[:.h]00|6\s?p\.?m"],
    "A3": [r"e-?mail", r"report|overdue list"],
    "A4": [r"patron|\$\s?5|five dollars|500 cents", r"borrow|block|check\s?out|go out"],
    "A5": [r"renew", r"example|24 june|june 24|2026-06-24|renewal date"],
    "A6": [r"\bfast\b"],
}


class Lend:
    """One fresh store in a temporary directory."""

    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self.dir = tempfile.mkdtemp(prefix="lend-probe-")

    def run(self, *args: str, now: str = "2026-06-01") -> subprocess.CompletedProcess:
        return subprocess.run([*self.cmd, *args], cwd=self.dir, env={**os.environ, "LEND_NOW": now},
                              capture_output=True, text=True, timeout=60)

    def must(self, *args: str, now: str = "2026-06-01") -> subprocess.CompletedProcess:
        result = self.run(*args, now=now)
        if result.returncode != 0:
            raise RuntimeError(f"lend {' '.join(args)} -> {result.returncode}: {result.stderr.strip()[:200]}")
        return result

    def setup(self) -> "Lend":
        self.must("init")
        self.must("member", "add", "M1", "--name", "Ana", "--email", "ana@example.org")
        for item in ("T1", "T2"):
            self.must("item", "add", item, "--title", f"Tool {item}", "--category", "hand")
        return self

    def status(self, now: str) -> dict:
        return json.loads(self.must("status", "--json", now=now).stdout)

    def report(self, now: str) -> list[list[str]]:
        out = Path(self.dir) / "report.csv"
        self.must("report", "--out", str(out), now=now)
        return list(csv.reader(out.read_text(encoding="utf-8").splitlines()))


def probe_p1(cmd):
    """Fee cap. 40 days late at 50 cents a day: capped at $10 (A), at $15 (B), or something else."""
    s = Lend(cmd).setup()
    s.must("checkout", "T1", "M1")                      # due 2026-06-15
    s.must("return", "T1", now="2026-07-25")            # 40 days late
    fee = s.status("2026-07-25")["members"][0]["fees_cents"]
    return {1000: "A", 1500: "B"}.get(fee, "neither"), f"fee after 40 days late: {fee} cents"


def probe_p2(cmd):
    """Report boundary on the due date: not overdue that day (A), or overdue from 18:00 (B)."""
    s = Lend(cmd).setup()
    s.must("checkout", "T1", "M1")                      # due 2026-06-15
    morning = len(s.report("2026-06-15T10:00:00")) - 1
    evening = len(s.report("2026-06-15T19:00:00")) - 1
    side = "neither" if morning else ("B" if evening else "A")
    return side, f"report rows on the due date: {morning} at 10:00, {evening} at 19:00"


def probe_p3(cmd):
    """Report privacy: no email in the report (A), or the member's email in each row (B)."""
    s = Lend(cmd).setup()
    s.must("checkout", "T1", "M1")
    rows = s.report("2026-06-20")
    if len(rows) < 2:
        return "neither", "no overdue row 5 days after the due date"
    has_email = any("ana@example.org" in cell for cell in rows[1])
    return ("B" if has_email else "A"), f"report header: {rows[0]}"


def probe_p4(cmd):
    """Fees and borrowing: fees never block (A), or a member owing more than $5 cannot borrow (B)."""
    s = Lend(cmd).setup()
    s.must("checkout", "T1", "M1")
    s.must("return", "T1", now="2026-06-27")            # 12 days late: 600 cents
    fee = s.status("2026-06-27")["members"][0]["fees_cents"]
    code = s.run("checkout", "T2", "M1", now="2026-06-27").returncode
    return {0: "A", 3: "B"}.get(code, "neither"), f"owing {fee} cents, next checkout exits {code}"


def probe_p10(cmd):
    """Early renewal: a period added to the current due date (A), or counted from the renewal date (B)."""
    s = Lend(cmd).setup()
    s.must("checkout", "T1", "M1")                      # due 2026-06-15
    s.must("renew", "T1", now="2026-06-10")
    due = s.status("2026-06-10")["loans"][0]["due"]
    return {"2026-06-29": "A", "2026-06-24": "B"}.get(due, "neither"), f"due after renewing on 10 June: {due}"


PROBES = {"P1": probe_p1, "P2": probe_p2, "P3": probe_p3, "P4": probe_p4, "P10": probe_p10}


def requirement_states(junit: Path | None) -> tuple[dict[str, str], int, int]:
    states = {r: "no test ran" for r in REQUIREMENTS}
    if junit is None or not junit.exists():
        return states, 0, 0
    by_req: dict[str, list[bool]] = {}
    cases = list(ET.parse(junit).getroot().iter("testcase"))
    for case in cases:
        m = re.match(r"test_r(\d+)_", case.get("name", ""))
        passed = all(case.find(tag) is None for tag in ("failure", "error", "skipped"))
        if m:
            by_req.setdefault(f"R{m.group(1)}", []).append(passed)
    for req, results in by_req.items():
        if req in states:
            states[req] = "met" if all(results) else "not met"
    passed = sum(all(c.find(t) is None for t in ("failure", "error", "skipped")) for c in cases)
    return states, passed, len(cases)


def extra_commands(cmd: list[str]) -> tuple[int, list[str]]:
    try:
        text = subprocess.run([*cmd, "--help"], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return -1, []
    found = set()
    for group in re.findall(r"\{([a-z0-9_,-]+)\}", text):               # argparse: {init,member,...}
        found |= set(group.split(","))
    block = re.search(r"^Commands:\n((?:[ \t]+\S.*\n?)+)", text, re.M)    # click and typer
    if block:
        found |= {line.split()[0] for line in block.group(1).splitlines() if line.strip()}
    # argparse with a metavar, and most hand-written help: "  name   description" lines
    found |= set(re.findall(r"^\s{2,}([a-z][a-z0-9_-]*)\s{2,}\S", text, re.M))
    if not found & SPEC_COMMANDS:
        return -1, []
    extra = sorted(found - SPEC_COMMANDS - {"help"})
    return len(extra), extra


def noticed(app: Path) -> tuple[dict[str, bool], dict[str, bool]]:
    present = {name: (app / name).is_file() for name in DOCS}
    text = "\n".join((app / n).read_text(encoding="utf-8", errors="replace") for n in DOCS if present[n]).lower()
    return {item: all(re.search(p, text) for p in patterns) for item, patterns in NOTICED.items()}, present


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", default="lend")
    ap.add_argument("--app", type=Path, required=True)
    ap.add_argument("--junit", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--not-installable", action="store_true")
    ap.add_argument("--settled", default="", help="owner verdicts, e.g. P2=A,P3=B")
    a = ap.parse_args()
    cmd = shlex.split(a.cmd)
    settled = dict(pair.split("=") for pair in a.settled.split(",") if pair)
    if set(settled) - set(PROBES) or set(settled.values()) - {"A", "B"}:
        ap.error(f"--settled takes {'/'.join(PROBES)}=A|B pairs, got {a.settled!r}")

    states, tests_passed, tests_seen = requirement_states(None if a.not_installable else a.junit)
    met = sum(s == "met" for s in states.values())
    sides: dict[str, dict] = {}
    if a.not_installable:
        sides = {p: {"side": "not run", "evidence": "the package did not install"} for p in PROBES}
        n_extra, extra = -1, []
    else:
        for name, probe in PROBES.items():
            try:
                side, evidence = probe(cmd)
            except Exception as exc:                     # a probe that cannot run is reported, not hidden
                side, evidence = "error", f"{type(exc).__name__}: {exc}"[:300]
            sides[name] = {"side": side, "evidence": evidence}
        n_extra, extra = extra_commands(cmd)
    seen, present = noticed(a.app)

    count = lambda side: sum(v["side"] == side for v in sides.values())   # noqa: E731
    reward = {
        "reward": tests_passed / len(REQUIREMENTS) if tests_seen else 0,
        "tests_passed": tests_passed,
        "tests_total": len(REQUIREMENTS),
        "installable": 0 if a.not_installable else 1,
        "requirements_met": met,
        "omissions": len(REQUIREMENTS) - met,
        "contradictions_side_a": count("A"),
        "contradictions_side_b": count("B"),
        "contradictions_neither": count("neither"),
        "contradictions_error": count("error") + count("not run"),
        "noticed_auto": sum(seen.values()),
        "extra_commands": n_extra,
        "settled_followed": sum(sides[p]["side"] == side for p, side in settled.items()),
        "settled_total": len(settled),
        "has_open_questions": int(present["OPEN_QUESTIONS.md"]),
        "has_implementation_notes": int(present["IMPLEMENTATION_NOTES.md"]),
    }
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "reward.json").write_text(json.dumps(reward), encoding="utf-8")
    (a.out_dir / "score.json").write_text(json.dumps({
        "rewards": reward, "tests_collected": tests_seen, "requirements": states, "contradictions": sides,
        "settled": {p: {"verdict": side, "followed": sides[p]["side"] == side} for p, side in settled.items()},
        "noticed_auto": seen, "extra_commands": extra, "documents_present": present}, indent=1), encoding="utf-8")
    print(json.dumps(reward))


if __name__ == "__main__":
    main()
