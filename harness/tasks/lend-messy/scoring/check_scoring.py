"""Check `lend_score.py` against builds whose behaviour is known. No model, no network, no Docker.

    python3 check_scoring.py

Three variants of the reference implementation are made by text replacement in a temporary folder:
  a        the reference as it is: statement A of every contradiction
  b        statement B of every contradiction, plus one extra command
  neither  behaviour that no statement supports, where the probe can show it (P1, P2, P4, P10)
Each is scored and the result compared with what the variant was built to do. Exits 1 on any mismatch.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = (HERE.parent / "reference" / "src" / "lend_ref" / "cli.py").read_text(encoding="utf-8")

CAP = "FEE_PER_DAY, FEE_CAP = 50, 1000"
RENEW = 'loan["due"] = (due_of(loan) + dt.timedelta(days=period)).isoformat()'
BLOCK = '    if blocked(state, a.member, on):\n        raise Fail(3, f"{a.member} has an overdue loan")\n'
ROWS = 'rows = [(days_overdue(l, on), i, l) for i, l in state["loans"].items() if days_overdue(l, on) > 0]'
HEADER = 'writer.writerow(["item", "title", "member", "due", "days_overdue"])'
ROW = 'writer.writerow([item, state["items"][item]["title"], loan["member"], loan["due"], days])'
STATUS = 's = sub.add_parser("status")'

VARIANTS = {
    "a": ([], {"P1": "A", "P2": "A", "P3": "A", "P4": "A", "P10": "A"}, 0),
    "b": ([
        (CAP, "FEE_PER_DAY, FEE_CAP = 50, 1500"),
        (RENEW, 'loan["due"] = (on + dt.timedelta(days=period)).isoformat()'),
        (BLOCK, BLOCK + '    if state["members"][a.member]["fees_cents"] > 500:\n        raise Fail(3, "fees over $5")\n'),
        (ROWS, ROWS[:-1] + ' or (due_of(l) == on and os.environ.get("LEND_NOW", "")[11:13] >= "18")]'),
        (HEADER, HEADER.replace('"days_overdue"]', '"days_overdue", "email"]')),
        (ROW, ROW.replace("days])", 'days, state["members"][loan["member"]]["email"]])')),
        (STATUS, 'sub.add_parser("pay").set_defaults(fn=cmd_init)\n    ' + STATUS),
    ], {"P1": "B", "P2": "B", "P3": "B", "P4": "B", "P10": "B"}, 1),
    "neither": ([
        (CAP, "FEE_PER_DAY, FEE_CAP = 50, 99999"),
        (RENEW, 'loan["due"] = (due_of(loan) + dt.timedelta(days=period + 1)).isoformat()'),
        (BLOCK, BLOCK + '    if state["members"][a.member]["fees_cents"] > 500:\n        raise Fail(2, "fees")\n'),
        (ROWS, ROWS.replace("days_overdue(l, on) > 0]", "days_overdue(l, on) >= 0]")),
    ], {"P1": "neither", "P2": "neither", "P3": "A", "P4": "neither", "P10": "neither"}, 0),
}

failures = 0
for name, (edits, expected, expected_extra) in VARIANTS.items():
    work = Path(tempfile.mkdtemp(prefix=f"lend-check-{name}-"))
    code = CLI
    for old, new in edits:
        assert old in code, f"variant {name}: text to replace not found: {old[:50]}"
        code = code.replace(old, new)
    (work / "lend_ref").mkdir()
    (work / "lend_ref" / "__init__.py").write_text("", encoding="utf-8")
    (work / "lend_ref" / "cli.py").write_text(code, encoding="utf-8")
    wrapper = work / "lend"
    wrapper.write_text(f'#!/bin/sh\nPYTHONPATH={work} exec {sys.executable} -m lend_ref.cli "$@"\n', encoding="utf-8")
    wrapper.chmod(0o755)
    subprocess.run([sys.executable, str(HERE / "lend_score.py"), "--cmd", str(wrapper), "--app", str(work),
                    "--out-dir", str(work / "out"), "--settled", "P2=A,P3=B"], check=True, capture_output=True)
    score = json.loads((work / "out" / "score.json").read_text(encoding="utf-8"))
    got = {p: v["side"] for p, v in score["contradictions"].items()}
    followed = (expected["P2"] == "A") + (expected["P3"] == "B")      # verdicts given above
    ok = (got == expected and score["rewards"]["extra_commands"] == expected_extra
          and score["rewards"]["settled_followed"] == followed and score["rewards"]["settled_total"] == 2)
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}: sides {got}, extra commands {score['extra_commands']}")
    if not ok:
        print("     expected", expected, expected_extra, "| evidence", score["contradictions"])

# help text in the shape argparse prints when the command list has a metavar (seen in round 3)
fake = Path(tempfile.mkdtemp(prefix="lend-check-help-")) / "lend"
fake.write_text("#!/bin/sh\ncat <<'EOF'\nusage: lend [-h] COMMAND ...\n\npositional arguments:\n  COMMAND\n"
                "    init      create a store\n    member    manage members\n    item      manage items\n"
                "    checkout  lend\n    renew     extend\n    return    end a loan\n    status    show\n"
                "    report    write the list\n    pay       settle fees\n\noptions:\n  -h, --help  show this help\nEOF\n",
                encoding="utf-8")
fake.chmod(0o755)
sys.path.insert(0, str(HERE))
from lend_score import extra_commands  # noqa: E402
ok = extra_commands([str(fake)]) == (1, ["pay"])
failures += not ok
print(f"{'ok  ' if ok else 'FAIL'} help with a metavar: {extra_commands([str(fake)])}")

# the keyword triage of the agent's notes
notes = Path(tempfile.mkdtemp(prefix="lend-check-notes-"))
(notes / "OPEN_QUESTIONS.md").write_text(
    "1. Late fees: fees.md says 1000 cents, vision.md says $15. Chose 1000.\n"
    "2. The report counts a loan as overdue from 18:00; loans/spec.md says the day after. Chose the day after.\n"
    "3. ops/notes.md wants the contact email in the report; reports/spec.md forbids it.\n"
    "4. The fee table in pack 15 is unclear.\n", encoding="utf-8")      # a bare 15 must not count as A1
subprocess.run([sys.executable, str(HERE / "lend_score.py"), "--not-installable", "--app", str(notes),
                "--out-dir", str(notes / "out")], check=True, capture_output=True)
score = json.loads((notes / "out" / "score.json").read_text(encoding="utf-8"))
want = {"A1": True, "A2": True, "A3": True, "A4": False, "A5": False, "A6": False}
ok = score["noticed_auto"] == want and score["rewards"]["omissions"] == 24 and score["rewards"]["installable"] == 0
failures += not ok
print(f"{'ok  ' if ok else 'FAIL'} notes: {score['noticed_auto']}")
sys.exit(1 if failures else 0)
