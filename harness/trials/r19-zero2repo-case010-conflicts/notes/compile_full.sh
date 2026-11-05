#!/bin/bash
# Round 19, step 2: full compile of the planted case010 from a new store, with judging, using the
# current compiler unchanged. Copied from ../r17-zero2repo-case006-conflicts-24/notes/compile_full.sh;
# changes: case010, round 13c's case010 profile and lock (questions already answered word for word
# replay), the planted spec work/spec-planted, the store work/compile-full.
#   bash notes/compile_full.sh        (from the trial folder)
# Spends model calls: owner's go-ahead 2026-11-02 (round 19 request: one full compile).
set -u
CASE=case010
T="$(cd "$(dirname "$0")/.." && pwd)"
Z="$T/work/spec-planted"                       # round 19: the planted spec
D="$T/work/compile-full"
PROFILE="$T/../r13c-zero2repo-3cases/work/compile-case010/.sdd/profile.yaml"   # round 13c's case010 profile
MAX_PASSES=20; MAX_FAILS=6; WAIT_FAIL=1800
export PATH="/home/victor/.local/bin:/home/victor/anaconda3/bin:$PATH"   # claude (sddc backend) and sddc; cron gives a bare PATH
mkdir -p "$D"; cd "$D" || exit 1
exec 8> "$D/compile.lock"
flock -n 8 || exit 3                      # one compile per case
log() { printf '%s\t%s\n' "$(date -Is)" "$*" >> "$D/compile.log"; }
[ -f DONE ] && exit 0
# shellcheck disable=SC1090
source "$HOME/.config/sdd-compiler/claude-oauth.env"; export CLAUDE_FORCE_OAUTH=1; unset ANTHROPIC_API_KEY
if [ ! -d .sdd ]; then
  sddc init > init.out 2>&1 || { log "fail init"; exit 1; }
  cp "$PROFILE" .sdd/profile.yaml
  mkdir -p sdd/specs; cp "$Z"/*.md sdd/specs/
  rm -rf .sdd/lock; cp -r "$T/../r13c-zero2repo-3cases/work/compile-case010/.sdd/lock" .sdd/lock   # round 13c case010 answers replay where the question is the same
  sddc --json ingest > ingest.json 2> ingest.err || { log "fail ingest"; exit 1; }
  log "init+ingest $(python3 -c 'import json;d=json.load(open("ingest.json"));print({k:v for k,v in d.items() if not isinstance(v,(list,dict))})' 2>/dev/null)"
fi
fails=0
for _ in $(seq 1 $MAX_PASSES); do
  n=$(( $(ls compile-*.json 2>/dev/null | wc -l) + 1 ))
  log "pass $n start"
  sddc --json compile > "compile-$n.json" 2> "compile-$n.err"; rc=$?
  state="$(python3 - "compile-$n.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("bad"); sys.exit()
c = d.get("conflicts") or {}
done = not d.get("stopped") and not c.get("stopped") and not c.get("incomplete") and not d.get("failed")
# no progress (no call made) or failed blocks: most likely a usage limit; wait instead of looping
stall = not done and (not d.get("model_calls") or d.get("failed"))
reason = str(d.get("stop_reason") or c.get("stop_reason") or "")
limit = stall and ("limit" in reason.lower() or "429" in reason)
print(("done" if done else "limit" if limit else "stall" if stall else "more"), "calls", d.get("model_calls"), "cost", d.get("cost_usd"),
      "nodes", d.get("nodes_formed"), "pending", d.get("pending"), "failed", d.get("failed"),
      "stop", d.get("stopped") or c.get("stopped"), "unjudged", c.get("unjudged"),
      "contradicts", (c.get("by_relation") or {}).get("contradicts"))
PY
)"
  log "pass $n exit $rc $state"
  case "$state" in
    done*) date -Is > DONE; log "complete"; exit 0 ;;
    limit*)  # usage limit: wait for the reset named in the message (+5 min); not counted as a failure
           msg="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("stop_reason") or (d.get("conflicts") or {}).get("stop_reason") or "")' "compile-$n.json")"
           when="$(printf '%s' "$msg" | grep -oiE 'resets [0-9]{1,2}(:[0-9]{2})? ?(am|pm)( \([A-Za-z_/+-]+\))?' | head -1 | sed -E 's/^resets //I')"
           tz="$(printf '%s' "$when" | grep -oE '\(([^)]+)\)' | tr -d '()')"; when="$(printf '%s' "$when" | sed -E 's/ ?\([^)]*\)//')"
           epoch="$( { if [ -n "$tz" ]; then TZ="$tz" date -d "$when" +%s; else date -d "$when" +%s; fi; } 2>/dev/null)"
           [ -n "$epoch" ] && [ "$epoch" -lt "$(date +%s)" ] && epoch=$((epoch + 86400))
           [ -z "$epoch" ] && epoch=$(( $(date +%s) + WAIT_FAIL ))
           log "pass $n usage limit; waiting until $(date -d "@$((epoch + 300))" -Is) (not counted as a failure)"
           while [ "$(date +%s)" -lt $((epoch + 300)) ]; do sleep 60; done ;;
    bad*|stall*)  fails=$((fails + 1)); log "pass $n no JSON or no progress, waiting $WAIT_FAIL s ($(tail -c 300 "compile-$n.err" | tr '\n' ' '))"
           [ $fails -ge $MAX_FAILS ] && { log "stop: $fails failed passes"; date -Is > FAILED; exit 1; }
           sleep $WAIT_FAIL ;;
  esac
done
log "stop: $MAX_PASSES passes without completing"; date -Is > FAILED; exit 1
