#!/bin/bash
# Round 13c hook for ../../watchdog.sh: (re)start each case's compile until it is DONE.
# A compile that stopped on repeated failures leaves FAILED and is not restarted (needs a person).
T="$1"
for c in case010 case006 case016; do
  D="$T/work/compile-$c"
  [ -f "$D/DONE" ] || [ -f "$D/FAILED" ] && continue
  mkdir -p "$D"
  flock -n "$D/compile.lock" true 2>/dev/null || continue      # already running
  (setsid nohup bash "$T/notes/compile_case.sh" "$c" > /dev/null 2>&1 < /dev/null &)
  printf '%s\t%s\n' "$(date -Is)" "compile $c started" >> "$T/watchdog.log"
done
