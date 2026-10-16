#!/bin/bash
# Watchdog for one trial, run by cron (every 10 min): keeps the trial going after an interruption
# (reboot, killed driver, closed Claude session). No model call of its own.
#
#   crontab line:  */10 * * * * /bin/bash <repo>/harness/trials/watchdog.sh <repo>/harness/trials/<trial>
#
# Each pass:
#   - STOP file in the trial → does nothing;
#   - runs <trial>/notes/watchdog_hook.sh if present (e.g. restarts unfinished compiles);
#   - if no driver holds <trial>/work/driver.lock:
#       a row left `running` (driver died mid-run) → set back to `pending` (the driver keeps the old job
#       folder as .attemptN); then, if any row is pending or limited, starts ../run_queue.sh detached.
# Writes <trial>/work/watchdog.status every pass and one line to <trial>/watchdog.log when it acts.
# The driver itself handles usage limits (waits for the reset) and pauses near them (usage_guard).
set -u
T="$(cd "${1:?usage: watchdog.sh <trial-dir>}" && pwd)"
KIT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/home/victor/.local/bin:/home/victor/anaconda3/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
Q="$T/queue.tsv"; L="$T/work/driver.lock"
log() { printf '%s\t%s\n' "$(date -Is)" "$*" >> "$T/watchdog.log"; }
[ -f "$T/STOP" ] && { echo "$(date -Is) STOP present; idle" > "$T/work/watchdog.status"; exit 0; }
# one pass at a time; children are started with fd 7 closed so they do not keep this lock (found
# 2026-10-14: the first version's children held it and every later pass exited at once)
exec 7> "$T/work/watchdog.pass.lock"; flock -n 7 || exit 0

[ -x "$T/notes/watchdog_hook.sh" ] && bash "$T/notes/watchdog_hook.sh" "$T" 7>&-

if flock -n "$L" true; then                                 # no driver running (lock taken and released)
  if awk -F'\t' 'NR>1 && $4=="running"' "$Q" | grep -q .; then
    for r in $(awk -F'\t' 'NR>1 && $4=="running" {print $1}' "$Q"); do
      awk -F'\t' -v OFS='\t' -v p="$r" '$1==p {$4="pending"; $7="reset by watchdog: driver gone while running"} {print}' "$Q" > "$Q.tmp" && mv "$Q.tmp" "$Q"
      log "reset $r running → pending (no driver)"
    done
  fi
  if awk -F'\t' 'NR>1 && ($4=="pending" || $4=="limited")' "$Q" | grep -q .; then
    # fd 7 closed on the whole subshell: closing it only on the driver left the launching subshell
    # holding the pass lock for the driver's lifetime, so later passes exited at once (found 2026-10-15)
    (cd "$KIT" && setsid nohup bash run_queue.sh "$T" >> "$T/run_queue.log" 2>&1 < /dev/null &) 7>&-
    log "driver started (rows waiting: $(awk -F'\t' 'NR>1 && ($4=="pending"||$4=="limited")' "$Q" | wc -l))"
  fi
  state="no driver"
else
  state="driver running"
fi
counts="$(awk -F'\t' 'NR>1 {c[$4]++} END {for (k in c) printf "%s=%d ", k, c[k]}' "$Q")"
echo "$(date -Is) $state | $counts| last log: $(tail -1 "$T/run_queue.log" 2>/dev/null | cut -c1-160)" > "$T/work/watchdog.status"
