#!/bin/bash
# v2 (2026-10-16): the same, after the compiler change of rel02 D26 (F5 D14, F3 D41, D42), into work/compile-planted-v2.
# Incremental compile of the planted case006 in a copy of round 13c's finished store
# (work/compile-planted: .sdd/ copied from ../r13c-zero2repo-3cases/work/compile-case006, then the
# planted Markdown copied over sdd/specs/ and re-ingested: 7 blocks changed, 458 unchanged).
# Haiku via Claude Code on the owner's subscription (approved 2026-10-16). Passes until complete.
set -u
D="$(cd "$(dirname "$0")/../work/compile-planted-v2" && pwd)"; cd "$D" || exit 1
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
