#!/bin/bash
# Rescore a finished run from its saved workspace (runs/<run_id>/app.tgz) with the current task's
# scorer, through Harbor's oracle agent (no model):  bash notes/rescore.sh <run_id> <task-name>
set -eu
cd "$(dirname "$0")/.."
R="$1"; TASK="$2"; RT="work/tasks/rescore-$R"
rm -rf "$RT"; cp -r "work/tasks/$TASK" "$RT"
mkdir -p "$RT/solution"; cp "runs/$R/app.tgz" "$RT/solution/app.tgz"
printf '#!/bin/bash\n# Restore the saved workspace of run %s (rescore, not a reference).\ntar -xzf /solution/app.tgz -C /app\n' "$R" > "$RT/solution/solve.sh"
sed -i "s/^name = .*/name = \"sdd-compiler\/rescore-$R\"/" "$RT/task.toml"
cd work && HARBOR_TELEMETRY=0 timeout 1800 env -u ANTHROPIC_API_KEY ../../../platforms/harbor/download/.venv/bin/harbor \
  run -p "tasks/rescore-$R" -a oracle -o jobs --job-name "rescore-$R" > "jobs/rescore-$R.out" 2>&1
V="$(ls -d jobs/rescore-$R/*__*/verifier)"
mkdir -p "../runs/$R/rescore"; cp "$V"/*.json "$V"/*.xml "$V"/*.out "$V"/*.log "../runs/$R/rescore/" 2>/dev/null || true
echo "$R rescored: $(cat "$V/reward.json")"
