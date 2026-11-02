#!/bin/bash
# Footprint of each planted item, with no model call: Zero2Repo's hidden tests run (through Harbor's
# oracle agent) on the base build and on each side-B copy (notes/sides.py); copied from round 14. The tests whose result
# differs from the base are that item's footprint. Nobody reads the tests; only the judge's report.
#   bash notes/footprint.sh BASE P1 P2 ...        (from the trial folder)
cd "$(dirname "$0")/../work" || exit 1
H=../../../platforms/harbor/download/.venv/bin/harbor
for v in "$@"; do
  t="tasks/oracle-$v"; rm -rf "$t"; cp -r tasks/case006-markdown-original "$t"
  cp "sides/$v.tgz" "$t/solution/app.tgz"
  printf '#!/bin/bash\nset -e\nmkdir -p /app\ntar -xzf /solution/app.tgz -C /app\n' > "$t/solution/solve.sh"
  sed -i "s/^name = .*/name = \"sdd-compiler\/zero2repo-case006-oracle-$v\"/" "$t/task.toml"
  rm -rf "jobs/footprint-$v"
  HARBOR_TELEMETRY=0 timeout 3600 env -u ANTHROPIC_API_KEY "$H" run -p "$t" -a oracle -o jobs --job-name "footprint-$v" > "jobs/footprint-$v.out" 2>&1
  echo "$v exit $? $(find "jobs/footprint-$v" -name reward.json -path '*verifier*' | head -1 | xargs cat 2>/dev/null)"
done
echo footprint-finished
