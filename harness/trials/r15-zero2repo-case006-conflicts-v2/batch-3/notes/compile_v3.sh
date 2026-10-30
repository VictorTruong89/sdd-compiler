#!/bin/bash
# v3 (2026-10-28, batch 3 / T1): the same as round 14's v2 replay, with the current compiler (F7 D17), into ../work/compile-v3.
# Store: ../../work/compile-v3 = .sdd/ and sdd/ of ../../../r13c-zero2repo-3cases/work/compile-case006, planted
# Markdown (../../work/spec-planted) over sdd/specs/, `sddc ingest` (7 changed, 458 unchanged), then
# .sdd/lock replaced by round 14's v2 lock so the same answers replay.
# Haiku via Claude Code on the owner's subscription (approved 2026-10-28). Passes until complete.
set -u
D="$(cd "$(dirname "$0")/../../work/compile-v3" && pwd)"; cd "$D" || exit 1
export PATH="/home/victor/.local/bin:/home/victor/anaconda3/bin:$PATH"
# shellcheck disable=SC1090
source "$HOME/.config/sdd-compiler/claude-oauth.env"; export CLAUDE_FORCE_OAUTH=1; unset ANTHROPIC_API_KEY
for n in 1 2 3 4 5 6 7 8; do
  sddc --json compile > "compile-$n.json" 2> "compile-$n.err"; rc=$?
  state="$(python3 - "compile-$n.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("bad"); sys.exit()
c = d.get("conflicts") or {}
done = not d.get("stopped") and not c.get("stopped") and not c.get("incomplete") and not d.get("failed")
print(("done" if done else "more"), "calls", d.get("model_calls"), "cost", d.get("cost_usd"), "failed", d.get("failed"),
      "stop", d.get("stopped") or c.get("stopped"), "reason", str(d.get("stop_reason") or c.get("stop_reason"))[:120])
PY
)"
  printf '%s\tpass %s exit %s %s\n' "$(date -Is)" "$n" "$rc" "$state" | tee -a compile.log
  case "$state" in done*) date -Is > DONE; exit 0 ;; bad*) sleep 600 ;; esac
done
date -Is > FAILED; exit 1
