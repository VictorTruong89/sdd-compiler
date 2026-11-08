"""Cost and token breakdown per run, read from the agent's own logs (added 2026-11-08).

For each run under ../runs/, reads from agent.tgz:
  - claude-code.txt: Claude Code's final record (num_turns, total_cost_usd, usage), and
  - projects/-app/*.jsonl: the per-response `usage` the API returned (last record per message id).
Prints both totals side by side so they can be checked against each other, the peak context
(largest per-response input incl. cache), and API time. With --fit, fits per-token list prices per
model by least squares on (cache write, cache read, output) and prints the largest residual.

Usage: python3 notes/cost_breakdown.py [--fit]     (run from the trial folder)
"""
import glob
import json
import os
import sys
import tarfile

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")


def read_run(path):
    final, per_msg = None, {}
    with tarfile.open(os.path.join(path, "agent.tgz")) as tar:
        for m in tar.getmembers():
            if m.name.endswith("claude-code.txt"):
                for line in tar.extractfile(m).read().decode().splitlines():
                    if '"total_cost_usd"' in line:
                        final = json.loads(line)
            elif "/projects/-app/" in m.name and m.name.endswith(".jsonl"):
                for line in tar.extractfile(m).read().decode().splitlines():
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = o.get("message")
                    if isinstance(msg, dict) and msg.get("usage") and msg.get("id"):
                        per_msg[msg["id"]] = msg["usage"]
    if final is None:
        raise SystemExit(f"no final record with total_cost_usd in {path}")
    return final, per_msg


def main():
    rows = {}
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    print("run\tturns\tcost_usd_est\tcache_write\tcache_read\toutput\tthinking\tsum_matches_final\tpeak_ctx\tapi_min")
    for path in sorted(glob.glob(os.path.join(RUNS, "*"))):
        name = os.path.basename(path)
        final, per_msg = read_run(path)
        u = final["usage"]
        summed = {k: sum(x.get(k, 0) for x in per_msg.values()) for k in keys}
        match = all(summed[k] == u[k] for k in keys)
        peak = max(x["input_tokens"] + x["cache_creation_input_tokens"] + x["cache_read_input_tokens"]
                   for x in per_msg.values())
        thinking = u.get("output_tokens_details", {}).get("thinking_tokens", 0)
        rows[name] = [u[k] for k in keys] + [final["total_cost_usd"]]
        print(f"{name}\t{final['num_turns']}\t{final['total_cost_usd']:.4f}\t{u[keys[1]]}\t{u[keys[2]]}"
              f"\t{u[keys[3]]}\t{thinking}\t{match}\t{peak}\t{final['duration_api_ms'] / 60000:.1f}")
    if "--fit" in sys.argv:
        import numpy as np
        for model in sorted({n.split("-")[1] for n in rows}):
            ks = [k for k in rows if k.split("-")[1] == model]
            a = np.array([rows[k][1:4] for k in ks], float)
            b = np.array([rows[k][4] for k in ks])
            p = np.linalg.lstsq(a, b, rcond=None)[0]
            resid = np.abs(a @ p - b).max()
            print(f"fit {model}: $/MTok cache_write {p[0]*1e6:.4f} cache_read {p[1]*1e6:.4f} "
                  f"output {p[2]*1e6:.4f}; largest residual ${resid:.6f}")


if __name__ == "__main__":
    main()
