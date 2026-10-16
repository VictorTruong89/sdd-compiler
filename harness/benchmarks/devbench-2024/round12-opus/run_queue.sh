#!/bin/bash
# Round 12 driver: runs the Opus queue one project at a time, unattended, without a Claude session.
#
#   cd harness/benchmarks/devbench-2024/round12-opus
#   nohup bash run_queue.sh        > run_queue.log 2>&1 &     # whole queue
#   nohup bash run_queue.sh --one  > run_queue.log 2>&1 &     # next row only (the pilot)
#   touch STOP                                                # stop cleanly before the next run
#
# Reads and rewrites queue.tsv (project, task, status, job, attempts, last_message).
# status: pending | running | done | limited | failed | hold (skipped). A `done` row is never rerun.
# Spends model calls (Opus, the owner's subscription): start it only with the owner's go-ahead.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DL="$HERE/../download"
QUEUE="$HERE/queue.tsv"
TOKEN_FILE="$HOME/.config/sdd-compiler/claude-oauth.env"
H="$HERE/../../../platforms/harbor/download/.venv/bin/harbor"
MODEL="anthropic/claude-opus-5-5"
DISALLOW=Task,CronCreate,CronDelete,CronList,DesignSync,EnterWorktree,ExitWorktree,ListAgents,NotebookEdit,RemoteTrigger,ReportFindings,ScheduleWakeup,SendMessage,Skill,TaskStop,ToolSearch,WebFetch,WebSearch,Workflow
RUN_TIMEOUT=7200        # agent 3600 s + build 900 s + verifier 900 s, with margin
GAP=120                 # seconds between runs
PROBE_EVERY=1800        # seconds between usage probes when no reset time is given
MAX_ATTEMPTS=3          # one run plus two retries for a non-limit failure
LIMIT_RE='usage limit|rate.?limit|limit reached|hit your limit|out of (extra )?usage|resets? (at )?[0-9]|status.{0,4}429'
ONE=0; [ "${1:-}" = "--one" ] && ONE=1

export HARBOR_TELEMETRY=0 CLAUDE_FORCE_OAUTH=1
unset ANTHROPIC_API_KEY
# shellcheck disable=SC1090
source "$TOKEN_FILE"     # never echo it

log() { printf '%s\t%s\n' "$(date -Is)" "$*"; }

# queue.tsv helpers: get_field <project> <col>, set_row <project> <status> <job> <attempts> <message>
get_field() { awk -F'\t' -v p="$1" -v c="$2" '$1==p {print $c}' "$QUEUE"; }
set_row() {
  local msg; msg="$(printf '%s' "$5" | tr '\t\n\r' '   ' | cut -c1-300)"
  awk -F'\t' -v OFS='\t' -v p="$1" -v s="$2" -v j="$3" -v a="$4" -v m="$msg" \
    '$1==p {$3=s; $4=j; $5=a; $6=m} {print}' "$QUEUE" > "$QUEUE.tmp" && mv "$QUEUE.tmp" "$QUEUE"
}
next_row() { awk -F'\t' 'NR>1 && ($3=="pending" || $3=="limited") {print $1; exit}' "$QUEUE"; }

cleanup_docker() {
  # Only Harbor's own trial containers and networks (named <task>__<id>__...), never anything else.
  docker ps -a --filter status=exited --filter status=created --format '{{.Names}}' | grep -E '__[A-Za-z0-9]+__' \
    | xargs -r docker rm -f > /dev/null 2>&1
  docker network ls --format '{{.Name}}' | grep -E '__[A-Za-z0-9]+__env_default$' \
    | xargs -r docker network rm > /dev/null 2>&1
  log "docker" "$(docker ps -a --format '{{.Names}}' | grep -cE '__[A-Za-z0-9]+__') harbor containers left"
}

probe() {   # 0 when the subscription answers again
  local dir out; dir="$(mktemp -d)"
  out="$(cd "$dir" && timeout 300 env -u ANTHROPIC_API_KEY claude -p "reply ok" --model haiku --max-turns 1 \
         --output-format json 2>&1)"; local rc=$?
  rm -rf "$dir"
  if [ $rc -eq 0 ] && printf '%s' "$out" | python3 -c 'import json,sys; sys.exit(json.loads(sys.stdin.read()).get("is_error") is not False)' 2>/dev/null
  then return 0; fi
  log "probe" "not yet: $(printf '%s' "$out" | tr '\n\t' '  ' | cut -c1-200)"
  return 1
}

wait_for_reset() {   # $1: the limit message
  local msg="$1" epoch="" when=""
  epoch="$(printf '%s' "$msg" | grep -oE '\|[0-9]{10}' | head -1 | tr -d '|')"
  if [ -z "$epoch" ]; then
    when="$(printf '%s' "$msg" | grep -oiE 'resets? (at )?[0-9]{1,2}(:[0-9]{2})? ?(am|pm)?( \([A-Za-z_/+-]+\))?' | head -1 \
            | sed -E 's/^[Rr]esets? (at )?//')"
    if [ -n "$when" ]; then
      local tz; tz="$(printf '%s' "$when" | grep -oE '\(([^)]+)\)' | tr -d '()')"
      when="$(printf '%s' "$when" | sed -E 's/ ?\([^)]*\)//')"
      epoch="$( if [ -n "$tz" ]; then TZ="$tz" date -d "$when" +%s; else date -d "$when" +%s; fi 2>/dev/null || true)"
      [ -n "$epoch" ] && [ "$epoch" -lt "$(date +%s)" ] && epoch=$((epoch + 86400))
    fi
  fi
  if [ -n "$epoch" ]; then
    log "limit" "reset parsed: $(date -d "@$epoch" -Is); sleeping until 5 min after"
    while [ "$(date +%s)" -lt $((epoch + 300)) ]; do [ -f "$HERE/STOP" ] && return 1; sleep 60; done
    return 0
  fi
  log "limit" "no reset time in the message; probing every $PROBE_EVERY s"
  while :; do
    local t=0; while [ $t -lt $PROBE_EVERY ]; do [ -f "$HERE/STOP" ] && return 1; sleep 60; t=$((t + 60)); done
    probe && return 0
  done
}

save_run() {   # $1 project, $2 trial dir, $3 job dir
  local out="$HERE/runs/$1" v="$2/verifier"
  rm -rf "$out"; mkdir -p "$out"
  cp "$2/result.json" "$out/result.json" 2>/dev/null
  for f in reward.json pytest.out junit-unit_tests.xml junit-acceptance_tests.xml; do cp "$v/$f" "$out/" 2>/dev/null; done
  cp "$v/agent_files/app.tgz" "$out/app.tgz" 2>/dev/null
  # The job folder as in evidence/: no .claude.json, settings, shell snapshots, backups or setup.
  tar -czf "$out/agent.tgz" -C "$(dirname "$3")" \
    --exclude='*/agent/setup' --exclude='*/agent/sessions/.claude.json' --exclude='*/agent/sessions/backups' \
    --exclude='*/agent/sessions/shell-snapshots' --exclude='*/agent/sessions/session-env' \
    --exclude='*/agent/sessions/policy-limits.json*' --exclude='*/agent/sessions/remote-settings.json' \
    "$(basename "$3")"
}

log "start" "queue $QUEUE, model $MODEL, one=$ONE"
while :; do
  [ -f "$HERE/STOP" ] && { log "stop" "STOP file found; exiting between runs"; break; }
  P="$(next_row)"
  [ -z "$P" ] && { log "end" "no pending or limited row left"; break; }
  TASK="$(get_field "$P" 2)"; ATT="$(get_field "$P" 5)"; ATT=$((${ATT:-0} + 1))
  JOB="r12-$P-markdown-opus-1"; JOBDIR="$DL/jobs/$JOB"
  if [ -e "$JOBDIR" ]; then   # keep an earlier partial job instead of overwriting it
    mv "$JOBDIR" "$JOBDIR.attempt$((ATT - 1))-$(date +%Y%m%dT%H%M%S)"
    log "kept" "$P earlier job renamed to $(basename "$JOBDIR").attempt$((ATT - 1))-*"
  fi
  set_row "$P" running "$JOB" "$ATT" ""
  log "run" "$P attempt $ATT job $JOB"
  T0=$(date +%s)
  ( cd "$DL" && timeout "$RUN_TIMEOUT" env -u ANTHROPIC_API_KEY "$H" run -p "$TASK" -a claude-code -m "$MODEL" \
      --ak version=2.1.296 --ak max_budget_usd=10 --ak disallowed_tools=$DISALLOW -o jobs --job-name "$JOB" ) \
      > "$HERE/runs/.harbor-$P.out" 2>&1
  RC=$?
  log "harbor" "$P exit $RC after $(( $(date +%s) - T0 )) s"

  if [ -d "$JOBDIR" ] && grep -rlq "sk-ant-oat01" "$JOBDIR" 2>/dev/null; then
    set_row "$P" failed "$JOB" "$ATT" "TOKEN FOUND IN JOB FOLDER: queue stopped"
    log "TOKEN" "$P: token string found in the job folder; queue stopped. Do not share the folder."
    exit 2
  fi

  TRIAL="$(ls -d "$JOBDIR"/*__*/ 2>/dev/null | head -1)"; TRIAL="${TRIAL%/}"
  CC="$TRIAL/agent/claude-code.txt"
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
    print("")' "$TRIAL/result.json" 2>/dev/null)"
  REWARD="$(cat "$TRIAL/verifier/reward.json" 2>/dev/null)"

  # A clean finish, or the agent stopped by the $10 ceiling (still scored, never retried).
  if [ -n "$REWARD" ] && [ -z "$EXC" ] && { [ "$IS_ERR" = "false" ] || [[ "$SUB" == error_max* ]]; }; then
    save_run "$P" "$TRIAL" "$JOBDIR"
    NOTE=""; [ "$SUB" != "success" ] && NOTE="subtype $SUB"
    set_row "$P" done "$JOB" "$ATT" "$NOTE"
    log "done" "$P turns $TURNS cost_usd_est $COST reward $REWARD $NOTE"
  else
    # Not a clean finish: is it the usage limit? Take the exact message from the agent's output.
    MSG="$( { printf '%s\n' "$RES" | python3 -c 'import json,sys
try: d=json.loads(sys.stdin.read()); print(d.get("result",""), d.get("api_error_status") or "")
except Exception: pass'; printf '%s\n' "$EXC"; tail -n 30 "$CC" 2>/dev/null; tail -n 30 "$HERE/runs/.harbor-$P.out"; } \
      | grep -iE "$LIMIT_RE" | head -1 | cut -c1-300)"
    if [ -n "$MSG" ]; then
      [ -d "$JOBDIR" ] && mv "$JOBDIR" "$JOBDIR.limited-$(date +%Y%m%dT%H%M%S)"
      set_row "$P" limited "$JOB" "$((ATT - 1))" "$MSG"     # a limit does not use up an attempt
      log "limited" "$P turns $TURNS cost_usd_est $COST message: $MSG"
      cleanup_docker
      wait_for_reset "$MSG" || { log "stop" "STOP file found while waiting"; break; }
      continue
    fi
    TXT="$(printf '%s' "$RES" | python3 -c 'import json,sys
try: print(str(json.loads(sys.stdin.read()).get("result",""))[:150])
except Exception: pass')"
    WHY="rc $RC, is_error $IS_ERR, subtype $SUB, turns $TURNS, reward ${REWARD:-none}, exception ${EXC:-none}, result: ${TXT:-none}"
    if [ "$ATT" -ge "$MAX_ATTEMPTS" ]; then
      [ -d "$TRIAL" ] && save_run "$P" "$TRIAL" "$JOBDIR"
      set_row "$P" failed "$JOB" "$ATT" "$WHY"
      log "failed" "$P after $ATT attempts: $WHY"
    else
      set_row "$P" pending "$JOB" "$ATT" "$WHY"
      log "retry" "$P will be retried: $WHY"
    fi
  fi
  cleanup_docker
  [ $ONE -eq 1 ] && { log "end" "--one: stopping after one run"; break; }
  sleep "$GAP"
done
