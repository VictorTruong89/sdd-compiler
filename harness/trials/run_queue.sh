#!/bin/bash
# Trial driver: runs one trial's queue through Harbor, one run at a time, unattended (no Claude session).
#
#   cd harness/trials
#   nohup bash run_queue.sh <trial-dir>        >> <trial-dir>/run_queue.log 2>&1 &
#   nohup bash run_queue.sh <trial-dir> --one  >> <trial-dir>/run_queue.log 2>&1 &   # next row only
#   touch <trial-dir>/STOP                                                           # stop between runs
#
# <trial-dir>/queue.tsv, tab-separated, one row per run:
#   run_id  task  model  status  job  attempts  last_message
# task is a Harbor task folder relative to <trial-dir> (normally work/tasks/<name>); model is a Harbor
# model id (anthropic/claude-haiku-5-5 ...). status: pending | running | done | limited | failed | hold.
# A `done` row is never rerun. Conditions come from <trial-dir>/trial.env (CLAUDE_VERSION, BUDGET_USD,
# DISALLOW, RUN_TIMEOUT) so they are recorded with the trial.
# Each run's job goes to <trial-dir>/work/jobs/<trial>-<run_id>; its files are copied to runs/<run_id>/.
# Spends model calls (the owner's subscription): start it only with the owner's go-ahead.
set -u
T="$(cd "${1:?usage: run_queue.sh <trial-dir> [--one]}" && pwd)"
ONE=0; [ "${2:-}" = "--one" ] && ONE=1
TRIAL="$(basename "$T")"
QUEUE="$T/queue.tsv"
KIT="$(cd "$(dirname "$0")" && pwd)"
H="$KIT/../platforms/harbor/download/.venv/bin/harbor"
TOKEN_FILE="$HOME/.config/sdd-compiler/claude-oauth.env"
CLAUDE_VERSION=2.1.296
BUDGET_USD=10
DISALLOW=Task,CronCreate,CronDelete,CronList,DesignSync,EnterWorktree,ExitWorktree,ListAgents,NotebookEdit,RemoteTrigger,ReportFindings,ScheduleWakeup,SendMessage,Skill,TaskStop,ToolSearch,WebFetch,WebSearch,Workflow
RUN_TIMEOUT=9000
GAP=120
PROBE_EVERY=1800
USAGE_FIVE_HOUR_MAX=0.90    # pause new runs at this share of the 5-hour window (rate_limit_event)
USAGE_SEVEN_DAY_MAX=0.95    # and of the 7-day window
MAX_ATTEMPTS=3
# shellcheck disable=SC1091
[ -f "$T/trial.env" ] && source "$T/trial.env"
LIMIT_RE='usage limit|rate.?limit|limit reached|hit your limit|out of (extra )?usage|resets? (at )?[0-9]|status.{0,4}429'

export HARBOR_TELEMETRY=0 CLAUDE_FORCE_OAUTH=1
unset ANTHROPIC_API_KEY
# shellcheck disable=SC1090
source "$TOKEN_FILE"     # never echo it
mkdir -p "$T/work/jobs" "$T/runs"
# One driver per trial: a second start exits at once (added 2026-10-14 after a restart overlapped one
# still sleeping in its gap). Do not edit this script while a driver is running: bash reads it as it goes.
exec 9> "$T/work/driver.lock"
flock -n 9 || { printf "%s\tbusy\tanother driver holds $T/work/driver.lock; exiting\n" "$(date -Is)"; exit 3; }

log() { printf '%s\t%s\n' "$(date -Is)" "$*"; }
# columns: 1 run_id 2 task 3 model 4 status 5 job 6 attempts 7 last_message
get_field() { awk -F'\t' -v p="$1" -v c="$2" '$1==p {print $c}' "$QUEUE"; }
set_row() {   # run_id status job attempts message
  local msg; msg="$(printf '%s' "$5" | tr '\t\n\r' '   ' | cut -c1-300)"
  awk -F'\t' -v OFS='\t' -v p="$1" -v s="$2" -v j="$3" -v a="$4" -v m="$msg" \
    '$1==p {$4=s; $5=j; $6=a; $7=m} {print}' "$QUEUE" > "$QUEUE.tmp" && mv "$QUEUE.tmp" "$QUEUE"
}
next_row() { awk -F'\t' 'NR>1 && ($4=="pending" || $4=="limited") {print $1; exit}' "$QUEUE"; }

cleanup_docker() {   # only Harbor's own trial containers and networks (<task>__<id>__...)
  docker ps -a --filter status=exited --filter status=created --format '{{.Names}}' | grep -E '__[A-Za-z0-9]+__' \
    | xargs -r docker rm -f > /dev/null 2>&1
  docker network ls --format '{{.Name}}' | grep -E '__[A-Za-z0-9]+__env_default$' \
    | xargs -r docker network rm > /dev/null 2>&1
}

probe() {
  local dir out rc; dir="$(mktemp -d)"
  out="$(cd "$dir" && timeout 300 env -u ANTHROPIC_API_KEY claude -p "reply ok" --model haiku --max-turns 1 \
         --output-format json 2>&1)"; rc=$?
  rm -rf "$dir"
  if [ $rc -eq 0 ] && printf '%s' "$out" | python3 -c 'import json,sys; sys.exit(json.loads(sys.stdin.read()).get("is_error") is not False)' 2>/dev/null
  then return 0; fi
  log "probe" "not yet: $(printf '%s' "$out" | tr '\n\t' '  ' | cut -c1-200)"
  return 1
}

wait_for_reset() {
  local msg="$1" epoch="" when="" tz=""
  epoch="$(printf '%s' "$msg" | grep -oE '\|[0-9]{10}' | head -1 | tr -d '|')"
  if [ -z "$epoch" ]; then
    when="$(printf '%s' "$msg" | grep -oiE 'resets? (at )?[0-9]{1,2}(:[0-9]{2})? ?(am|pm)?( \([A-Za-z_/+-]+\))?' | head -1 \
            | sed -E 's/^[Rr]esets? (at )?//')"
    if [ -n "$when" ]; then
      tz="$(printf '%s' "$when" | grep -oE '\(([^)]+)\)' | tr -d '()')"
      when="$(printf '%s' "$when" | sed -E 's/ ?\([^)]*\)//')"
      epoch="$( if [ -n "$tz" ]; then TZ="$tz" date -d "$when" +%s; else date -d "$when" +%s; fi 2>/dev/null || true)"
      [ -n "$epoch" ] && [ "$epoch" -lt "$(date +%s)" ] && epoch=$((epoch + 86400))
    fi
  fi
  if [ -n "$epoch" ]; then
    log "limit" "reset parsed: $(date -d "@$epoch" -Is); sleeping until 5 min after"
    while [ "$(date +%s)" -lt $((epoch + 300)) ]; do [ -f "$T/STOP" ] && return 1; sleep 60; done
    return 0
  fi
  log "limit" "no reset time in the message; probing every $PROBE_EVERY s"
  while :; do
    local t=0; while [ $t -lt "$PROBE_EVERY" ]; do [ -f "$T/STOP" ] && return 1; sleep 60; t=$((t + 60)); done
    probe && return 0
  done
}

save_run() {   # run_id trial_dir job_dir
  local out="$T/runs/$1" v="$2/verifier"
  rm -rf "$out"; mkdir -p "$out"
  cp "$2/result.json" "$out/result.json" 2>/dev/null
  # every small verifier file (rewards, reports, junit, logs); the agent's workspace archive as app.tgz
  find "$v" -maxdepth 1 -type f -size -20M -exec cp {} "$out/" \; 2>/dev/null
  cp "$v/agent_files/app.tgz" "$out/app.tgz" 2>/dev/null
  # the job folder without .claude.json, settings, shell snapshots, backups or setup
  tar -czf "$out/agent.tgz" -C "$(dirname "$3")" \
    --exclude='*/agent/setup' --exclude='*/agent/sessions/.claude.json' --exclude='*/agent/sessions/backups' \
    --exclude='*/agent/sessions/shell-snapshots' --exclude='*/agent/sessions/session-env' \
    --exclude='*/agent/sessions/policy-limits.json*' --exclude='*/agent/sessions/remote-settings.json' \
    --exclude='*/verifier/agent_files' "$(basename "$3")"
}

usage_guard() {   # claude-code.txt of the last run: log the subscription's usage; wait if near a limit
  local cc="$1" line
  [ -f "$cc" ] || return 0
  line="$(grep '"type":"rate_limit_event"' "$cc" | tail -1 | python3 -c '
import json, sys
try:
    w = json.loads(sys.stdin.read())["rate_limit_info"].get("unifiedWindows") or {}
except Exception:
    sys.exit()
f, s = w.get("five_hour") or {}, w.get("seven_day") or {}
print(f.get("utilization", ""), f.get("resetsAt", ""), s.get("utilization", ""), s.get("resetsAt", ""))')"
  [ -z "$line" ] && return 0
  read -r FU FR SU SR <<< "$line"
  log "usage" "five_hour $FU (resets $(date -d "@$FR" -Is 2>/dev/null)) seven_day $SU (resets $(date -d "@$SR" -Is 2>/dev/null))"
  local until=""
  python3 -c "import sys; sys.exit(0 if float('${FU:-0}' or 0) >= $USAGE_FIVE_HOUR_MAX else 1)" && until="$FR"
  python3 -c "import sys; sys.exit(0 if float('${SU:-0}' or 0) >= $USAGE_SEVEN_DAY_MAX else 1)" && until="$SR"
  [ -z "$until" ] && return 0
  log "limit" "usage near the limit; pausing new runs until $(date -d "@$until" -Is) + 5 min"
  while [ "$(date +%s)" -lt $((until + 300)) ]; do [ -f "$T/STOP" ] && return 1; sleep 60; done
}

log "start" "trial $TRIAL, claude $CLAUDE_VERSION, budget $BUDGET_USD, one=$ONE"
while :; do
  [ -f "$T/STOP" ] && { log "stop" "STOP file found; exiting between runs"; break; }
  R="$(next_row)"
  [ -z "$R" ] && { log "end" "no pending or limited row left"; break; }
  TASK="$T/$(get_field "$R" 2)"; MODEL="$(get_field "$R" 3)"
  ATT="$(get_field "$R" 6)"; ATT=$((${ATT:-0} + 1))
  JOB="$TRIAL-$R"; JOBDIR="$T/work/jobs/$JOB"
  if [ -e "$JOBDIR" ]; then
    mv "$JOBDIR" "$JOBDIR.attempt$((ATT - 1))-$(date +%Y%m%dT%H%M%S)"
    log "kept" "$R earlier job renamed (attempt $((ATT - 1)))"
  fi
  set_row "$R" running "$JOB" "$ATT" ""
  log "run" "$R attempt $ATT model $MODEL task $(basename "$TASK")"
  T0=$(date +%s)
  ( cd "$T/work" && timeout "$RUN_TIMEOUT" env -u ANTHROPIC_API_KEY "$H" run -p "$TASK" -a claude-code -m "$MODEL" \
      --ak version="$CLAUDE_VERSION" --ak max_budget_usd="$BUDGET_USD" --ak disallowed_tools="$DISALLOW" \
      -o jobs --job-name "$JOB" ) > "$T/runs/.harbor-$R.out" 2>&1
  RC=$?
  log "harbor" "$R exit $RC after $(( $(date +%s) - T0 )) s"

  if [ -d "$JOBDIR" ] && grep -rlq "sk-ant-oat01" "$JOBDIR" 2>/dev/null; then
    set_row "$R" failed "$JOB" "$ATT" "TOKEN FOUND IN JOB FOLDER: queue stopped"
    log "TOKEN" "$R: token string found in the job folder; queue stopped. Do not share the folder."
    exit 2
  fi

  TD="$(ls -d "$JOBDIR"/*__*/ 2>/dev/null | head -1)"; TD="${TD%/}"
  CC="$TD/agent/claude-code.txt"
  RES="$(grep '"type":"result"' "$CC" 2>/dev/null | tail -1)"
  read -r IS_ERR TURNS COST SUB < <(printf '%s' "$RES" | python3 -c '
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(str(d.get("is_error")).lower(), d.get("num_turns", 0), d.get("total_cost_usd", ""), d.get("subtype", ""))
except Exception:
    print("noresult 0 - -")')
  EXC="$(python3 -c '
import json, sys
try:
    e = json.load(open(sys.argv[1])).get("exception_info")
    print("" if not e else json.dumps(e)[:400])
except Exception:
    print("")' "$TD/result.json" 2>/dev/null)"
  REWARD="$(cat "$TD/verifier/reward.json" 2>/dev/null)"

  if [ -n "$REWARD" ] && [ -z "$EXC" ] && { [ "$IS_ERR" = "false" ] || [[ "$SUB" == error_max* ]]; }; then
    save_run "$R" "$TD" "$JOBDIR"
    NOTE=""; [ "$SUB" != "success" ] && NOTE="subtype $SUB"
    set_row "$R" done "$JOB" "$ATT" "$NOTE"
    log "done" "$R turns $TURNS cost_usd_est $COST reward $REWARD $NOTE"
  else
    MSG="$( { printf '%s\n' "$RES" | python3 -c 'import json,sys
try: d=json.loads(sys.stdin.read()); print(d.get("result",""), d.get("api_error_status") or "")
except Exception: pass'; printf '%s\n' "$EXC"; tail -n 30 "$CC" 2>/dev/null; tail -n 30 "$T/runs/.harbor-$R.out"; } \
      | grep -v '"status":"allowed"' | grep -iE "$LIMIT_RE" | head -1 | cut -c1-300)"
    if [ -n "$MSG" ]; then
      [ -d "$JOBDIR" ] && mv "$JOBDIR" "$JOBDIR.limited-$(date +%Y%m%dT%H%M%S)"
      set_row "$R" limited "$JOB" "$((ATT - 1))" "$MSG"
      log "limited" "$R turns $TURNS cost_usd_est $COST message: $MSG"
      cleanup_docker
      wait_for_reset "$MSG" || { log "stop" "STOP file found while waiting"; break; }
      continue
    fi
    TXT="$(printf '%s' "$RES" | python3 -c 'import json,sys
try: print(str(json.loads(sys.stdin.read()).get("result",""))[:150])
except Exception: pass')"
    WHY="rc $RC, is_error $IS_ERR, subtype $SUB, turns $TURNS, reward ${REWARD:-none}, exception ${EXC:-none}, result: ${TXT:-none}"
    if [ "$ATT" -ge "$MAX_ATTEMPTS" ]; then
      [ -d "$TD" ] && save_run "$R" "$TD" "$JOBDIR"
      set_row "$R" failed "$JOB" "$ATT" "$WHY"
      log "failed" "$R after $ATT attempts: $WHY"
    else
      set_row "$R" pending "$JOB" "$ATT" "$WHY"
      log "retry" "$R will be retried: $WHY"
    fi
  fi
  cleanup_docker
  usage_guard "$CC" || { log "stop" "STOP file found while pausing for usage"; break; }
  [ $ONE -eq 1 ] && { log "end" "--one: stopping after one run"; break; }
  sleep "$GAP"
done
