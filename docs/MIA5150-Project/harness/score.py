"""Score one run: install what the agent built, run the hidden tests, count what it accounted for.

    python score.py --run ~/sddc-runs/study-runs/<run> --task ../tasks/f1-ingest

The agent's code is untrusted, so installing and testing it happen in the same sandbox as the run
(network on, for PyPI). Writes <run>/score/score.json and junit.xml. No model call.

Omissions and hallucinations beyond the tests are a human audit (proposal, evaluation plan); this
script lists the `audit` rows of requirements.md for that, it does not decide them.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sandbox import bwrap_argv  # noqa: E402

SCRIPT = """set -e
python3 -m venv /work/venv
/work/venv/bin/pip install -q -e /work/ws pytest pyyaml > /work/pip.log 2>&1 || { echo PIP_FAILED; exit 3; }
/work/venv/bin/pip freeze > /work/freeze.txt
cd /work && SDDC_CMD=/work/venv/bin/sddc PYTHONDONTWRITEBYTECODE=1 \\
  /work/venv/bin/python -m pytest /hidden -q -p no:cacheprovider --junitxml /work/junit.xml || true
"""


def requirement_map(task: Path) -> tuple[dict[str, str], list[str]]:
    """test-name prefix → R id, and the R ids scored by audit."""
    tests, audits = {}, []
    for line in (task / "requirements.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (R\d+) \|.*\| (.*) \|$", line)
        if not m:
            continue
        rid, scored = m.groups()
        if "audit" in scored:
            audits.append(rid)
        for prefix in re.findall(r"`(test_[a-z0-9_]+)\*`", scored):
            tests[prefix] = rid
    return tests, audits


def junit_results(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        state = "passed"
        for child in case:
            if child.tag in ("failure", "error"):
                state = "failed"
            elif child.tag == "skipped":
                state = "skipped"
        out[case.get("name")] = state
    return out


def referenced_ids(ws: Path) -> dict[str, set[str]]:
    """Spec ids the agent wrote down: `# spec:` marks in code, and any id in its notes."""
    marks, mentioned = set(), set()
    ident = r"(?:N-\d{6}|AC-\d+\.\d+|CT-\d+\.\d+)"
    for path in ws.rglob("*"):
        if not path.is_file() or "spec" in path.relative_to(ws).parts[:1] or path.suffix not in (".py", ".md", ".toml", ".txt"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"#\s*spec:\s*([^\n]+)", text):
            marks |= set(re.findall(ident, m.group(1)))
        mentioned |= set(re.findall(ident, text))
    return {"spec_marks": marks, "mentioned": mentioned}


def f1_checklist_ids(spec: Path) -> set[str]:
    checklist = spec / "CHECKLIST.md"
    if not checklist.exists():
        return set()
    ids, inside = set(), False
    for line in checklist.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Pack"):
            inside = "f1-ingest" in line
        elif inside and line.startswith("- [ ] "):
            ids.add(line.split()[3])
    return ids


def f1_labels(task: Path) -> set[str]:
    text = (task / "requirements.md").read_text(encoding="utf-8")
    return set(re.findall(r"(?:AC|CT)-1\.\d+", text))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--task", type=Path, required=True)
    args = ap.parse_args()
    run, task = args.run.expanduser().resolve(), args.task.resolve()
    score_dir = run / "score"
    if score_dir.exists():
        shutil.rmtree(score_dir)
    (score_dir / "ws").mkdir(parents=True)
    shutil.copytree(run / "workspace", score_dir / "ws", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".venv", "venv", "__pycache__", ".pytest_cache"))
    proc = subprocess.run([*bwrap_argv(score_dir, score_dir, with_claude=False,
                                       extra_ro={str(task / "hidden_tests"): "/hidden"}),
                           "sh", "-c", SCRIPT], capture_output=True, text=True, timeout=1800)
    (score_dir / "pytest.out").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode != 0 or not (score_dir / "junit.xml").exists():       # fail loud, never a silent 0
        reason = "the agent's package did not install" if "PIP_FAILED" in proc.stdout else \
            f"the sandbox or the test run failed (exit {proc.returncode}): {(proc.stderr or proc.stdout).strip()[-300:]}"
        (score_dir / "score.json").write_text(json.dumps({"error": reason}, indent=1), encoding="utf-8")
        print(f"score: NOT SCORED — {reason}", file=sys.stderr)
        return 3 if "PIP_FAILED" in proc.stdout else 4

    tests, audits = requirement_map(task)
    results = junit_results(score_dir / "junit.xml")
    by_req: dict[str, list[str]] = {}
    for name, state in results.items():
        rid = next((r for prefix, r in tests.items() if name.startswith(prefix)), "unmapped")
        by_req.setdefault(rid, []).append(state)
    req_state = {rid: "passed" if all(s == "passed" for s in states) else "failed"
                 for rid, states in sorted(by_req.items())}
    refs = referenced_ids(score_dir / "ws")
    labels = f1_labels(task)
    checklist = f1_checklist_ids(run / "workspace" / "spec")
    ws = run / "workspace"
    score = {
        "install": "ok",
        "hidden_tests": {"passed": sum(s == "passed" for s in results.values()),
                         "failed": sum(s == "failed" for s in results.values()),
                         "total": len(results)},
        "requirements_by_test": {"passed": sum(v == "passed" for v in req_state.values() if v),
                                 "of": len([r for r in req_state if r != "unmapped"]),
                                 "detail": req_state},
        "requirements_by_audit": {rid: "to be audited" for rid in audits},
        "f1_labels_mentioned": {"count": len(refs["mentioned"] & labels), "of": len(labels)},
        "spec_marks": len(refs["spec_marks"]),
        "f1_checklist_ids_mentioned": ({"count": len(refs["mentioned"] & checklist), "of": len(checklist)}
                                       if checklist else None),
        "deliverables": {name: (ws / name).exists()
                         for name in ("pyproject.toml", "OPEN_QUESTIONS.md", "IMPLEMENTATION_NOTES.md")},
        "tests": results,
    }
    (score_dir / "score.json").write_text(json.dumps(score, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in score.items() if k not in ("tests",)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
