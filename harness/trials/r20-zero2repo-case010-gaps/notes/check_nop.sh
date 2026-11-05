#!/bin/bash
# Round 20: copied from round 19, unchanged.
# Do-nothing check of every built task (Harbor's nop agent, no model). Writes work/jobs/check-nop-<task>.
cd "$(dirname "$0")/../work"
H=../../../platforms/harbor/download/.venv/bin/harbor
for t in "$@"; do
  HARBOR_TELEMETRY=0 timeout 2400 env -u ANTHROPIC_API_KEY "$H" run -p "tasks/$t" -a nop -o jobs --job-name "check-nop-$t" > "jobs/check-nop-$t.out" 2>&1
  echo "$t exit $? $(find "jobs/check-nop-$t" -name reward.json -path '*verifier*' | head -1 | xargs cat 2>/dev/null)"
done
echo checks-finished
