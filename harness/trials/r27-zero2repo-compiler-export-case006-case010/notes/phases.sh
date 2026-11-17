#!/bin/bash
# Round 27 launcher: phase 1 = case010 rows (early-stop threshold 99); phase 2 = case006 rows (238), as round 25.
#   nohup setsid bash notes/phases.sh >> run_queue.log 2>&1 &
set -u
T="$(cd "$(dirname "$0")/.." && pwd)"; KIT="$(dirname "$T")"
bash "$KIT/run_queue.sh" "$T"
[ -f "$T/STOP" ] && exit 0
if awk -F'\t' 'NR>1 && $2 ~ /case010/ && $4 != "done" && $4 != "failed" {f=1} END {exit !f}' "$T/queue.tsv"; then
  printf '%s\tphases\tcase010 rows not all finished; phase 2 not started\n' "$(date -Is)"; exit 1; fi
sed -i 's/^EARLYSTOP_MIN_PASSED=99$/EARLYSTOP_MIN_PASSED=238/' "$T/trial.env"
echo "# Phase 2 set $(date -Is): EARLYSTOP_MIN_PASSED 99 -> 238 (case006 rows released from hold)." >> "$T/trial.env"
awk -F'\t' -v OFS='\t' 'NR>1 && $4=="hold" {$4="pending"} {print}' "$T/queue.tsv" > "$T/queue.tsv.tmp" && mv "$T/queue.tsv.tmp" "$T/queue.tsv"
printf '%s\tphases\tphase 2 started\n' "$(date -Is)"
bash "$KIT/run_queue.sh" "$T"
printf '%s\tphases\tall phases finished\n' "$(date -Is)"
touch "$T/work/ALL_DONE"
