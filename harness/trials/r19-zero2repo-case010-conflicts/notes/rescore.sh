#!/bin/bash
# Score a saved build on a task with no model call: Harbor's oracle agent unpacks the build into /app,
# then the task's own verifier runs the hidden tests (the method of ../r17-…/notes/footprint.sh).
#   bash notes/rescore.sh <task folder under work/tasks> <label> <app.tgz> [<label> <app.tgz> ...]
# Writes work/jobs/rescore-<label>; prints the reward line. Nobody reads the tests; only the judge's report.
ARGS=(); for a in "$@"; do if [ -f "$a" ]; then ARGS+=("$(readlink -f "$a")"); else ARGS+=("$a"); fi; done; set -- "${ARGS[@]}"
cd "$(dirname "$0")/../work" || exit 1
H=../../../platforms/harbor/download/.venv/bin/harbor
base="tasks/$1"; shift
while [ $# -ge 2 ]; do
  label="$1"; tgz="$2"; shift 2
  t="tasks/oracle-$label"; rm -rf "$t"; cp -r "$base" "$t"
  cp "$tgz" "$t/solution/app.tgz"
  printf '#!/bin/bash\nset -e\nmkdir -p /app\ntar -xzf /solution/app.tgz -C /app\n' > "$t/solution/solve.sh"
  sed -i "s/^name = .*/name = \"sdd-compiler\/zero2repo-case010-oracle-$label\"/" "$t/task.toml"
  rm -rf "jobs/rescore-$label"
  HARBOR_TELEMETRY=0 timeout 3600 env -u ANTHROPIC_API_KEY "$H" run -p "$t" -a oracle -o jobs --job-name "rescore-$label" > "jobs/rescore-$label.out" 2>&1
  echo "$label exit $? $(find "jobs/rescore-$label" -name reward.json -path '*verifier*' | head -1 | xargs cat 2>/dev/null)"
  rm -rf "$t"
done
echo rescore-finished
