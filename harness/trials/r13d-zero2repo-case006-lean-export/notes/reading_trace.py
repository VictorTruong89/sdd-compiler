"""Reading trace and token figures of saved runs, from their transcripts only (no model call).

    python3 notes/reading_trace.py runs/<run_id> [../r13c-zero2repo-3cases/runs/<run_id> ...]

For each run: Claude Code's turns and cost (`claude-code.txt` result line); per model request (session
JSONL, deduplicated by message id) the context = input + cache write + cache read; the context entering the
request with the largest output (in every round-13c run, the planning request after the spec was read); peak; sums of cache read, cache write, output; the
largest single output and its stop reason; then every tool call that touches the spec, in order.
Token figures are the transcripts' own `usage` fields; nothing is estimated.
"""
import json
import re
import sys
import tarfile
import tempfile
from pathlib import Path


def load(run: Path, tmp: Path):
    with tarfile.open(run / "agent.tgz") as tar:
        tar.extractall(tmp, filter="data")
    session = next(tmp.rglob("agent/sessions/projects/-app/*.jsonl"))
    result = [json.loads(x) for x in next(tmp.rglob("agent/claude-code.txt")).read_text().splitlines()
              if '"type":"result"' in x][-1]
    return session, result


SPEC_WORDS = re.compile(r"/app/spec|\bspec/|packs|CHECKLIST|MAP\.md|\.md\b")


def is_spec_read(name: str, args: dict) -> bool:
    """A Read of anything but code (spec files, saved outputs, extracts in /tmp), or a shell command
    naming spec files that does not write code."""
    if name == "Read":
        path = args.get("file_path", "")
        return not (path.startswith(("/app/src", "/app/tests")) or path.endswith(".py"))
    command = args.get("command", "") if name == "Bash" else ""
    return bool(SPEC_WORDS.search(command)) and "/app/src" not in command and "cat >" not in command


def trace(run: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        session, result = load(run, Path(tmp))
        usage, order, calls, results = {}, [], [], {}
        for line in session.read_text().splitlines():
            d = json.loads(line)
            if d.get("type") == "assistant":
                m = d["message"]
                if m["id"] not in usage:
                    order.append(m["id"])
                usage[m["id"]] = (m.get("usage") or {}, m.get("stop_reason"))
                for c in m["content"]:
                    if c.get("type") == "tool_use":
                        calls.append((len(order), c["id"], c["name"], c["input"]))
            elif d.get("type") == "user" and isinstance(d["message"]["content"], list):
                for x in d["message"]["content"]:
                    if x.get("type") == "tool_result":
                        content = x.get("content")
                        if isinstance(content, list):
                            content = "".join(y.get("text", "") for y in content if isinstance(y, dict))
                        results[x["tool_use_id"]] = content or ""
    ctx, sums = [], [0, 0, 0]
    for mid in order:
        u = usage[mid][0]
        ctx.append(u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                   + u.get("cache_read_input_tokens", 0))
        sums[0] += u.get("cache_read_input_tokens", 0)
        sums[1] += u.get("cache_creation_input_tokens", 0)
        sums[2] += u.get("output_tokens", 0)
    spec = [(t, n, i) + (results.get(cid, ""),) for t, cid, n, i in calls if is_spec_read(n, i)]
    big = max(range(len(order)), key=lambda k: usage[order[k]][0].get("output_tokens", 0))
    print(f"## {run.name}")
    print(f"turns {result['num_turns']} · requests {len(order)} · $ est. {result['total_cost_usd']:.4f}")
    print(f"context: request 1 {ctx[0]} · entering the largest-output request {ctx[big]} · peak {max(ctx)}"
          f" · last {ctx[-1]}")
    print(f"sum cache read {sums[0]} · sum cache write {sums[1]} · sum output {sums[2]}")
    print(f"largest output: request {big + 1}, {usage[order[big]][0].get('output_tokens')} tokens, "
          f"stop {usage[order[big]][1]}")
    print("spec reads (request: tool, argument, result chars):")
    for t, n, i, r in spec:
        arg = f"{i.get('file_path')} offset={i.get('offset')} limit={i.get('limit')}" if n == "Read" \
            else repr(i.get("command", "")[:140])
        saved = " [saved to file]" if "persisted-output" in r else ""
        print(f"  {t:3d} {n} {arg} → {len(r)}{saved}")
    print()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        trace(Path(arg))
