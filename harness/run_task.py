"""Run one coding-agent trial: one task, one spec format, one model — sandboxed, capped, logged.

    python run_task.py --task tasks/f1-ingest --format export --model sonnet --budget-usd 10
    python run_task.py ... --dry-run      # prepare and probe the sandbox; no model call

Writes a durable run directory under --out (default ~/sddc-runs/study-runs):
    <run>/workspace/        what the agent built (spec/ holds its inputs)
    <run>/transcript.jsonl  Claude Code's stream-json output, verbatim
    <run>/run.json          configuration, versions, exit, cost, turns, time, contamination audit

Every `$` is Claude Code's own `total_cost_usd`: an estimated API-equivalent on the owner's
subscription, never "cost" or "spend" without that label (build-plan I-82).
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sandbox import CLAUDE_IN, WORK_IN, bwrap_argv  # noqa: E402


def copy_inputs(task: Path, fmt: str, spec_dir: Path) -> tuple[str, list[str]]:
    config = json.loads((task / "inputs.json").read_text(encoding="utf-8"))
    entry = config["formats"][fmt]
    source = Path(entry["source"]).expanduser()
    copied = []
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source).as_posix()
        if path.is_file() and any(fnmatch.fnmatch(rel, pattern) for pattern in entry["include"]):
            target = spec_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            copied.append(rel)
    missing = [p for p in entry["include"] if "*" not in p and p not in copied]
    if missing:
        raise SystemExit(f"harness: inputs missing from {source}: {', '.join(missing)}")
    return entry["spec_line"], copied


#: The agent's whole tool set, the same for every format. No web tools: the agent could otherwise
#: search for this project's repository and copy it (found on the first, aborted run, 2026-09-30).
TOOLS = "Bash,Read,Write,Edit"


def claude_argv(prompt: str, model: str, budget: float) -> list[str]:
    return [CLAUDE_IN, "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose",
            "--max-budget-usd", f"{budget:.2f}", "--permission-mode", "bypassPermissions",
            "--no-session-persistence", "--strict-mcp-config", "--tools", TOOLS]


def probe(run_dir: Path, work: Path) -> dict:
    """No model call: what the sandbox can and cannot see."""
    checks = {
        "home_hidden": f"test ! -e {Path.home()}",
        "runs_hidden": f"test ! -e {Path.home() / 'sddc-runs'}",
        "spec_visible": f"test -d {WORK_IN}/spec",
        "claude_runs": f"{CLAUDE_IN} --version",
        "python": "python3 --version",
        "no_api_key": 'test -z "$ANTHROPIC_API_KEY"',
    }
    out = {}
    for name, command in checks.items():
        r = subprocess.run([*bwrap_argv(run_dir, work), "sh", "-c", command],
                           capture_output=True, text=True, timeout=60)
        out[name] = {"ok": r.returncode == 0, "output": (r.stdout + r.stderr).strip()[:200]}
    return out


def audit(transcript: Path) -> list[str]:
    """Tool calls that reached for a path outside the sandbox's view of the task (contamination)."""
    # Host paths only: the spec itself names the package `sdd_compiler` / `sdd-compiler`, so the bare
    # project name is not evidence (a false positive on the first run, 2026-09-30).
    suspicious = re.compile(re.escape(str(Path.home())) + r"|sddc-runs|hidden_tests|Workspace/")
    hits = []
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message") if isinstance(event, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                text = json.dumps(block.get("input"))
                if suspicious.search(text):
                    hits.append(text[:300])
    return hits


def summarise(transcript: Path) -> dict:
    init, result = {}, {}
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
        if event.get("type") == "result":
            result = event
    return {"model_reported": init.get("model"), "claude_code_version": init.get("claude_code_version"),
            "result_subtype": result.get("subtype"), "is_error": result.get("is_error"),
            "num_turns": result.get("num_turns"), "duration_ms": result.get("duration_ms"),
            "est_api_equivalent_usd": result.get("total_cost_usd"), "usage": result.get("usage")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", type=Path, required=True)
    ap.add_argument("--format", required=True, choices=("markdown", "export"))
    ap.add_argument("--model", required=True)
    ap.add_argument("--budget-usd", type=float, required=True,
                    help="ceiling in estimated API-equivalent $ (claude --max-budget-usd)")
    ap.add_argument("--timeout-s", type=int, default=3600)
    ap.add_argument("--out", type=Path, default=Path.home() / "sddc-runs" / "study-runs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    task = args.task.resolve()
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = args.out.expanduser() / f"{task.name}--{args.format}--{args.model}--{stamp}"
    work = run_dir / "workspace"
    (work / "spec").mkdir(parents=True)
    spec_line, copied = copy_inputs(task, args.format, work / "spec")
    prompt = (task / "task.md").read_text(encoding="utf-8").replace("{SPEC_LINE}", spec_line)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    record = {"task": task.name, "format": args.format, "model_requested": args.model,
              "budget_usd": args.budget_usd, "timeout_s": args.timeout_s, "inputs": copied,
              "argv": claude_argv("<prompt.md>", args.model, args.budget_usd),
              "probe": probe(run_dir, work)}
    failed = [k for k, v in record["probe"].items() if not v["ok"]]
    if failed:
        record["error"] = f"sandbox probe failed: {', '.join(failed)}"
    if args.dry_run or failed:
        (run_dir / "run.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
        print(json.dumps(record["probe"], indent=1))
        print(f"{'dry run' if not failed else 'STOPPED'}: {run_dir}")
        return 0 if not failed else 4

    transcript = run_dir / "transcript.jsonl"
    started = time.time()
    with transcript.open("w", encoding="utf-8") as handle:
        try:
            proc = subprocess.run([*bwrap_argv(run_dir, work), *claude_argv(prompt, args.model, args.budget_usd)],
                                  stdout=handle, stderr=subprocess.PIPE, text=True, timeout=args.timeout_s)
            record["exit_code"], record["stderr"] = proc.returncode, proc.stderr[-4000:]
        except subprocess.TimeoutExpired:
            record["exit_code"], record["stderr"] = None, f"wall-clock timeout after {args.timeout_s} s"
    record["wall_s"] = round(time.time() - started, 1)
    record.update(summarise(transcript))
    record["contamination"] = audit(transcript)
    (run_dir / "run.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(json.dumps({k: record.get(k) for k in ("exit_code", "result_subtype", "num_turns", "wall_s",
                                                  "est_api_equivalent_usd", "contamination")}, indent=1))
    print(run_dir)
    return 0 if record["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
