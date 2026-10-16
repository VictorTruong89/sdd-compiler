#!/bin/bash
# Make a new trial folder from the template:  bash new_trial.sh <trial-id> "<one-line question>"
# The id names the round and what it tries, e.g. r13-zero2repo-case004.
set -eu
KIT="$(cd "$(dirname "$0")" && pwd)"
ID="${1:?usage: new_trial.sh <trial-id> \"<question>\"}"; Q="${2:-TODO}"
T="$KIT/$ID"
[ -e "$T" ] && { echo "exists: $T" >&2; exit 1; }
mkdir -p "$T"/{runs,notes,work/tasks,work/jobs}
printf 'run_id\ttask\tmodel\tstatus\tjob\tattempts\tlast_message\n' > "$T/queue.tsv"
cat > "$T/trial.env" <<'EOF'
# Conditions for run_queue.sh (sourced). Change only before the first run; record changes in TRIAL.md.
CLAUDE_VERSION=2.1.296
BUDGET_USD=10
RUN_TIMEOUT=9000
EOF
sed -e "s/{{ID}}/$ID/g" -e "s/{{DATE}}/$(date +%F)/g" -e "s|{{QUESTION}}|$Q|g" "$KIT/TRIAL_TEMPLATE.md" > "$T/TRIAL.md"
echo "made $T"
