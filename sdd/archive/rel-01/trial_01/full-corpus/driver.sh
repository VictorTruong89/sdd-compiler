#!/usr/bin/env bash
# R18 round driver: run compile rounds until the check phase completes (HANDOVER §3).
# Exit 5 → next round. Exit 6 → sleep until the reset the message names (+5 min). Other → stop.
set -u
cd ~/sddc-runs/full-corpus
export PYTHONPATH=/home/victor/Workspace/sdd-compiler/src
MEAS=/home/victor/Workspace/sdd-compiler/sdd/design/rel01_design/measurements
log() { echo "$(date -Is) $*" | tee -a driver.log; }

# Let a round already in flight finish first.
while [ -f round-11.start ] && [ ! -f round-11.exit ]; do sleep 30; done

record() {   # $1 = round number; prints the summary line, copies the JSON
  local n=$1
  cp "round-$n.json" "$MEAS/R18_round$n.json" 2>/dev/null
  python - "round-$n.json" <<'PY' 2>/dev/null
import json, sys
d = json.load(open(sys.argv[1])); c = d.get('conflicts') or {}
print(f"pending={d.get('pending')} completed={d.get('completed')} failed={d.get('failed')} "
      f"calls={d.get('model_calls')} usd={d.get('cost_usd')} judged={c.get('pairs_judged')} "
      f"replayed={c.get('pairs_replayed')} unjudged={c.get('unjudged')} failed2={c.get('unjudged_failed')} "
      f"suppressed={c.get('suppressed')} opened={c.get('opened')} open={c.get('open')} "
      f"incomplete={c.get('incomplete')} stopped={c.get('stopped')}")
PY
}

n=11
code=$(sed -n 's/exit=//p' round-11.exit)
while true; do
  log "round $n exit=$code $(record $n)"
  case "$code" in
    0|3)
      done_=$(python -c "import json;d=json.load(open('round-$n.json'));c=d.get('conflicts') or {};print(int(c.get('unjudged',1)==0 and not c.get('incomplete')))" 2>/dev/null)
      if [ "$done_" = "1" ]; then log "DONE: check phase complete after round $n"; exit 0; fi
      log "exit $code but check not complete — continuing" ;;
    5) ;;
    6)
      reset=$(grep -o 'resets [0-9:apm]*' "round-$n.err" "round-$n.json" 2>/dev/null | head -1 | awk '{print $2}')
      target=$(date -d "$reset" +%s 2>/dev/null || echo $(( $(date +%s) + 3600 )))
      now=$(date +%s); [ "$target" -le "$now" ] && target=$(( target + 86400 ))
      [ -z "$reset" ] && target=$(( now + 3600 ))
      log "session limit; sleeping until $(date -d @$((target + 300)) -Is)"
      sleep $(( target + 300 - now )) ;;
    *) log "STOP: unexpected exit $code — see round-$n.err"; exit 1 ;;
  esac
  n=$((n + 1))
  date -Is > "round-$n.start"
  timeout 7200 python -m sdd_compiler compile --json > "round-$n.json" 2> "round-$n.err"
  code=$?
  echo "exit=$code" > "round-$n.exit"; date -Is > "round-$n.end"
done
